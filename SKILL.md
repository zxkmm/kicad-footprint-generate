---
name: kicad-footprint-generator
description: >
  Generates production-ready KiCad footprint scripts (.py) from component datasheets (images, PDFs, or text). 
  Specializes in precise coordinate math and official KiCad API compliance.
---

# KiCad Footprint Generator

## 🎯 Primary Goal
Transform component physical specifications into a fully functional, hardcoded KiCad Footprint Wizard script. The output must be a ready-to-run Python script that automates the generation of a `.kicad_mod` file within the KiCad environment.

## 🛠 Strategic Workflow

### 1. Specification Research
Extract precise dimensions from provided inputs (images, PDFs, or descriptions). Focus on:
- Pin/Pad geometry (pitch, width, length).
- Package body dimensions and Pin 1 orientation.
- Thermal pad (EPad) requirements and courtyard clearances.
*Refer to [Analysis Guide](docs/GUIDE.md#1-specification-analysis).*

### 2. Template Selection & Mapping
Identify the package type (SOP, QFP, BGA, QFN, etc.) and map it to the corresponding template in `templates/`. 
*Refer to [Templates Reference](docs/API_REFERENCE.md#template-directory-templates).*

### 3. Implementation (Hardcoded Logic)
Generate a standalone Python script where all dimensions are hardcoded. 
- **Rule**: The user should not have to configure parameters; the script should generate the specific footprint immediately upon execution.
- **API Compliance**: Strictly follow the conventions in `docs/API_REFERENCE.md`.

### 4. Local Verification
Before delivering the script, perform the mandatory verification steps:
1. **Syntax Check**: `python3 <script>.py`
2. **Lifecycle Test**: Run `BuildFootprint()` via CLI.
*Refer to the full [Verification Workflow](docs/VERIFICATION.md).*

### 5. Deployment & Delivery
- Deploy the script to the detected KiCad scripting directory.
- Provide clear run instructions to the user.
*Refer to [Environment & Deployment](docs/ENVIRONMENT.md).*

## 📚 Supporting Documentation
- [Detailed Guide](docs/GUIDE.md) - Deep dive into the generation process.
- [API & Templates](docs/API_REFERENCE.md) - KiCad Python API and blueprint mapping.
- [Environment Setup](docs/ENVIRONMENT.md) - Path detection and installation.
- [Verification](docs/VERIFICATION.md) - Mandatory testing procedures.
- [Examples](docs/EXAMPLES.md) - Reference implementations.
