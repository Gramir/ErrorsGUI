## Phase 1 Complete: Base Structure and GUI

Created the main file `crash_finder.py` with the complete graphical interface using PySimpleGUI with dark theme. All UI elements are implemented and functional, with placeholder handlers ready for the following phases. All code and comments are in English.

**Files created/changed:**
- crash_finder.py

**Functions created/changed:**
- `create_layout()` - Creates the complete GUI layout
- `handle_search(values)` - Placeholder handler for search
- `handle_copy(window, results_text)` - Handler to copy to clipboard
- `create_window()` - Creates the main window
- `main()` - Main event loop

**UI Elements implemented:**
- File browser for .exe (`-EXE_PATH-`, `-BROWSE-`)
- Days dropdown (`-DAYS-`) with options 2, 3, 7, 14 days
- Deep Scan checkbox (`-DEEP_SCAN-`)
- Search button (`-SEARCH-`)
- Read-only Multiline area (`-RESULTS-`)
- Copy Report button (`-COPY-`)
- Magnifying glass icon embedded in base64

**Tests created/changed:**
- N/A (code verified with py_compile, no syntax errors)

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: Create Crash Detective GUI base structure

- Add PySimpleGUI dark theme interface with all UI elements
- Implement file browser for .exe selection
- Add days dropdown (2, 3, 7, 14 days) and Deep Scan checkbox
- Create large read-only results multiline area
- Add Copy Report to Clipboard button with clipboard functionality
- Embed magnifying glass icon in base64
- Setup placeholder handlers for search and copy functions
```
