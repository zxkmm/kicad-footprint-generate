# Measuring a Datasheet Drawing

Reading dimensions off a drawing "by eye" is the single largest source of wrong
footprints. A land pattern is only useful at ±0.05 mm; visual estimation from a
rendered page is good to about ±0.1 mm at best, and it silently rounds 0.65 to
0.60. **Measure the drawing in pixels and convert with a scale derived from a
printed dimension.**

This costs about three tool calls and turns "probably 0.5 mm pitch" into
"0.500 mm, confirmed against two independent printed dimensions".

## 1. Find the right drawing

Datasheets usually contain two families of views:

| View | Use it for |
| :--- | :--- |
| **RECOMMENDED P.C.B. LAYOUT** / "CIRCUIT BOARD SIZE" / land pattern | **The footprint.** This is authoritative. |
| Mechanical / product outline views | Body size, height, 3D model, sanity checks only. |

Prefer the land pattern **always**. Mechanical views frequently dimension from a
different datum (a shell edge, a contact tail tip, a moulding step), so their
numbers will not add up against the land pattern's. That is not an error in
either drawing — they are measuring different features. Do not try to force
them to agree; note the discrepancy and follow the land pattern.

## 2. Render the page at high resolution

`pdftotext -layout` first, to get the pin table, part number and any dimensions
that live in real text. The drawing itself is vector art, so it must be
rasterised:

```bash
pdftotext -layout datasheet.pdf -            # tables, pin names, notes
pdftoppm -r 600 -png -f 2 -l 2 datasheet.pdf hi   # page 2 at 600 dpi
magick hi-2.png -crop WxH+X+Y +repage layout.png  # isolate the land pattern
```

600 dpi gives ~0.0115 mm per pixel — about 4x finer than the tolerance you care
about. Read the crop back with the Read tool to orient yourself, then measure
numerically.

## 3. Scan for stroke centres, do not eyeball

CAD drawings are strokes with real width. Locate the *centre* of each stroke:
that is where the true geometry lies. Scan columns (or rows) and record runs of
dark pixels.

```python
from PIL import Image
im = Image.open('layout.png').convert('L'); px = im.load()

def col_runs(x, y0, y1, thr=128):
    """Vertical dark runs in column x -> [(start, end), ...]"""
    out, r = [], None
    for y in range(y0, y1):
        d = px[x, y] < thr
        if d and r is None: r = y
        if not d and r is not None: out.append((r, y - 1)); r = None
    return out

def edges(y0, y1, x0, x1, min_run=4):
    """X positions of vertical strokes spanning most of the band y0..y1."""
    hits, r = [], None
    for x in range(x0, x1):
        c = sum(1 for y in range(y0, y1) if px[x, y] < 128)
        hi = c >= (y1 - y0) * 0.85
        if hi and r is None: r = x
        if not hi and r is not None:
            if x - r >= min_run: hits.append((r + x - 1) / 2)   # stroke centre
            r = None
    return hits
```

Run width discriminates feature types: thick runs (5-6 px at 600 dpi) are pad
outlines, thin runs (2-3 px) are dimension extension lines and centrelines.
Pairing consecutive thick edges gives each pad's two sides; their midpoint is
the pad centre and their spacing is the pad width.

## 4. Derive the scale, then cross-validate it

Take **one** printed dimension whose extension lines you have located, and get
mm-per-pixel from it. Then check *every other* printed dimension against that
scale. If they all land within ~0.5%, your mapping is correct and every
unlabelled feature you measure is now trustworthy.

```
scale = 6.40 mm / 558 px = 0.011470 mm/px

4.80 dim  -> 418 px * 0.011470 = 4.794   ✓
11.20 dim -> 977 px * 0.011470 = 11.206  ✓
4.00 dim  -> 349 px * 0.011470 = 4.003   ✓
2.10 dim  -> 183 px * 0.011470 = 2.099   ✓
```

Four independent confirmations across both axes. Now a pad width that measures
26 px is 0.298 mm, i.e. 0.30 mm, and you can say so.

## 5. Reconcile to intended values

Measurements land near, not on, the intended numbers. Snap them using the
structure of the part, not by rounding each value in isolation:

- **Symmetry.** Positions should mirror about the part centreline. If pad 3
  reads 1.45 and pad 10 reads 5.00 on a 6.40 span, one of them is misread.
- **Constant gaps.** Land patterns are laid out on a uniform copper-to-copper
  gap. In the worked example every pad — wide and narrow, uniform pitch and
  irregular — sat on exactly 0.20 mm gaps. That single fact confirmed all
  twelve widths and positions simultaneously.
- **Sums must close.** Sub-dimensions have to add up to the overall dimension.
  `0.40 + 4.00 + 2.10 = 6.50` closing exactly against the printed body depth
  is a much stronger check than any one measurement.

An unlabelled dimension that only closes to ±0.02 mm is an *inference*. Derive
it from the dimensions that are printed (e.g. `pad height = (pad top to slot
centre) − (slot centre to pad bottom)`), state the value you chose, and flag it
to the user as inferred rather than read.

## 6. Record what you could not read

Say plainly in the delivery which numbers were printed and which were derived,
and call out anything the fab should check (thin annular rings, sub-0.2 mm
gaps, board cutouts a footprint cannot express).
