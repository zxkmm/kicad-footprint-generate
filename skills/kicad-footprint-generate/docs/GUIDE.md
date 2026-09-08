# KiCad Footprint Generation Guide

This guide provides the detailed procedural logic for creating high-quality KiCad footprint scripts.

## 1. Specification Analysis
- **Multimodal Input**: Prioritize direct analysis of datasheet images or PDFs. Extract precise values for pitch, span, pad size, and body size.
- **Pin Mapping**: Identify Pin 1 location, pin numbering direction (usually counter-clockwise), and any special pin arrangements (e.g., missing pins, irregular grids).
- **Clearances**: Calculate appropriate courtyard (`F.CrtYd`) and solder mask (`F.Mask`) clearances if not explicitly provided, following IPC standards where possible.

## 2. Structural Implementation
- **Class Inheritance**: Every script must inherit from `FootprintWizardBase.FootprintWizard`.
- **Method Implementation**:
    - `GetName()`: Return a unique name (e.g., `PartNumber_Package`).
    - `GetDescription()`: Provide a concise summary of the part.
    - `GenerateParameterList()`: Define parameters but **hardcode** their default values to the specific component dimensions.
    - `CheckParameters()`: Perform basic validation (e.g., pitch > 0).
    - `BuildThisFootprint()`: The core logic where pads, silkscreen, and courtyard are drawn.

## 3. Best Practices
- **Hardcoding**: Unlike generic wizards, these scripts should be "one-part-specific". Hardcode the extracted datasheet values as defaults in `GenerateParameterList`.
- **Layer Management**: Ensure all standard layers are addressed:
    - `F.Cu`: Copper pads.
    - `F.SilkS`: Silkscreen outline and Pin 1 marker.
    - `F.Mask`: Solder mask (usually calculated from copper size).
    - `F.Paste`: Solder paste (for SMD).
    - `F.CrtYd`: Courtyard boundary.
- **Unit Awareness**: All calculations in the wizard should use the internal unit system. Use `self.uMM` for conversions if necessary, but remember that parameters defined with `self.uMM` are already converted to Internal Units (IU).

## 4. Error Handling
- If specifications are ambiguous, do not guess. Ask the user for clarification or specific missing dimensions (e.g., "The datasheet shows two possible body sizes, please specify which one you need").
- If a Python error occurs during verification, analyze the traceback, fix the script, and re-verify.
