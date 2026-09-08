# KiCad Footprint Generation Guide

This guide provides the detailed procedural logic for creating high-quality KiCad footprint scripts.

## 1. Specification Analysis
- **Multimodal Input**: Prioritize direct analysis of datasheet images or PDFs. Extract precise values for pitch, span, pad size, and body size.
- **Measure, do not estimate**: render the drawing and measure it in pixels against a printed dimension. Visual estimates are not accurate enough for a land pattern. **See [Measurement](MEASUREMENT.md) — this is the highest-value step in the whole workflow.**
- **Use the recommended land pattern**: when a datasheet has both a "RECOMMENDED P.C.B. LAYOUT" and mechanical views, the land pattern is authoritative for the footprint. The views may dimension from different datums and will not always reconcile.
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
- If a dimension is simply *absent* but derivable from ones that are printed, derive it, state the value, and flag it in the delivery as inferred rather than read. Do not block on it, and do not present it as if it came off the drawing.
- If a Python error occurs during verification, analyze the traceback, fix the script, and re-verify.

## 5. Irregular Land Patterns (Connectors)

Connectors are the common case that no template covers. Handle them explicitly:

- **Write a pad table, not an array.** List every position with its X, its
  width and its pad number(s). Derive the X values from the printed span and
  pitch dimensions so the table stays readable and checkable:

    ```python
    PAD_MAP = [
        (('outer', -1), True,  ['A1', 'B12'], 'GND'),    # +/- span_outer/2
        (('inner', -1), True,  ['A4', 'B9'],  'VBUS'),   # +/- span_inner/2
        ((3, -1),       False, ['A8'],        'SBU1'),   # +/- pitch * (n + 0.5)
        ...
    ]
    ```

  Carrying the signal name alongside costs nothing and makes the table
  reviewable against the datasheet's pin table.

- **Pick an origin and justify it.** The centre of the connector body is the
  usual choice. Express every coordinate as an offset from a printed dimension
  (`pad_y = -body_depth/2 - pad_height/2`) rather than as a literal, so the
  arithmetic is visible and the parameters stay meaningful.

- **State the orientation.** Say which way the mating face points and where pin
  1 sits, in the module docstring and in the delivery message. Rotation is
  trivial for the user; guessing your convention is not.

- **Mechanical anchors** are plated slots, not round holes — see the oblong
  drill recipe in [API Reference](API_REFERENCE.md#oblong-slotted-plated-hole).

- **Keep silkscreen off copper.** Break the outline around the pad row rather
  than running a line through it; leave ~0.2 mm from any pad edge.

- **Mention what the footprint cannot express**: board cutouts and edge notches
  for mid-mount / sink-board parts, and any keep-out the datasheet shows.
