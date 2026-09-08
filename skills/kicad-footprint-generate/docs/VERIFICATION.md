# Verification Workflow

To prevent runtime errors (API mismatches, unit scaling, lifecycle issues), **ALWAYS** perform this local verification before reporting completion to the user.

Steps A and B prove the script *runs*. Steps C and D prove the footprint is
*correct* — they are what actually catches a mistyped coordinate, and they are
cheap. Do not stop at B.

## 1. Setup Local Environment

Point `PYTHONPATH` to the `templates` directory to resolve imports like `FootprintWizardBase` and `PadArray`.

```bash
export TEMPLATE_DIR="$(pwd)/templates"
export PYTHONPATH="$TEMPLATE_DIR:$PYTHONPATH"
```

If a real KiCad is installed, `import pcbnew` will load the system module and
may emit `assert "m_choices.GetCount() > 0" failed` lines on stderr. These are
harmless KiCad property-system warnings; filter them so they do not bury real
output:

```bash
python3 script.py 2>&1 | grep -v "property.h\|assert"
```

## 2. Validation Suite

### A. Syntax & Import Check
Catches basic typos, indentation errors, and missing dependencies.
```bash
python3 <your_generated_script>.py
```

### B. Lifecycle & Build Check
Tests the actual `BuildThisFootprint` logic. Call `BuildFootprint()` (the base class wrapper) to ensure the drawing context and lifecycle state are initialized correctly.

```bash
python3 -c 'import <script_module>; wizard = <script_module>.<ClassName>(); wizard.BuildFootprint(); print("Verification Success")'
```

Note the module must be importable, so name the file with underscores
(`mc_314c_4p16_wizard.py`), not the raw part number (`MC-314C-4P16.py`).

### C. Geometry Dump

Build the footprint and print every pad in millimetres, then read the table
against the datasheet. This is where a transposed sign or a wrong pitch shows
up immediately.

```python
import pcbnew, my_wizard
w = my_wizard.MyWizard(); w.BuildFootprint()
M = pcbnew.ToMM
for p in sorted(w.module.Pads(), key=lambda p: (p.GetPosition().y, p.GetPosition().x)):
    pos, sz, d = p.GetPosition(), p.GetSize(), p.GetDrillSize()
    print('%-5s x=%7.3f y=%7.3f  %5.2f x %5.2f  drill %4.2f x %4.2f' % (
        p.GetNumber(), M(pos.x), M(pos.y), M(sz.x), M(sz.y), M(d.x), M(d.y)))
```

Check: pad count, numbering order, pitch, symmetry about the intended origin,
and that the courtyard encloses every pad.

### D. Overlay Back Onto the Datasheet  ← strongest check

If the dimensions came from a rendered drawing (see
[Measurement](MEASUREMENT.md)), you already know the pixel-to-millimetre
mapping. Reuse it to draw the *generated* pads on top of the *datasheet* image.
Any error in extraction, in the arithmetic, or in the wizard shows up instantly
as copper that does not sit on the printed land pattern.

```python
from PIL import Image, ImageDraw
import pcbnew, my_wizard

w = my_wizard.MyWizard(); w.BuildFootprint()
im = Image.open('layout.png').convert('RGB'); d = ImageDraw.Draw(im)

S = 6.40 / 558.0          # mm per pixel, from the measurement step
X0, Y0 = 1097.5, 947.75   # pixel coords of the footprint origin
P = lambda xm, ym: (X0 + xm / S, Y0 + ym / S)

M = pcbnew.ToMM
for p in w.module.Pads():
    x, y = M(p.GetPosition().x), M(p.GetPosition().y)
    hw, hh = M(p.GetSize().x) / 2, M(p.GetSize().y) / 2
    box = [P(x - hw, y - hh), P(x + hw, y + hh)]
    if p.GetShape() == pcbnew.PAD_SHAPE_OVAL:
        d.rounded_rectangle(box, radius=(box[1][0] - box[0][0]) / 2,
                            outline=(255, 0, 0), width=4)
        dw, dh = M(p.GetDrillSize().x) / 2, M(p.GetDrillSize().y) / 2
        hole = [P(x - dw, y - dh), P(x + dw, y + dh)]
        d.rounded_rectangle(hole, radius=(hole[1][0] - hole[0][0]) / 2,
                            outline=(0, 160, 0), width=4)
    else:
        d.rectangle(box, outline=(255, 0, 0), width=4)
im.save('overlay.png')
```

Then **read `overlay.png` back** and confirm every outline lands on its printed
counterpart. Also overlay the courtyard so you can see it encloses the part.

### E. Export a `.kicad_mod`

Deliver the finished footprint alongside the wizard so the user can use it
without running anything. Note that the module-level `pcbnew.FootprintSave()`
helper is broken in KiCad 10 (its internal plugin lookup returns `None`); go
through `PCB_IO_MGR` instead:

```python
import os, pcbnew
lib = os.path.abspath('MyPart.pretty')
os.makedirs(lib, exist_ok=True)
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
io.FootprintSave(lib, w.module)      # writes <GetValue()>.kicad_mod
```

Read the resulting file. It is plain s-expression text: confirm `(attr ...)`,
pad layers, `(drill oval w h)` on slots, and that nothing landed at `0 0` by
accident.

## 3. Common Pitfalls
- **Over-scaling**: Avoid double-scaling units. If a value comes from a parameter defined as `self.uMM`, it is already in Internal Units.
- **Float vs. Int**: KiCad API constructors (like `VECTOR2I`) strictly require integers. Use `int()` around math expressions.
- **Method Names**: See [API Reference](API_REFERENCE.md#method-names-verified-on-kicad-100) — verify against the installed `pcbnew` with `hasattr()` rather than trusting any doc, including this one.
- **Stale `__pycache__`**: the verification steps leave a `__pycache__/` next to the generated script. Delete it before handing the directory over.
