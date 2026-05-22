# Examples

## Example 1: P8X32A-M44 QFN (44-pin)

**Scenario**: User provides a datasheet image for a 44-pin QFN package with a 7.5mm thermal pad.

**Generated Script Snippet**:
```python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew
import FootprintWizardBase
import PadArray as PA

class P8X32A_QFN_Wizard(FootprintWizardBase.FootprintWizard):
    """
    Hardcoded footprint generator for P8X32A-M44 (44-pin QFN).
    Based on the datasheet provided image.
    """

    def GetName(self):
        return "P8X32A-M44_QFN"

    def GetDescription(self):
        return "Footprint for Parallax P8X32A-M44 (44-pin QFN) based on datasheet"

    def GenerateParameterList(self):
        """
        Hardcode all parameters from the datasheet image.
        """
        # ---- Pads ----
        # 44 pins: 11 per side (nx=11, ny=11)
        self.AddParam("Pads", "nx", self.uInteger, 11)
        self.AddParam("Pads", "ny", self.uInteger, 11, min_value=1)
        self.AddParam("Pads", "pitch", self.uMM, 0.65, designator='e')
        self.AddParam("Pads", "width", self.uMM, 0.33, designator='X1')  # from land pattern 0.33mm
        self.AddParam("Pads", "length", self.uMM, 0.65, designator='Y1') # from land pattern 0.60-0.65mm
        self.AddParam("Pads", "offset", self.uMM, 0.0)
        self.AddParam("Pads", "oval", self.uBool, True)

        # ---- EPad (Exposed Pad) ----
        # 4x4 grid of thermal pads, each 2.65mm square, overall 7.5mm square
        self.AddParam("EPad", "epad", self.uBool, True)
        self.AddParam("EPad", "width", self.uMM, 7.5, designator="E2")
        self.AddParam("EPad", "length", self.uMM, 7.5, designator="D2")
        self.AddParam("EPad", "thermal vias", self.uBool, True)
        self.AddParam("EPad", "thermal vias drill", self.uMM, 0.3, min_value=0.1) # 0.3mm for 0.65 pitch
        self.AddParam("EPad", "x divisions", self.uInteger, 4, min_value=1) # 4x4 grid
        self.AddParam("EPad", "y divisions", self.uInteger, 4, min_value=1)
        self.AddParam("EPad", "paste margin", self.uMM, 0.1)

        # ---- Package ----
        self.AddParam("Package", "width", self.uMM, 9.0, designator='E')    # 9.00mm body
        self.AddParam("Package", "height", self.uMM, 9.0, designator='D')   # 9.00mm body
        self.AddParam("Package", "margin", self.uMM, 0.25, minValue=0.2)

    @property
    def pads(self):
        return self.parameters['Pads']

    @property
    def epad(self):
        return self.parameters['EPad']

    @property
    def package(self):
        return self.parameters['Package']

    def CheckParameters(self):
        pass

    def GetValue(self):
        return "QFN-44_EP_9x9mm_Pitch0.65mm_P8X32A-M44"

    def BuildThisFootprint(self):
        pad_pitch = self.pads["pitch"]
        pad_length = self.pads["length"]
        pad_offset = self.pads["offset"]
        pad_width = self.pads["width"]

        v_pitch = self.package["height"]
        h_pitch = self.package["width"]

        v_pads_per_row = int(self.pads["ny"])
        h_pads_per_row = int(self.pads["nx"])

        v_row_len = (v_pads_per_row - 1) * pad_pitch
        h_row_len = (h_pads_per_row - 1) * pad_pitch

        pad_shape = pcbnew.PAD_SHAPE_OVAL if self.pads["oval"] else pcbnew.PAD_SHAPE_RECT

        h_pad = PA.PadMaker(self.module).SMDPad(pad_length, pad_width,
                                                 shape=pad_shape, rot_degree=90.0)
        v_pad = PA.PadMaker(self.module).SMDPad(pad_length, pad_width, shape=pad_shape)

        h_pitch = (int)(h_pitch / 2 - pad_length + pad_offset + pad_length/2)
        v_pitch = (int)(v_pitch / 2 - pad_length + pad_offset + pad_length/2)

        # ---- Left row (Pin 1) ----
        pin1Pos = pcbnew.VECTOR2I(-h_pitch, 0)
        array = PA.PadLineArray(h_pad, v_pads_per_row, pad_pitch, True, pin1Pos)
        array.SetFirstPadInArray(1)
        array.AddPadsToModule(self.draw)

        # ---- Bottom row ----
        pin1Pos = pcbnew.VECTOR2I(0, v_pitch)
        array = PA.PadLineArray(v_pad, h_pads_per_row, pad_pitch, False, pin1Pos)
        array.SetFirstPadInArray(v_pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        # ---- Right row ----
        pin1Pos = pcbnew.VECTOR2I(h_pitch, 0)
        array = PA.PadLineArray(h_pad, v_pads_per_row, -pad_pitch, True, pin1Pos)
        array.SetFirstPadInArray(v_pads_per_row + h_pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        # ---- Top row ----
        pin1Pos = pcbnew.VECTOR2I(0, -v_pitch)
        array = PA.PadLineArray(v_pad, h_pads_per_row, -pad_pitch, False, pin1Pos)
        array.SetFirstPadInArray(2 * v_pads_per_row + h_pads_per_row + 1)
        array.AddPadsToModule(self.draw)

        lim_x = self.package["width"] / 2
        lim_y = self.package["height"] / 2

        # ---- Exposed Pad ----
        epad_width = self.epad["width"]
        epad_length = self.epad["length"]
        aper_pad_ny = self.epad["x divisions"]
        aper_pad_nx = self.epad["y divisions"]
        epad_via_drill = self.epad["thermal vias drill"]

        if self.epad['epad'] == True:
            epad_num = (self.pads['nx'] + self.pads['ny']) * 2 + 1

            aper_pad_w = epad_length / aper_pad_nx
            aper_pad_l = epad_width / aper_pad_ny
            paste_margin = self.epad['paste margin']

            if paste_margin >= aper_pad_w:
                paste_margin = aper_pad_w - 1
            if paste_margin >= aper_pad_l:
                paste_margin = aper_pad_l - 1

            # Create the EPad
            aperture_pad = PA.PadMaker(self.module).AperturePad(
                aper_pad_w - paste_margin, aper_pad_l - paste_margin,
                shape=pcbnew.PAD_SHAPE_RECT
            )
            epad = PA.PadMaker(self.module).SMDPad(
                epad_length, epad_width, shape=pcbnew.PAD_SHAPE_RECT
            )

            layers = pcbnew.LSET()
            layers.AddLayer(pcbnew.F_Mask)
            layers.AddLayer(pcbnew.F_Cu)
            epad.SetLayerSet(layers)
            epad.SetPosition(pcbnew.VECTOR2I(0, 0))
            epad.SetName(epad_num)
            self.module.Add(epad)

            # Add aperture pads (stencil openings)
            array = PA.EPADGridArray(
                aperture_pad, aper_pad_ny, aper_pad_nx, aper_pad_l, aper_pad_w,
                pcbnew.VECTOR2I(0, 0)
            )
            array.AddPadsToModule(self.draw)

            # ---- Thermal Vias ----
            if self.epad['thermal vias']:
                via_diam = min(aper_pad_w, aper_pad_l) / 2
                via_drill = min(via_diam / 2, epad_via_drill)
                via = PA.PadMaker(self.module).THRoundPad(via_diam, via_drill)
                via.SetProperty(pcbnew.PAD_PROP_HEATSINK)

                layers = pcbnew.LSET.AllCuMask()
                layers.AddLayer(pcbnew.B_Mask)
                layers.AddLayer(pcbnew.F_Mask)
                via.SetLayerSet(layers)

                # Thermal vias placed between aperture pads
                via_array = PA.EPADGridArray(
                    via, aper_pad_ny - 1, aper_pad_nx - 1, aper_pad_l, aper_pad_w,
                    pcbnew.VECTOR2I(0, 0)
                )
                via_array.SetFirstPadInArray(epad_num)
                via_array.AddPadsToModule(self.draw)

        # ---- Package Outline (F.Fab) ----
        bevel = min(pcbnew.FromMM(1.0), self.package['width'] / 2, self.package['height'] / 2)
        self.draw.SetLayer(pcbnew.F_Fab)

        w = self.package['width']
        h = self.package['height']
        self.draw.BoxWithDiagonalAtCorner(0, 0, w, h, bevel)

        # ---- Silkscreen ----
        self.draw.SetLayer(pcbnew.F_SilkS)
        offset = self.draw.GetLineThickness()
        h_clip = h_row_len / 2 + self.pads['pitch']
        v_clip = v_row_len / 2 + self.pads['pitch']
        self.draw.SetLineThickness(pcbnew.FromMM(0.12))

        if h_pads_per_row > 0:
            # Top right
            self.draw.Polyline([
                [h_clip, -h / 2 - offset],
                [w / 2 + offset, -h / 2 - offset],
                [w / 2 + offset, -v_clip]
            ])
            # Bottom right
            self.draw.Polyline([
                [h_clip, h / 2 + offset],
                [w / 2 + offset, h / 2 + offset],
                [w / 2 + offset, v_clip]
            ])
            # Bottom left
            self.draw.Polyline([
                [-h_clip, h / 2 + offset],
                [-w / 2 - offset, h / 2 + offset],
                [-w / 2 - offset, v_clip]
            ])
            # Pin-1 indicator
            self.draw.Line(-h_clip, -h / 2 - offset, -w / 2 - pad_length / 2, -h / 2 - offset)
        else:
            self.draw.Polyline([
                [-w / 2 - offset, v_clip],
                [-w / 2 - offset, h / 2 + offset],
                [w / 2 + offset, h / 2 + offset],
                [w / 2 + offset, v_clip]
            ])
            self.draw.Polyline([
                [-h / 2 - offset, -h / 2 - offset],
                [w / 2 + offset, -h / 2 - offset],
                [w / 2 + offset, -v_clip]
            ])

        self.draw.SetLineThickness(offset)

        # ---- Courtyard ----
        cmargin = self.package["margin"]
        self.draw.SetLayer(pcbnew.F_CrtYd)
        sizex = (lim_x + cmargin) * 2 + pad_length
        sizey = (lim_y + cmargin) * 2 + pad_length
        sizex = pcbnew.PutOnGridMM(sizex, 0.1)
        sizey = pcbnew.PutOnGridMM(sizey, 0.1)
        thick = self.draw.GetLineThickness()
        self.draw.SetLineThickness(pcbnew.FromMM(0.05))
        self.draw.Box(0, 0, sizex, sizey)
        self.draw.SetLineThickness(pcbnew.FromMM(thick))

        # ---- Reference and Value ----
        text_size = self.GetTextSize()
        text_offset = sizey / 2 + text_size
        self.draw.Value(0, text_offset, text_size)
        self.draw.Reference(0, -text_offset, text_size)

        # ---- Extra text on F.Fab ----
        extra_text = pcbnew.PCB_TEXT(self.module)
        extra_text.SetLayer(pcbnew.F_Fab)
        extra_text.SetPosition(pcbnew.VECTOR2I(0, 0))
        extra_text.SetTextSize(pcbnew.VECTOR2I(text_size, text_size))
        extra_text.SetText("${REFERENCE}")
        self.module.Add(extra_text)

        # ---- Set SMD attribute ----
        self.module.SetAttributes(pcbnew.FP_SMD)


# Register the wizard
P8X32A_QFN_Wizard().register()
```

