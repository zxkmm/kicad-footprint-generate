"""Render a board -- or any region of it -- to a PNG an agent can read.

How it works: kicad-cli exports SVG whose viewBox is the page in millimetres,
so board coordinates map 1:1 onto SVG user units. Zooming is therefore just
rewriting the viewBox, which is exact -- no pixel math, no guessing.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from typing import Optional, Sequence

from .geom import Box, BoardView

# Layer presets. KiCad accepts both old and new names; these are the 10.x forms
# that also work on 9.x.
PRESETS = {
    "front": "F.Cu,F.SilkS,F.Mask,Edge.Cuts",
    "front-clean": "F.Cu,F.SilkS,Edge.Cuts",
    "back": "B.Cu,B.SilkS,B.Mask,Edge.Cuts",
    "copper": "F.Cu,B.Cu,Edge.Cuts",
    "both": "F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts",
    "outline": "Edge.Cuts",
    "assembly": "F.Fab,F.SilkS,Edge.Cuts",
    "courtyard": "F.CrtYd,F.Cu,Edge.Cuts",
}

_VIEWBOX = re.compile(r'viewBox="([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)"')
_SIZE = re.compile(r'width="[-\d.]+mm"\s+height="[-\d.]+mm"')


def _require(tool: str):
    if shutil.which(tool) is None:
        raise RuntimeError(f"required tool not found on PATH: {tool}")


def _export_svg(pcb: str, dest: str, layers: str, whole_page: bool, theme: Optional[str]):
    _require("kicad-cli")
    cmd = [
        "kicad-cli", "pcb", "export", "svg",
        "--output", dest,
        "--layers", layers,
        "--mode-single",
        "--page-size-mode", "0" if whole_page else "2",
    ]
    if not whole_page:
        cmd.append("--exclude-drawing-sheet")
    if theme:
        cmd += ["--theme", theme]
    cmd.append(pcb)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dest):
        raise RuntimeError(f"kicad-cli svg export failed:\n{r.stdout}\n{r.stderr}")


def _set_viewbox(svg_path: str, box: Box):
    """Zoom the SVG to `box` (millimetres, page coordinates)."""
    with open(svg_path) as fh:
        svg = fh.read()
    if not _VIEWBOX.search(svg):
        raise RuntimeError("exported SVG has no viewBox; cannot zoom")
    svg = _VIEWBOX.sub(
        f'viewBox="{box.x:.4f} {box.y:.4f} {box.w:.4f} {box.h:.4f}"', svg, count=1
    )
    svg = _SIZE.sub(f'width="{box.w:.4f}mm" height="{box.h:.4f}mm"', svg, count=1)
    with open(svg_path, "w") as fh:
        fh.write(svg)


def _rasterize(svg: str, png: str, width_px: int, background: str):
    _require("rsvg-convert")
    r = subprocess.run(
        ["rsvg-convert", "-w", str(width_px), "-b", background, svg, "-o", png],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not os.path.exists(png):
        raise RuntimeError(f"rsvg-convert failed:\n{r.stderr}")


def render_schematic(
    sch: str,
    out_png: str,
    width_px: int = 1600,
    background: str = "white",
    theme: Optional[str] = None,
    drawing_sheet: bool = False,
    sheet: Optional[str] = None,
    all_sheets: bool = False,
    region: Optional[Box] = None,
) -> dict:
    """Render a schematic sheet to PNG.

    A schematic authored as text is exactly as capable of being silently wrong
    as a placement script -- symbols on top of each other, a label parked over
    a part, two chains overlapping. ERC does not see any of that, because none
    of it is an electrical error. Only the picture catches it.

    A hierarchical design is one SVG per sheet, and the root sheet of such a
    design is usually just a box per child -- the parts live on the children.
    Pick one with `sheet=`, or get the lot with `all_sheets=True`; rendering
    only the root is almost never what you wanted.

    Schematic SVGs carry a millimetre viewBox exactly like the board ones, so
    `region` (x, y, w, h in sheet mm, y down) zooms without any pixel math.
    """
    _require("kicad-cli")
    out_png = os.path.abspath(out_png)
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["kicad-cli", "sch", "export", "svg", "--output", tmp,
               "--no-background-color"]
        if not drawing_sheet:
            cmd.append("--exclude-drawing-sheet")
        if theme:
            cmd += ["--theme", theme]
        cmd.append(sch)
        r = subprocess.run(cmd, capture_output=True, text=True)
        svgs = sorted(f for f in os.listdir(tmp) if f.endswith(".svg"))
        if r.returncode != 0 or not svgs:
            raise RuntimeError(f"kicad-cli sch svg export failed:\n{r.stdout}\n{r.stderr}")

        # kicad-cli names the root after the file and each child "<root>-<Sheetname>".
        root_svg = os.path.splitext(os.path.basename(sch))[0] + ".svg"
        stem = os.path.splitext(root_svg)[0]
        names = {}                      # friendly sheet name -> svg filename
        for f in svgs:
            base = os.path.splitext(f)[0]
            names[base[len(stem) + 1:] if base.startswith(stem + "-") else "root"] = f

        if all_sheets:
            picks = [(n, names[n]) for n in sorted(names)]
        elif sheet:
            hits = [n for n in names if n.lower() == sheet.lower()] or \
                   [n for n in names if sheet.lower() in n.lower()]
            if len(hits) != 1:
                raise RuntimeError(
                    "--sheet %r matched %d of %s"
                    % (sheet, len(hits), sorted(names))
                )
            picks = [(hits[0], names[hits[0]])]
        else:
            picks = [("root", root_svg if root_svg in svgs else svgs[0])]

        out_stem, ext = os.path.splitext(out_png)
        written = {}
        for name, svg in picks:
            png = out_png if len(picks) == 1 else f"{out_stem}-{name}{ext}"
            src = os.path.join(tmp, svg)
            if region is not None:
                _set_viewbox(src, region)
            _rasterize(src, png, width_px, background)
            written[name] = png

    info = {
        "png": list(written.values())[0] if len(written) == 1 else sorted(written.values()),
        "rendered": written,
        "source": os.path.abspath(sch),
        "width_px": width_px,
        "sheets_available": sorted(names),
    }
    if region is not None:
        info["region_mm"] = region.as_dict()
        info["mm_per_px"] = round(region.w / width_px, 5)
    return info


def render(
    pcb: str,
    out_png: str,
    layers: str = "front",
    refs: Optional[Sequence[str]] = None,
    region: Optional[Box] = None,
    margin_mm: float = 2.0,
    width_px: int = 1200,
    background: str = "white",
    theme: Optional[str] = None,
    square: bool = True,
) -> dict:
    """Render the board to `out_png`.

    Region is chosen by, in order of precedence: explicit `region`, the bounding
    box of `refs`, else the whole board. Returns what was actually drawn so the
    caller knows the scale it is looking at.
    """
    layer_str = PRESETS.get(layers, layers)
    out_png = os.path.abspath(out_png)
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    if region is None and refs:
        region = BoardView(pcb).box_of(refs, margin_mm)
    if region is not None and square:
        region = region.squared()

    with tempfile.TemporaryDirectory() as tmp:
        svg = os.path.join(tmp, "plot.svg")
        # Whole-page export keeps the 1:1 mm mapping we need in order to zoom.
        # With no region we let kicad-cli crop to the board itself instead.
        _export_svg(pcb, svg, layer_str, whole_page=region is not None, theme=theme)
        if region is not None:
            _set_viewbox(svg, region)
        _rasterize(svg, out_png, width_px, background)

    info = {
        "png": out_png,
        "layers": layer_str,
        "width_px": width_px,
        "region_mm": region.as_dict() if region else "whole board",
    }
    if region is not None:
        info["mm_per_px"] = round(region.w / width_px, 5)
    return info
