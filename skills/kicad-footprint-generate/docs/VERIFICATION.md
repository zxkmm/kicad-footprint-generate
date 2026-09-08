# Verification Workflow

To prevent runtime errors (API mismatches, unit scaling, lifecycle issues), **ALWAYS** perform this local verification before reporting completion to the user.

## 1. Setup Local Environment
Point `PYTHONPATH` to the `templates` directory to resolve imports like `FootprintWizardBase` and `PadArray`.

```bash
export TEMPLATE_DIR="$(pwd)/templates"
export PYTHONPATH="$TEMPLATE_DIR:$PYTHONPATH"
```

## 2. Validation Suite

### A. Syntax & Import Check
Catches basic typos, indentation errors, and missing dependencies.
```bash
python3 <your_generated_script>.py
```

### B. Lifecycle & Build Check
Tests the actual `BuildThisFootprint` logic. Call `BuildFootprint()` (the base class wrapper) to ensure the drawing context and lifecycle state are initialized correctly.

```bash
python3 -c 'import <script_module>; wizard = <script_module>.<ClassName>(); wizard.BuildFootprint(); print("Verification Success")'
```

## 3. Common Pitfalls
- **Over-scaling**: Avoid double-scaling units. If a value comes from a parameter defined as `self.uMM`, it is already in Internal Units.
- **Float vs. Int**: KiCad API constructors (like `VECTOR2I`) strictly require integers. Use `int()` around math expressions.
- **Method Names**: Double-check `SetPos()` vs `SetPosition()`. The former is more common in modern KiCad Python bindings.