**Instruction to User**:
"I have generated the `P8X32A-M44_QFN` footprint script. It has been placed in `~/.local/share/kicad/8.0/scripting/plugins/`. You can now use the KiCad Footprint Wizard to generate the footprint."

## Example 2: AD9361BBCZ BGA (144-pin)

**Scenario**: User provides a datasheet PDF for a 144-pin BGA package.

**Generated Script Snippet**:
```python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew
import FootprintWizardBase
import PadArray as PA

class AD9361PadGridArray(PA.PadGridArray):
    def NamingFunction(self, n_x, n_y):
        # Alphabet skipping I, O, Q, S, X, Z
        alphabet = "ABCDEFGHJKLMNPRTUVWY"
        return "%s%d" % (
            self.AlphaNameFromNumber(n_y + 1, alphabet=alphabet),
            n_x + 1)

class AD9361_Wizard(FootprintWizardBase.FootprintWizard):
    def GetName(self):
        return "AD9361_CSP_BGA"

    def GetDescription(self):
        return "Footprint for Analog Devices AD9361 (144-ball CSP_BGA, 10x10mm, 0.8mm pitch)"

    def GenerateParameterList(self):
        self.AddParam("Pads", "pitch", self.uMM, 0.8)
        self.AddParam("Pads", "size", self.uMM, 0.40)
        self.AddParam("Pads", "columns", self.uInteger, 12)
        self.AddParam("Pads", "rows", self.uInteger, 12)

        self.AddParam("Package", "width", self.uMM, 10.0)
        self.AddParam("Package", "length", self.uMM, 10.0)
        self.AddParam("Package", "margin", self.uMM, 0.25)

    def CheckParameters(self):
        pass

    def GetValue(self):
        return "BGA-144_12x12_10.0x10.0mm_P0.8mm_AD9361"

    def BuildThisFootprint(self):
        pads = self.parameters["Pads"]
        rows = int(pads["rows"])
        cols = int(pads["columns"])
        pad_size = int(pads["size"])      # Already in internal units
        pad_pitch = int(pads["pitch"])    # Already in internal units

        # Add the pads
        pad = PA.PadMaker(self.module).SMTRoundPad(pad_size)
        
        # PadGridArray centers itself at the provided centre (default 0,0)
        array = AD9361PadGridArray(pad, cols, rows, pad_pitch, pad_pitch, pcbnew.VECTOR2I(0, 0))
        array.AddPadsToModule(self.draw)

        # Draw box outline on F.Fab layer
        self.draw.SetLayer(pcbnew.F_Fab)
        w = int(self.parameters['Package']['width'])   # Already in internal units
        h = int(self.parameters['Package']['length'])  # Already in internal units
        bevel = pcbnew.FromMM(1.0)
        self.draw.SetLineThickness(pcbnew.FromMM(0.1))
        self.draw.BoxWithDiagonalAtCorner(0, 0, w, h, bevel)

        # Silkscreen
        self.draw.SetLayer(pcbnew.F_SilkS)
        self.draw.SetLineThickness(pcbnew.FromMM(0.12))
        offset = self.draw.GetLineThickness()
        
        sw = w // 2 + offset
        sh = h // 2 + offset
        l = pcbnew.FromMM(2.0)
        
        # Corner marks
        self.draw.Polyline([[sw-l, -sh], [sw, -sh], [sw, -sh+l]])
        self.draw.Polyline([[sw-l, sh], [sw, sh], [sw, sh-l]])
        self.draw.Polyline([[-sw+l, sh], [-sw, sh], [-sw, sh-l]])
        
        # Pin 1 marker
        self.draw.Circle(-sw - pcbnew.FromMM(0.5), -sh - pcbnew.FromMM(0.5), pcbnew.FromMM(0.2), filled=True)

        # Courtyard
        cmargin = int(self.parameters['Package']['margin'])
        self.draw.SetLayer(pcbnew.F_CrtYd)
        self.draw.SetLineThickness(pcbnew.FromMM(0.05))
        
        # Calculate courtyard size in mm for grid rounding, then back to internal units
        cw_mm = pcbnew.PutOnGridMM(pcbnew.ToMM(w + 2*cmargin), 0.1)
        ch_mm = pcbnew.PutOnGridMM(pcbnew.ToMM(h + 2*cmargin), 0.1)
        self.draw.Box(0, 0, pcbnew.FromMM(cw_mm), pcbnew.FromMM(ch_mm))

        # Reference and Value
        text_size = self.GetTextSize()
        self.draw.Value(0, h // 2 + text_size * 2, text_size)
        self.draw.Reference(0, -(h // 2 + text_size * 2), text_size)

        # SMD attribute
        self.module.SetAttributes(pcbnew.FP_SMD)

AD9361_Wizard().register()
```

**Instruction to User**:
"I have generated the `P8X32A-M44_QFN` footprint script. It has been placed in `~/.local/share/kicad/8.0/scripting/plugins/`. You can now use the KiCad Footprint Wizard to generate the footprint."