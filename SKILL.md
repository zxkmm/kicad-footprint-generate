---
name: kicad-footprint-generator
description: >
  Use this skill to generate KiCad footprints based on provided component specifications (e.g., datasheet screenshots, PDF files, or dimensional text). Trigger this when the user asks to "generate a footprint," "create a KiCad package," or provides packaging dimensions and asks for an EDA footprint script.
---

# 🎯 Goal
Act as an EDA expert to generate a ready-to-run Python script that automatically builds a KiCad footprint (`.kicad_mod`) based on the provided datasheet specifications, strictly following official KiCad API conventions.

# 📋 Instructions
When you are called to execute this task, strictly follow these steps:
1. **Analyze the Specifications**: Extract key packaging dimensions from the provided user input (datasheet image, PDF, or text). Pay special attention to pad pitch, pad width/length, package body size, pin 1 location, and courtyard clearances. Use your multimodal power if user provides images firstly, instead of use OCR tools etc. Choose the best way of you to fetch teh information.
2. **Identify Footprint Type**: Determine the appropriate packaging type (e.g., SOP, QFP, BGA) based on the extracted dimensions and characteristics, then choose the correct footprint script template from the `templates/` directory to read.
3. **Consult Demo Script**: Read the reference template to understand the exact structure, syntax, and KiCad Python API methods required for footprint generation.
4. **Generate the Script**: Write a new Python script where all extracted packaging dimensions and coordinates are **hardcoded**. The user should not need define any option to run it. When generating codes, **make sure types matches**, if you are not sure, just read the codes in `/templates/` , the entire engine's code is in there.
When generating the final script, these files must be seen as a references:
- FootprintWizardBase.py (The Foundation): This is the core base class for all generated footprints. You must analyze this file to understand the standard lifecycle of footprint generation, including how a wizard is registered, how parameters are initialized, and how the root footprint object is constructed.
- qfp_wizard.py (Peripheral Pin Template): Use this file as your primary blueprint when generating Quad Flat Packages (QFP), Small Outline Packages (SOP), or any component with pins distributed around the perimeter. Observe how dimensions like pitch, body size, and pad margins are mathematically applied.
- bga_wizard.py (Grid Array Template): Use this file as your primary blueprint for Ball Grid Arrays (BGA) or any matrix-based pin arrangements. Pay close attention to the loop structures and coordinate math used to generate rows and columns of pads.
- pad_array.py (Array Calculation Helper): This is the official helper class specifically designed for handling complex pad array calculations. You must mimic its logic for determining pad coordinates and grid numbering schemes (e.g., alphanumeric BGA grid numbering) instead of hardcoding raw coordinate math from scratch.
- pcbnew.py (KiCad API Reference): This is the official KiCad Python API. You must ensure that all method calls, object constructions, and attribute settings in your generated script strictly adhere to the conventions and structures defined in this API. Pay special attention to how layers, pad types, and footprint attributes are set.
5. **Embed Metadata**: Ensure the generated script correctly records and attaches metadata (Description, Keywords/Tags, SMD/Through-Hole attributes) so the KiCad EDA tool can correctly read and filter the footprint in its library browser.
6. **Output & Placement**: 
   - The default added output directory on Linux is usually `/home/USER_NAME/.local/share/kicad/KICAD_VERSION/scripting`, you should detect correct path (just use filesystem tool like `ls` or `dir` in specific paths, DO NOT run KiCad.) and output the generated script there. If it doesn't exist, create it, or ask user to run command. If you have permission issues or environment path issues, ask user to run command, BUT YOU SHOULD TRY TO PUT THE FILE YOURSELF FIRSTLY.
    - Provide clear instructions on how to run the generated script using KiCad's footprint wizard.
    - Guide user that if python runtime error occurs, copy the error message back and you will fix the script, then ask user to run it again.

# 🚫 Constraints
- **NEVER** use generic or placeholder values for dimensions if the data is available in the provided specification, **just hardcode the actual values into the script, one script, one footprint**.
- **MUST** ensure the script generates standard KiCad layers correctly (e.g., `F.Cu`, `F.SilkS`, `F.Mask`, `F.Paste`, `F.CrtYd`).
- **DO NOT** output explanatory filler; focus entirely on the Python script and the execution instructions.
- **FAILURE OR INTERRUPTIONS IS ALLOWED** if the provided specifications are incomplete or ambiguous. In such cases, output a clear error message indicating what information is missing, or ask the user to provide the necessary details.

# 💡 Examples
To help you better understand the expected behavior, here is an example of a correct execution:

**User Input:**
"Here are the image/PDF for my IC. [files attached]

**Expected Output:**
I have generated the script for the SOP-8 footprint. I have put it in the default KiCad scripting directory. You can run it using the KiCad footprint wizard to create the footprint in your library. Maybe click refiresh script dir button is needed in the wizard.

[Optional] I noticed a permission issue when trying to write to the default directory. Please run the following command in your terminal to make it happen:[correct step]

```bash

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

# ...

        extra_text.SetText("${REFERENCE}")
        self.module.Add(extra_text)

        # ---- Set SMD attribute ----
        self.module.SetAttributes(pcbnew.FP_SMD)


# Register the wizard
P8X32A_QFN_Wizard().register()
```

# Informations

This the the default search path for scripts on Linux:
```
/usr/share/kicad/scripting/
/usr/share/kicad/scripting/plugins
/home/USER_NAME/.config/kicad/KICAD_VERSION/scripting
/home/USER_NAME/.config/kicad/KICAD_VERSION/scripting/plugins
/home/USER_NAME/.local/share/kicad/KICAD_VERSION/scripting
/home/USER_NAME/.local/share/kicad/KICAD_VERSION/scripting/plugins
/home/USER_NAME/.local/share/kicad/KICAD_VERSION/3rdparty//plugins
```