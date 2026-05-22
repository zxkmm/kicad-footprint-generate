# Environment & Deployment

## 📂 KiCad Scripting Paths

To make the generated footprint available in KiCad's Footprint Wizard, the script must be placed in one of the following directories.

### Linux (Default Priority)
1. `~/.local/share/kicad/8.0/scripting/plugins/` (Recommended)
2. `~/.config/kicad/8.0/scripting/plugins/`
3. `/usr/share/kicad/scripting/plugins/` (Requires sudo)

*Note: Replace `8.0` with the actual installed KiCad version (e.g., `7.0`, `6.0`).*

### Detection Strategy
Before writing the file, use `ls -d` or `find` to detect the existence of these paths.
```bash
ls -d ~/.local/share/kicad/*/scripting/plugins/
```

## 🚀 Deployment Instructions for User
1. Open KiCad.
2. Launch the **Footprint Editor**.
3. Go to **File > Create Footprint...** (or click the Footprint Wizard icon).
4. Select your script from the list (e.g., `P8X32A-M44_QFN`).
5. Click **Export to Footprint Editor**.
6. If the script doesn't appear, click the **Refresh** button in the wizard selection dialog.
