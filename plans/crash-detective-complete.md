## Plan Complete: Crash Detective - Windows Crash Diagnosis Tool

Successfully created a standalone Windows GUI application that helps non-technical users diagnose why a game or program crashed. The tool reads Windows Event Logs, searches for crash events related to the selected executable, and provides user-friendly translations of technical error codes.

**Phases Completed:** 4 of 4
1. ✅ Phase 1: Base Structure and GUI
2. ✅ Phase 2: Windows Event Log Reading
3. ✅ Phase 3: Search and Matching Logic
4. ✅ Phase 4: Crash Interpreter and Copy Functionality

**All Files Created/Modified:**
- crash_finder.py (main application - single file)
- plans/crash-detective-plan.md (planning documentation)
- plans/crash-detective-phase-1-complete.md (phase 1 completion)

**Key Functions/Classes Added:**
- `CrashDetectiveWindow` - Main PyQt6 window class
- `read_application_logs(days)` - Windows Event Log reader with permission handling
- `interpret_crash(log_message)` - Error code translator with 12+ patterns
- `get_game_root_folder(exe_path)` - Smart game folder detection for Deep Scan
- `create_layout()`, `_handle_search()`, `_copy_to_clipboard()` - Core functionality

**Features Implemented:**
- ✅ Dark theme PyQt6 interface
- ✅ File browser for .exe selection (starts from app directory)
- ✅ Days dropdown (2, 3, 7, 14 days)
- ✅ Deep Scan with fuzzy matching AND game folder path detection
- ✅ Windows Event Log reading (Event IDs 1000, 1001, 1002)
- ✅ Permission error handling ("Run as Admin" message)
- ✅ Crash code translations (ACCESS_VIOLATION, GPU_ERROR, HEAP_CORRUPTION, etc.)
- ✅ Copy Report to Clipboard button
- ✅ Smart game root folder detection for Deep Scan
- ✅ Match reason display in results

**Crash Translations Included:**
- 0xc0000005 → ACCESS VIOLATION
- 0xc0000374 → HEAP CORRUPTION
- 0xc00000fd → STACK OVERFLOW
- 0xc0000409 → STACK BUFFER OVERRUN
- 0xc000001d → ILLEGAL INSTRUCTION
- 0xc0000142 → DLL INIT FAILED
- 0x80000003 → BREAKPOINT
- nvwgf → GPU ERROR (NVIDIA)
- d3d11 → GPU ERROR (Direct3D 11)
- dxgi → DirectX ERROR
- unity → UNITY ENGINE crash
- unreal/ue4 → UNREAL ENGINE crash

**Compilation Command:**
```bash
pip install PyQt6 pywin32 pyinstaller
pyinstaller --onefile --windowed --name "CrashDetective" crash_finder.py
```

**Recommendations for Next Steps:**
- Add more crash code translations as discovered
- Consider adding export to file functionality
- Add system info collection (GPU driver version, Windows version)
