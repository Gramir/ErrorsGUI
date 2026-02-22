---
description: Build Crash Detective into a standalone .exe
---

# Build Crash Detective

## Prerequisites

Ensure you have the virtual environment activated and dependencies installed.

// turbo
1. Activate the virtual environment:
```
.venv\Scripts\activate
```

// turbo
2. Install build dependencies (if not already installed):
```
pip install PyQt6 pywin32 pyinstaller
```

## Build

// turbo
3. Build using the spec file (bundles pywin32 DLLs and all dependencies automatically):
```
pyinstaller --clean CrashDetective.spec
```

## Output

4. The built executable will be at:
```
dist\CrashDetective.exe
```

You can distribute this single `.exe` file — no Python installation required on the target machine.

## Notes

- The `CrashDetective.spec` file handles all build configuration:
  - `collect_all('pywin32')` bundles pywin32 modules + DLLs
  - `--onefile` mode for single-file output
  - `--windowed` hides the console window
  - `icon.ico` is set as the app icon
- The `build/` folder is an intermediate build artifact and can be deleted
