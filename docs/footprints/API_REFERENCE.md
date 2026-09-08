# API & Templates Reference

## Template Directory (`templates/`)

Use these files as architectural blueprints for different package types:

| Template | Primary Use Case | Key Features to Observe |
| :--- | :--- | :--- |
| `FootprintWizardBase.py` | **The Foundation** | Base class, lifecycle management, drawing helpers (`self.draw`). |
| `qfp_wizard.py` | **Peripheral Pins** | QFP, SOP, QFN. Corner pin logic and perimeter distribution. |
| `bga_wizard.py` | **Grid Arrays** | BGA, LGA. Matrix loops and alphanumeric grid numbering (`A1, B2...`). |
| `PadArray.py` | **Array Helper** | Classes for Linear, Rectangular, and Circular pad arrays. **Crucial for coordinate math.** |
| `FPC_wizard.py`, `microMatch_connectors.py` | **Connectors** | Mixed SMD/THT parts, mechanical anchors. |
| `pcbnew.py` | **Core API** | The low-level KiCad API. Reference for layer names and object attributes. |

**No template fits an irregular land pattern.** USB-C, card edges and most
connectors have non-uniform pitch, mixed pad widths and mechanical anchors.
`PadArray` cannot express these — do not bend the geometry to fit it. Write an
explicit pad table and place pads directly. See
[Irregular land patterns](GUIDE.md#5-irregular-land-patterns-connectors).

## 🛠 KiCad Python API Tips

### Unit Handling
- **Internal Units (IU)**: KiCad uses nanometers internally. 
- **Wizard Parameters**: Parameters added via `self.AddParam(..., self.uMM, value)` are automatically converted to IU.
- **Math & Casting**: Wrap geometric math results in `int()` before passing to `pcbnew` constructors.
    ```python
    pos = pcbnew.VECTOR2I(int(x_coord), int(y_coord))
    ```

### Method Names (verified on KiCad 10.0)

Do not guess, and do not trust this table blindly across versions — probe the
installed module first:

```python
python3 -c "import pcbnew; p = pcbnew.PAD(pcbnew.FOOTPRINT(None)); \
print([n for n in ('SetPosition','SetPos','SetNumber','SetName','SetDrillShape') if hasattr(p, n)])"
```

| Task | Use | Notes |
| :--- | :--- | :--- |
| Place a pad | `pad.SetPosition(VECTOR2I(x, y))` | `SetPos()` also exists; `SetPosition()` is what `PadArray.py` itself uses. |
| Set the pad number | `pad.SetNumber("A1")` | `SetName()` is the legacy alias. Numbers are strings — `"A1"`, `"S1"` are all valid. |
| Standard layer sets | `pad.SMDMask()`, `pad.PTHMask()`, `pad.UnplatedHoleMask()`, `pad.ApertureMask()` | `PTHMask()` deliberately excludes paste. |
| Oblong drill | `pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)` | Constant is `PAD_DRILL_SHAPE_*`, not `DRILL_SHAPE_*`. |
| Save a `.kicad_mod` | `pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)` | The `pcbnew.FootprintSave()` helper is broken in KiCad 10. `PCB_IO_MGR.PluginFind` does not exist — it is `FindPlugin`. |

`self.draw.Box(x, y, w, h)` takes a **centre** plus width/height, not corners.
`self.draw.Circle(x, y, r, filled=True)` fakes a filled dot by stroking a
radius-`r/2` circle with width `r`, so the visible diameter is `2r`.

### Layer Constants
- `pcbnew.F_Cu`, `pcbnew.F_SilkS`, `pcbnew.F_Mask`, `pcbnew.F_Fab`, `pcbnew.F_CrtYd`.
- Attributes: `pcbnew.FP_SMD` or `pcbnew.FP_THROUGH_HOLE`. A part with both SMD
  pads and plated anchors should be flagged `FP_THROUGH_HOLE`.

## Recipes

### Oblong (slotted) plated hole

Connector shell anchors are almost always oval slots, dimensioned as a pad size
and a smaller slot size:

```python
pad = pcbnew.PAD(self.module)
pad.SetSize(pcbnew.VECTOR2I(int(pad_w), int(pad_h)))       # copper, e.g. 1.00 x 1.80
pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
pad.SetLayerSet(pad.PTHMask())
pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
pad.SetDrillSize(pcbnew.VECTOR2I(int(drill_w), int(drill_h)))  # slot, e.g. 0.60 x 1.40
pad.SetNumber("S1")
```

Check the resulting annular ring — `(pad − drill) / 2` — and warn the user if
it is under ~0.25 mm, which many datasheets specify and many fabs refuse.

### Coincident pads for merged contacts

USB-C and similar connectors tie contact pairs together inside the part, so one
piece of copper serves two symbol pins (A1+B12, A4+B9, ...). Emit **two pads at
the same position with the same size**, one per pin name. This is what KiCad's
own `USB_C_Receptacle_*` footprints do, and it keeps the footprint compatible
with the stock symbol (e.g. `USB_C_Receptacle_USB2.0_16P`).

```python
for number in ['A1', 'B12']:
    pad = make_smd_pad(w, h)
    pad.SetPosition(pcbnew.VECTOR2I(x, y))
    pad.SetNumber(number)
    self.module.Add(pad)
```

Give every mechanical anchor the same number (`"S1"`) so they land on one net.
Duplicate pad numbers are legal and mean "same net"; DRC is satisfied as long
as the schematic agrees.

### Matching an existing KiCad symbol

Before inventing pad numbers, check whether KiCad ships a symbol for the part
class and adopt its pin names verbatim. A footprint whose pads are named
`1..12` cannot be used with `USB_C_Receptacle_USB2.0_16P` without hand-editing
every net.
