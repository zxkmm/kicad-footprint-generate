# Environment & Deployment

## 📂 KiCad Scripting Paths

To make the generated footprint available in KiCad's Footprint Wizard, the script must be placed in one of the following directories.

### Linux (Default Priority)
1. `~/.local/share/kicad/10.0/scripting/plugins/` (Recommended)
2. `~/.config/kicad/10.0/scripting/plugins/`
3. `/usr/share/kicad/scripting/plugins/` (Requires sudo)

*Note: Replace `10.0` with the actual installed KiCad version (e.g., `8.0`, `7.0`).*
Use `kicad-cli --version`  to check KiCad version, If not avaliable, just guess based on filesystem.

### Detection Strategy
Before writing the file, use `ls -d` or `find` to detect the existence of these paths.
```bash
ls -d ~/.local/share/kicad/*/scripting/plugins/
```

## 📤 Deliverables

Ship **both**:

1. **The wizard script**, copied into the detected plugins directory. Name the
   file with underscores (`mc_314c_4p16_wizard.py`) so it is importable for
   verification; hyphens are fine in `GetName()` / `GetValue()`.
2. **A generated `.kicad_mod`**, written into a `.pretty` library beside the
   datasheet. Most users want the footprint, not the generator — do not make
   them run the wizard to get it. See
   [Verification step E](VERIFICATION.md#e-export-a-kicad_mod).

```text
MyPart/
├── datasheet.pdf
├── my_part_wizard.py           # also copied to ~/.local/share/kicad/<ver>/scripting/plugins/
└── MyPart.pretty/
    └── My_Part_Footprint.kicad_mod
```

Delete any `__pycache__/` left behind by verification before handing over.

## 🚀 Deployment Instructions for User

To add the `.kicad_mod` directly: **Preferences → Manage Footprint Libraries →
add the `.pretty` folder**.

To use the wizard instead:
1. Open KiCad.
2. Launch the **Footprint Editor**.
3. Go to **File > Create Footprint...** (or click the Footprint Wizard icon).
4. Select your script from the list (e.g., `P8X32A-M44_QFN`).
5. Click **Export to Footprint Editor**.
6. If the script doesn't appear, click the **Refresh** button in the wizard selection dialog.
