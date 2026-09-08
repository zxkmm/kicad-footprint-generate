---
name: kicad-footprint-generate
description: >
  Generates production-ready KiCad footprint scripts (.py) from component datasheets (images, PDFs, or text). 
  Specializes in precise coordinate math and official KiCad API compliance.
---

# KiCad Footprint Generator

## 🔁 Improve this skill as you use it

**This skill is a git repo, and you are expected to edit it.** When a package
type needs a rule that is not written down, when a template is wrong, when a
generated footprint fails verification for a reason the docs did not predict —
**fix the repo, then commit and push, in this same session.**

```bash
git -C <this repo> add <the files you changed>
git -C <this repo> commit -m "QFN: EPAD paste must be split into a stencil array"
git -C <this repo> push
```

Pad math that you had to derive, a datasheet convention that tripped you up, a
new package family — those belong in `docs/` or as a new file in `templates/`,
not only in the script you hand back. You have standing permission from the repo
owner to commit and push these fixes without asking; on a fork, commit to a
branch and say a PR is ready. Full rules: `../../docs/SELF_ITERATION.md`.

## 🎯 Primary Goal
Transform component physical specifications into a fully functional, hardcoded KiCad Footprint Wizard script. The output must be a ready-to-run Python script that automates the generation of a `.kicad_mod` file within the KiCad environment.

## 🛠 Strategic Workflow

### 1. Specification Research
Extract precise dimensions from provided inputs (images, PDFs, or descriptions). Focus on:
- Pin/Pad geometry (pitch, width, length).
- Package body dimensions and Pin 1 orientation.
- Thermal pad (EPad) requirements and courtyard clearances.

**Measure the drawing; do not eyeball it.** Render the datasheet at 600 dpi,
scan for stroke centres, and derive mm-per-pixel from a printed dimension —
then cross-validate that scale against every other printed dimension. Prefer
the "RECOMMENDED P.C.B. LAYOUT" page over mechanical views.
*Refer to [Measurement](docs/MEASUREMENT.md) and [Analysis Guide](docs/GUIDE.md#1-specification-analysis).*

### 2. Template Selection & Mapping
Identify the package type (SOP, QFP, BGA, QFN, etc.) and map it to the corresponding template in `templates/`.
Irregular land patterns (connectors, USB-C, card edges) fit no template — write an explicit pad table instead.
*Refer to [Templates Reference](docs/API_REFERENCE.md#template-directory-templates) and [Irregular Land Patterns](docs/GUIDE.md#5-irregular-land-patterns-connectors).*

### 3. Implementation (Hardcoded Logic)
Generate a standalone Python script where all dimensions are hardcoded. 
- **Rule**: The user should not have to configure parameters; the script should generate the specific footprint immediately upon execution.
- **API Compliance**: Strictly follow the conventions in `docs/API_REFERENCE.md`.

### 4. Local Verification
Before delivering the script, perform the mandatory verification steps:
1. **Syntax Check**: `python3 <script>.py`
2. **Lifecycle Test**: Run `BuildFootprint()` via CLI.
3. **Geometry Dump**: print every pad in mm and check it against the datasheet.
4. **Overlay**: draw the generated pads back onto the datasheet image using the
   pixel mapping from step 1, then look at the result. Steps 1-2 only prove the
   script runs; this is what proves it is right.
*Refer to the full [Verification Workflow](docs/VERIFICATION.md).*

### 5. Deployment & Delivery
- Deploy the script to the detected KiCad scripting directory.
- Also export a ready-to-use `.kicad_mod` into a `.pretty` library beside the datasheet, so the user is not forced to run the wizard.
- Provide clear run instructions to the user.
- State the orientation and origin, list any dimension you **inferred** rather than read, and flag anything the fab should check.
*Refer to [Environment & Deployment](docs/ENVIRONMENT.md).*

## 🔗 Putting the footprint on a board

Once the `.kicad_mod` exists, the `kicad-harness` skill in this same repo
(`../kicad-harness/SKILL.md`) takes over: `kh validate --footprints <lib:name>`
confirms KiCad resolves the id, and `kh view --refs <ref>` renders the part in
place so you can actually look at it next to its neighbours.

## 📚 Supporting Documentation
- [Measurement](docs/MEASUREMENT.md) - Getting exact dimensions out of a drawing.
- [Detailed Guide](docs/GUIDE.md) - Deep dive into the generation process.
- [API & Templates](docs/API_REFERENCE.md) - KiCad Python API and blueprint mapping.
- [Environment Setup](docs/ENVIRONMENT.md) - Path detection and installation.
- [Verification](docs/VERIFICATION.md) - Mandatory testing procedures.
- [Examples](docs/EXAMPLES.md) - Reference implementations.
