# API & Templates Reference

## Template Directory (`templates/`)

Use these files as architectural blueprints for different package types:

| Template | Primary Use Case | Key Features to Observe |
| :--- | :--- | :--- |
| `FootprintWizardBase.py` | **The Foundation** | Base class, lifecycle management, drawing helpers (`self.draw`). |
| `qfp_wizard.py` | **Peripheral Pins** | QFP, SOP, QFN. Corner pin logic and perimeter distribution. |
| `bga_wizard.py` | **Grid Arrays** | BGA, LGA. Matrix loops and alphanumeric grid numbering (`A1, B2...`). |
| `PadArray.py` | **Array Helper** | Classes for Linear, Rectangular, and Circular pad arrays. **Crucial for coordinate math.** |
| `pcbnew.py` | **Core API** | The low-level KiCad API. Reference for layer names and object attributes. |

## 🛠 KiCad Python API Tips

### Unit Handling
- **Internal Units (IU)**: KiCad uses nanometers internally. 
- **Wizard Parameters**: Parameters added via `self.AddParam(..., self.uMM, value)` are automatically converted to IU.
- **Math & Casting**: Wrap geometric math results in `int()` before passing to `pcbnew` constructors.
    ```python
    pos = pcbnew.VECTOR2I(int(x_coord), int(y_coord))
    ```

### Common Method Substitutions (API Versioning)
- Use `SetPos()` instead of `SetPosition()`.
- Use `PTHMask()` or `SMDMask()` for standard pad mask sets.
- `self.draw.Box(x1, y1, x2, y2)` - Note that drawing methods often use absolute coordinates relative to the footprint origin (0,0).

### Layer Constants
- `pcbnew.F_Cu`, `pcbnew.F_SilkS`, `pcbnew.F_Mask`, `pcbnew.F_CrtYd`.
- Attributes: `pcbnew.FP_SMD` or `pcbnew.FP_THROUGH_HOLE`.
