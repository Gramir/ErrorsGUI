#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crash Detective - Windows Event Log Crash Finder
Tool to search for application crashes in Windows Event Log.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import sys
import win32evtlog
import win32con
import pywintypes
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QFileDialog, QMessageBox, QFrame, QStyle, QStyleOptionComboBox,
    QStyleOptionButton, QProxyStyle
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QIcon, QClipboard, QPixmap, QPainter, QColor, QPen, QPolygon


# ============================================================================
# CUSTOM STYLE FOR BETTER CHECKBOX AND COMBOBOX RENDERING
# ============================================================================

class CustomStyle(QProxyStyle):
    """Custom style that draws proper checkmarks and dropdown arrows."""
    
    def drawPrimitive(self, element, option, painter, widget=None):
        """Draw primitive elements with custom appearance."""
        if element == QStyle.PrimitiveElement.PE_IndicatorCheckBox:
            # Draw custom checkbox
            rect = option.rect
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw background
            if option.state & QStyle.StateFlag.State_On:
                # Checked state
                painter.setBrush(QColor("#1a5fb4"))
                painter.setPen(QPen(QColor("#1a5fb4"), 2))
            else:
                # Unchecked state
                painter.setBrush(QColor("#313244"))
                painter.setPen(QPen(QColor("#45475a"), 2))
            
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 3, 3)
            
            # Draw checkmark if checked
            if option.state & QStyle.StateFlag.State_On:
                painter.setPen(QPen(QColor("#ffffff"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                # Draw checkmark path
                cx = rect.center().x()
                cy = rect.center().y()
                painter.drawLine(cx - 4, cy, cx - 1, cy + 3)
                painter.drawLine(cx - 1, cy + 3, cx + 4, cy - 3)
            return
        
        if element == QStyle.PrimitiveElement.PE_IndicatorArrowDown:
            # Draw dropdown arrow
            rect = option.rect
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#cdd6f4"), 2))
            
            cx = rect.center().x()
            cy = rect.center().y()
            
            # Draw V shape arrow
            painter.drawLine(cx - 4, cy - 2, cx, cy + 2)
            painter.drawLine(cx, cy + 2, cx + 4, cy - 2)
            return
        
        super().drawPrimitive(element, option, painter, widget)
    
    def drawComplexControl(self, control, option, painter, widget=None):
        """Draw complex controls with custom appearance."""
        if control == QStyle.ComplexControl.CC_ComboBox:
            # Let base style draw the combobox
            super().drawComplexControl(control, option, painter, widget)
            
            # Draw our custom arrow on top
            arrow_rect = self.subControlRect(control, option, QStyle.SubControl.SC_ComboBoxArrow, widget)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#cdd6f4"), 2))
            
            cx = arrow_rect.center().x()
            cy = arrow_rect.center().y()
            
            # Draw V shape arrow
            painter.drawLine(cx - 4, cy - 2, cx, cy + 2)
            painter.drawLine(cx, cy + 2, cx + 4, cy - 2)
            return
        
        super().drawComplexControl(control, option, painter, widget)


# ============================================================================
# CONSTANTS
# ============================================================================

# Days options for dropdown
DAYS_OPTIONS = ['2 days', '3 days', '7 days', '14 days']
DAYS_MAP = {'2 days': 2, '3 days': 3, '7 days': 7, '14 days': 14}

# Application version
APP_VERSION = "1.0.0"
APP_TITLE = "Crash Detective"

# Application Error Event IDs
# 1000 = Application Error
# 1001 = Windows Error Reporting
# 1002 = Application Hang
APPLICATION_ERROR_EVENT_IDS = [1000, 1001, 1002]

# Common binary folder names in games
# These folders typically contain the .exe but are not the "root" game folder
BINARY_FOLDER_PATTERNS = [
    'bin', 'binaries', 'binary',
    'x64', 'x86', 'win64', 'win32',
    'game', 'build', 'out', 'output',
    'release', 'debug', 'shipping',
    'engine', 'runtime', 'launcher',
]

# Crash code translations - User-friendly error interpretations
# Keys are patterns to search for (case-insensitive)
# Values are human-readable explanations
CRASH_TRANSLATIONS = {
    # ================================================================
    # NTSTATUS EXCEPTION CODES - Memory and Access Violations
    # ================================================================
    '0xc0000005': 'ACCESS VIOLATION: Likely corrupted files or memory issue.',
    '0xc0000374': 'HEAP CORRUPTION: Internal game error.',
    '0xc00000fd': 'STACK OVERFLOW: Infinite loop or mod conflict.',
    '0xc0000409': 'STACK BUFFER OVERRUN: Game security or anti-cheat issue.',
    '0xc0000008': 'INVALID HANDLE: Corrupted files or driver conflict.',
    '0xc0000017': 'NO MEMORY: System ran out of memory, close other apps.',
    '0xc000009a': 'INSUFFICIENT RESOURCES: Not enough system resources.',
    '0xc0000006': 'IN-PAGE ERROR: Disk read failure, check your hard drive.',

    # ================================================================
    # NTSTATUS EXCEPTION CODES - CPU and Instruction Errors
    # ================================================================
    '0xc000001d': 'ILLEGAL INSTRUCTION: CPU incompatibility or corrupted game files.',
    '0xc000001e': 'INVALID LOCK SEQUENCE: Thread synchronization error.',
    '0xc0000025': 'NONCONTINUABLE EXCEPTION: Fatal error, cannot recover.',
    '0xc0000026': 'INVALID DISPOSITION: Bad exception handler, corrupted files.',
    '0xc000008c': 'ARRAY BOUNDS EXCEEDED: Memory overrun, verify game files.',
    '0xc000008d': 'FLOAT DENORMAL: Floating-point math error in application.',
    '0xc000008e': 'FLOAT DIVIDE BY ZERO: Math error, likely a game bug.',
    '0xc000008f': 'FLOAT INEXACT RESULT: Floating-point precision error.',
    '0xc0000090': 'FLOAT INVALID OPERATION: Invalid math operation in app.',
    '0xc0000091': 'FLOAT OVERFLOW: Number too large, possible game bug.',
    '0xc0000092': 'FLOAT STACK CHECK: Floating-point stack error.',
    '0xc0000093': 'FLOAT UNDERFLOW: Number too small, possible game bug.',
    '0xc0000094': 'INTEGER DIVIDE BY ZERO: Math error, verify game files.',
    '0xc0000095': 'INTEGER OVERFLOW: Number too large, possible game bug.',
    '0xc0000096': 'PRIVILEGED INSTRUCTION: App tried restricted CPU op.',

    # ================================================================
    # NTSTATUS EXCEPTION CODES - DLL and Initialization
    # ================================================================
    '0xc0000142': 'DLL INIT FAILED: Missing Visual C++ Redistributable or corrupted DLLs.',
    '0xc0000135': 'DLL NOT FOUND: Missing runtime DLL, reinstall the app.',
    '0xc000007b': 'INVALID IMAGE: 32/64-bit mismatch or corrupted files.',
    '0xc0000018': 'CONFLICTING ADDRESSES: DLL load conflict, reinstall app.',
    '0xc000012f': 'BAD IMAGE: Corrupted executable or DLL file.',
    '0xc0000020': 'INVALID FILE FOR SECTION: Corrupted DLL or EXE file.',

    # ================================================================
    # .NET / CLR EXCEPTION CODES
    # ================================================================
    '0xe0434352': '.NET CLR EXCEPTION: .NET app crash, repair/reinstall .NET.',
    '0xe0434f4d': '.NET COM ERROR: .NET COM interop failure.',
    '0xe06d7363': 'C++ EXCEPTION: Unhandled Visual C++ exception thrown.',

    # ================================================================
    # DEBUGGING AND SPECIAL CODES
    # ================================================================
    '0x80000003': 'BREAKPOINT: Debugger attached or anti-tamper triggered.',
    '0x80000004': 'SINGLE STEP: Debugging trace detected.',
    '0x40000015': 'FATAL APP EXIT: App called abort(), critical error.',
    '0x40010006': 'CTRL+C EXIT: App terminated by user or script.',
    '0xc0000602': 'UNKNOWN SOFTWARE EXCEPTION: Fail-fast or critical error.',
    '0xc00000f0': 'STATUS CANCELLED: Operation was cancelled unexpectedly.',

    # ================================================================
    # VISUAL C++ RUNTIME ERRORS
    # ================================================================
    '0x40000016': 'FATAL USER CALLBACK: C runtime callback error.',
    '0xc0000417': 'INVALID C RUNTIME PARAM: Bad parameter in C runtime call.',

    # ================================================================
    # GPU AND GRAPHICS ERRORS - NVIDIA
    # ================================================================
    'nvwgf': 'GPU ERROR: Graphics driver crash (NVIDIA).',
    'nvlddmkm': 'GPU ERROR: NVIDIA kernel driver crash, update drivers.',
    'nvoglv': 'GPU ERROR: NVIDIA OpenGL driver crash, update drivers.',
    'nvd3dum': 'GPU ERROR: NVIDIA Direct3D driver crash, update drivers.',
    'nvcuda': 'GPU ERROR: NVIDIA CUDA driver crash, update drivers.',

    # ================================================================
    # GPU AND GRAPHICS ERRORS - AMD/ATI
    # ================================================================
    'atidxx': 'GPU ERROR: AMD/ATI Direct3D driver crash, update drivers.',
    'amdxc': 'GPU ERROR: AMD DirectX driver crash, update drivers.',
    'atioglxx': 'GPU ERROR: AMD/ATI OpenGL driver crash, update drivers.',
    'atig6pxx': 'GPU ERROR: AMD graphics driver crash, update drivers.',
    'amdkmdap': 'GPU ERROR: AMD kernel driver crash, update drivers.',

    # ================================================================
    # GPU AND GRAPHICS ERRORS - DirectX / Generic
    # ================================================================
    'd3d11': 'GPU ERROR: Graphics driver crash (Direct3D 11).',
    'd3d12': 'GPU ERROR: Direct3D 12 crash, update GPU drivers.',
    'd3d10': 'GPU ERROR: Direct3D 10 crash, update GPU drivers.',
    'd3d9': 'GPU ERROR: Direct3D 9 crash, install legacy DirectX.',
    'dxgi': 'DirectX ERROR: Graphics API crash, update DirectX.',
    'd3dcompiler': 'DirectX ERROR: Shader compiler crash, update DirectX.',
    'dxcore': 'DirectX ERROR: DirectX core crash, update Windows.',
    'igdumdim': 'GPU ERROR: Intel graphics driver crash, update drivers.',
    'igdkmd': 'GPU ERROR: Intel kernel graphics crash, update drivers.',
    'ig4icd': 'GPU ERROR: Intel legacy GPU driver crash, update drivers.',

    # ================================================================
    # COMMON FAULTING MODULES - Windows System DLLs
    # ================================================================
    'ntdll.dll': 'SYSTEM DLL: Low-level Windows crash, check for updates.',
    'kernelbase.dll': 'KERNEL ERROR: Windows API crash, update Windows.',
    'kernel32.dll': 'KERNEL ERROR: Core Windows crash, system needs update.',
    'ucrtbase.dll': 'C RUNTIME: Universal C Runtime crash, repair Visual C++.',
    'msvcrt.dll': 'C RUNTIME: Visual C++ runtime crash, reinstall VC++.',
    'msvcr100.dll': 'VC++ 2010 RUNTIME: Reinstall VC++ 2010 Redistributable.',
    'msvcr110.dll': 'VC++ 2012 RUNTIME: Reinstall VC++ 2012 Redistributable.',
    'msvcr120.dll': 'VC++ 2013 RUNTIME: Reinstall VC++ 2013 Redistributable.',
    'msvcp140.dll': 'VC++ 2015+ RUNTIME: Reinstall VC++ 2015-2022 Redist.',
    'vcruntime140.dll': 'VC++ RUNTIME: Reinstall VC++ 2015-2022 Redistributable.',
    'concrt140.dll': 'VC++ CONCURRENCY: Reinstall VC++ 2015-2022 Redist.',

    # ================================================================
    # COMMON FAULTING MODULES - .NET / CLR
    # ================================================================
    'clr.dll': '.NET CLR CRASH: .NET Framework runtime error, repair .NET.',
    'coreclr.dll': '.NET CORE CRASH: .NET Core/5+ runtime error.',
    'clrjit.dll': '.NET JIT CRASH: .NET JIT compiler error, repair .NET.',
    'mscorwks.dll': '.NET 2.0 CRASH: Old .NET Framework error, update .NET.',
    'mscorlib': '.NET LIBRARY CRASH: .NET base library error.',
    'wpfgfx': 'WPF CRASH: .NET WPF graphics subsystem crash.',

    # ================================================================
    # ANTI-CHEAT SYSTEMS
    # ================================================================
    'easyanticheat': 'ANTI-CHEAT: EasyAntiCheat crash. Repair or reinstall.',
    'eac_launcher': 'ANTI-CHEAT: EasyAntiCheat launcher error, repair EAC.',
    'battleye': 'ANTI-CHEAT: BattlEye crash, verify game files.',
    'beclient': 'ANTI-CHEAT: BattlEye client crash, reinstall BattlEye.',
    'beservice': 'ANTI-CHEAT: BattlEye service crash, reinstall BattlEye.',
    'bedaisy': 'ANTI-CHEAT: BattlEye driver error, update Windows.',
    'vanguard': 'ANTI-CHEAT: Riot Vanguard crash, restart PC.',
    'vgk.sys': 'ANTI-CHEAT: Riot Vanguard kernel crash, reinstall.',
    'eossdk': 'EPIC SERVICES: Epic Online Services crash.',
    'nprotect': 'ANTI-CHEAT: nProtect GameGuard crash, reinstall game.',
    'xigncode': 'ANTI-CHEAT: XIGNCODE crash, verify game files.',

    # ================================================================
    # DRM / COPY PROTECTION
    # ================================================================
    'denuvo': 'DRM: Denuvo anti-tamper crash, verify game files.',
    'steam_api': 'STEAM API: Steam integration crash, verify game files.',
    'steam_api64': 'STEAM API: Steam integration crash, verify game files.',
    'steamclient': 'STEAM CLIENT: Steam client crash, restart Steam.',
    'galaxydll': 'GOG GALAXY: GOG Galaxy integration crash.',
    'uplay_r': 'UBISOFT CONNECT: Ubisoft DRM crash, relaunch client.',

    # ================================================================
    # GAME ENGINES
    # ================================================================
    'unity': 'UNITY ENGINE: Game engine crash, verify game files.',
    'unreal': 'UNREAL ENGINE: Game engine crash, verify game files.',
    'ue4': 'UNREAL ENGINE: Game engine crash, verify game files.',
    'ue5': 'UNREAL ENGINE 5: Game engine crash, verify game files.',
    'cryengine': 'CRYENGINE: Game engine crash, verify game files.',
    'frostbite': 'FROSTBITE ENGINE: Game engine crash, verify files.',
    'gameoverlayrenderer': 'STEAM OVERLAY: Steam overlay crash, disable overlay.',
    'renderdoc': 'RENDERDOC: Graphics debugger conflict, close RenderDoc.',

    # ================================================================
    # AUDIO RELATED
    # ================================================================
    'xaudio2': 'AUDIO ERROR: XAudio2 crash, reinstall DirectX.',
    'dsound.dll': 'AUDIO ERROR: DirectSound crash, check audio drivers.',
    'wwise': 'AUDIO ENGINE: Wwise audio engine crash.',
    'fmod': 'AUDIO ENGINE: FMOD audio engine crash.',

    # ================================================================
    # NETWORK / ONLINE
    # ================================================================
    'ws2_32.dll': 'NETWORK ERROR: Winsock crash, check network drivers.',
    'winhttp.dll': 'NETWORK ERROR: HTTP connection crash, check network.',
    'mswsock.dll': 'NETWORK ERROR: Windows socket provider crash.',
}

# Dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel {
    color: #cdd6f4;
    font-size: 14px;
}
QLabel#title {
    color: #89b4fa;
    font-size: 22px;
    font-weight: bold;
}
QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 8px;
    color: #cdd6f4;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #89b4fa;
}
QPushButton {
    background-color: #1a5fb4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2d7cd6;
}
QPushButton:pressed {
    background-color: #155099;
}
QPushButton#searchBtn {
    background-color: #1a5fb4;
    font-size: 15px;
    padding: 12px 24px;
}
QPushButton#copyBtn {
    background-color: #26a269;
    font-size: 15px;
    padding: 14px 28px;
}
QPushButton#copyBtn:hover {
    background-color: #33b978;
}
QPushButton#browseBtn {
    background-color: #45475a;
    padding: 6px 12px;
}
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 8px 12px;
    color: #cdd6f4;
    font-size: 13px;
    min-width: 120px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #1a5fb4;
    color: #cdd6f4;
    font-size: 13px;
}
QCheckBox {
    color: #cdd6f4;
    font-size: 13px;
    spacing: 10px;
}
QTextEdit {
    background-color: #11111b;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 10px;
    color: #cdd6f4;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}
QFrame#separator {
    background-color: #45475a;
    max-height: 1px;
}
"""


# ============================================================================
# GAME FOLDER DETECTION
# ============================================================================

def get_game_root_folder(exe_path):
    """
    Detect the game's root folder by traversing up from the .exe location.
    
    Games often have .exe files in subfolders like:
    - C:/Games/Stellar Blade/bin/sb.exe -> root is "Stellar Blade"
    - C:/Games/Game/Binaries/Win64/game.exe -> root is "Game"
    
    This function identifies common binary folder patterns and goes up
    to find the actual game folder.
    
    Args:
        exe_path: Full path to the .exe file
        
    Returns:
        tuple: (game_root_path, game_folder_name)
               game_root_path is the full path to the game's root folder
               game_folder_name is just the folder name
    """
    exe_dir = os.path.dirname(os.path.abspath(exe_path))
    current_path = exe_dir
    
    # Keep track of how many levels we've gone up (limit to prevent going too high)
    max_levels = 4
    levels_up = 0
    
    while levels_up < max_levels:
        folder_name = os.path.basename(current_path)
        folder_name_lower = folder_name.lower()
        
        # Check if current folder is a binary folder pattern
        is_binary_folder = False
        for pattern in BINARY_FOLDER_PATTERNS:
            if pattern in folder_name_lower:
                is_binary_folder = True
                break
        
        if is_binary_folder:
            # Go up one level
            parent = os.path.dirname(current_path)
            if parent == current_path:  # Reached root
                break
            current_path = parent
            levels_up += 1
        else:
            # This folder doesn't match binary patterns, consider it the game root
            break
    
    # Safety check: don't return drive root or common folders
    folder_name = os.path.basename(current_path)
    folder_name_lower = folder_name.lower()
    
    # Avoid returning too generic folders
    generic_folders = ['games', 'program files', 'program files (x86)', 'steam', 'steamapps', 'common', 'users', '']
    if folder_name_lower in generic_folders:
        # Return the original exe directory instead
        return exe_dir, os.path.basename(exe_dir)
    
    return current_path, folder_name


# ============================================================================
# EVENT LOG READING
# ============================================================================

def read_application_logs(days):
    """
    Read Windows Application Event Logs for crash events.
    
    Args:
        days: Number of days to look back for events
        
    Returns:
        tuple: (list of log entries, error message or None)
        Each log entry is a dict with keys:
            - timestamp: datetime object
            - source: event source name
            - event_id: event ID number
            - message: event message/description
            - raw_data: additional data from the event
    """
    logs = []
    error_msg = None
    
    # Calculate time threshold
    time_threshold = datetime.now() - timedelta(days=days)
    
    try:
        # Open the Application event log
        hand = win32evtlog.OpenEventLog(None, "Application")
        
        if not hand:
            return [], "Failed to open Application Event Log"
        
        try:
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            while True:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                
                if not events:
                    break
                
                for event in events:
                    # Get event timestamp
                    event_time = event.TimeGenerated
                    
                    # Convert pywintypes.datetime to Python datetime if needed
                    if hasattr(event_time, 'Format'):
                        event_time = datetime(
                            event_time.year,
                            event_time.month,
                            event_time.day,
                            event_time.hour,
                            event_time.minute,
                            event_time.second
                        )
                    
                    # Stop if event is older than threshold
                    if event_time < time_threshold:
                        # Since we're reading backwards, we can stop here
                        break
                    
                    # Filter by event type (Error = 1)
                    event_type = event.EventType
                    if event_type != win32con.EVENTLOG_ERROR_TYPE:
                        continue
                    
                    # Get Event ID (mask to get actual ID)
                    event_id = event.EventID & 0xFFFF
                    
                    # Filter by specific crash-related Event IDs
                    if event_id not in APPLICATION_ERROR_EVENT_IDS:
                        continue
                    
                    # Extract event message
                    message = ""
                    if event.StringInserts:
                        message = " | ".join([str(s) for s in event.StringInserts if s])
                    
                    # Get additional data
                    raw_data = ""
                    if event.Data:
                        try:
                            raw_data = event.Data.decode('utf-8', errors='ignore')
                        except:
                            raw_data = str(event.Data)
                    
                    log_entry = {
                        'timestamp': event_time,
                        'source': event.SourceName or "Unknown",
                        'event_id': event_id,
                        'message': message,
                        'raw_data': raw_data
                    }
                    logs.append(log_entry)
                
                # Check if we've gone past the time threshold
                if events and event_time < time_threshold:
                    break
                    
        finally:
            win32evtlog.CloseEventLog(hand)
            
    except PermissionError:
        error_msg = "❌ Access denied. Please run as Administrator."
    except pywintypes.error as e:
        # Handle Windows-specific errors
        error_code = e.args[0] if e.args else 0
        if error_code == 5:  # Access denied
            error_msg = "❌ Access denied. Please run as Administrator."
        else:
            error_msg = f"❌ Windows Error: {str(e)}"
    except Exception as e:
        error_msg = f"❌ Error reading Event Log: {str(e)}"
    
    return logs, error_msg


def read_general_logs(days, game_folder_name, game_root_path):
    """
    Read BOTH Application and System event logs for any error event
    that mentions the game folder name or path. This is a last-resort
    general search with no Event ID filter.
    
    Args:
        days: Number of days to look back for events
        game_folder_name: Name of the game's root folder
        game_root_path: Full path to the game's root folder
        
    Returns:
        tuple: (list of log entries, error message or None)
        Each log entry is a dict with keys:
            - timestamp, source, event_id, message, raw_data, log_source_name
    """
    logs = []
    error_msg = None
    max_results = 10
    
    # Calculate time threshold
    time_threshold = datetime.now() - timedelta(days=days)
    
    # Prepare search terms
    folder_lower = game_folder_name.lower() if game_folder_name else ""
    root_normalized = game_root_path.replace('\\', '/').lower() if game_root_path else ""
    
    log_names = ["Application", "System"]
    
    for log_name in log_names:
        if len(logs) >= max_results:
            break
        
        try:
            hand = win32evtlog.OpenEventLog(None, log_name)
            
            if not hand:
                continue
            
            try:
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                
                while True:
                    if len(logs) >= max_results:
                        break
                    
                    events = win32evtlog.ReadEventLog(hand, flags, 0)
                    
                    if not events:
                        break
                    
                    past_threshold = False
                    for event in events:
                        if len(logs) >= max_results:
                            break
                        
                        # Get event timestamp
                        event_time = event.TimeGenerated
                        
                        # Convert pywintypes.datetime to Python datetime if needed
                        if hasattr(event_time, 'Format'):
                            event_time = datetime(
                                event_time.year,
                                event_time.month,
                                event_time.day,
                                event_time.hour,
                                event_time.minute,
                                event_time.second
                            )
                        
                        # Stop if event is older than threshold
                        if event_time < time_threshold:
                            past_threshold = True
                            break
                        
                        # Filter by event type (Error only)
                        event_type = event.EventType
                        if event_type != win32con.EVENTLOG_ERROR_TYPE:
                            continue
                        
                        # Get Event ID (mask to get actual ID)
                        event_id = event.EventID & 0xFFFF
                        
                        # Extract event message
                        message = ""
                        if event.StringInserts:
                            message = " | ".join([str(s) for s in event.StringInserts if s])
                        
                        message_lower = message.lower()
                        message_normalized = message_lower.replace('\\', '/')
                        
                        # Check if message mentions game folder or path
                        is_related = False
                        if len(folder_lower) > 3 and folder_lower in message_lower:
                            is_related = True
                        elif len(root_normalized) > 10 and root_normalized in message_normalized:
                            is_related = True
                        
                        if not is_related:
                            continue
                        
                        # Get additional data
                        raw_data = ""
                        if event.Data:
                            try:
                                raw_data = event.Data.decode('utf-8', errors='ignore')
                            except:
                                raw_data = str(event.Data)
                        
                        log_entry = {
                            'timestamp': event_time,
                            'source': event.SourceName or "Unknown",
                            'event_id': event_id,
                            'message': message,
                            'raw_data': raw_data,
                            'log_source_name': log_name
                        }
                        logs.append(log_entry)
                    
                    if past_threshold:
                        break
                        
            finally:
                win32evtlog.CloseEventLog(hand)
                
        except PermissionError:
            error_msg = "❌ Access denied. Please run as Administrator."
            break
        except pywintypes.error as e:
            error_code = e.args[0] if e.args else 0
            if error_code == 5:  # Access denied
                error_msg = "❌ Access denied. Please run as Administrator."
                break
            else:
                error_msg = f"❌ Windows Error reading {log_name} log: {str(e)}"
                continue
        except Exception as e:
            error_msg = f"❌ Error reading {log_name} Event Log: {str(e)}"
            continue
    
    return logs, error_msg


# ============================================================================
# CRASH INTERPRETATION
# ============================================================================

def interpret_crash(log_message):
    """
    Interpret crash log message and return user-friendly translations.
    
    Args:
        log_message: The log message text to analyze
        
    Returns:
        list: List of matching translations, or default message if none found
    """
    if not log_message:
        return ["No specific error pattern detected."]
    
    message_lower = log_message.lower()
    translations = []
    
    # Check each pattern against the message
    for pattern, translation in CRASH_TRANSLATIONS.items():
        if pattern.lower() in message_lower:
            translations.append(translation)
    
    # Return translations found, or default message
    if translations:
        return translations
    else:
        return ["No specific error pattern detected."]


# ============================================================================
# MAIN WINDOW
# ============================================================================

class CrashDetectiveWindow(QMainWindow):
    """Main window for Crash Detective application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Crash Detective")
        self.setMinimumSize(700, 600)
        self.resize(750, 650)
        
        # Set window icon
        self._set_window_icon()
        
        # Set dark theme
        self.setStyleSheet(DARK_STYLESHEET)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(f"🔎 {APP_TITLE}")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Separator
        main_layout.addWidget(self._create_separator())
        
        # File selection section
        file_label = QLabel("Executable file:")
        main_layout.addWidget(file_label)
        
        file_layout = QHBoxLayout()
        self.exe_path_input = QLineEdit()
        self.exe_path_input.setPlaceholderText("Select an executable file...")
        self.exe_path_input.textChanged.connect(self._on_file_changed)
        file_layout.addWidget(self.exe_path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setObjectName("browseBtn")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        main_layout.addLayout(file_layout)
        
        # Options section
        options_layout = QHBoxLayout()
        
        period_label = QLabel("Search period:")
        options_layout.addWidget(period_label)
        
        self.days_combo = QComboBox()
        self.days_combo.addItems(DAYS_OPTIONS)
        self.days_combo.setCurrentText("2 days")
        options_layout.addWidget(self.days_combo)
        
        options_layout.addStretch()
        
        main_layout.addLayout(options_layout)
        
        # Search button
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        self.search_btn = QPushButton("🔍 Search Crashes")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.clicked.connect(self._search_crashes)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)
        
        # Separator
        main_layout.addWidget(self._create_separator())
        
        # Results section
        results_label = QLabel("Results:")
        results_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(250)
        main_layout.addWidget(self.results_text, 1)
        
        # Separator
        main_layout.addWidget(self._create_separator())
        
        # Copy button
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        self.copy_btn = QPushButton("📋 Copy Report to Clipboard")
        self.copy_btn.setObjectName("copyBtn")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        copy_layout.addWidget(self.copy_btn)
        copy_layout.addStretch()
        main_layout.addLayout(copy_layout)
        
        # Version label
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("color: gray; font-size: 9px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(version_label)
    
    def _create_separator(self):
        """Create a horizontal separator line."""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        return separator
    
    def _set_window_icon(self):
        """Set the window icon - create a simple magnifying glass icon."""
        try:
            # Create a simple 32x32 pixmap as icon
            from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
            from PyQt6.QtCore import QPoint
            
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw magnifying glass
            pen = QPen(QColor("#89b4fa"))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor("#313244")))
            
            # Circle (lens)
            painter.drawEllipse(4, 4, 18, 18)
            
            # Handle
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(QPoint(19, 19), QPoint(28, 28))
            
            painter.end()
            
            self.setWindowIcon(QIcon(pixmap))
        except Exception:
            pass  # Use default icon if creation fails
    
    def _browse_file(self):
        """Open file browser dialog."""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable",
            initial_dir,
            "Executables (*.exe);;All files (*.*)"
        )
        if file_path:
            self.exe_path_input.setText(file_path)
    
    def _on_file_changed(self, text):
        """Handle file path change - auto-search when file is selected."""
        if text and os.path.exists(text) and text.lower().endswith('.exe'):
            # Auto-search when a valid exe is selected
            self._search_crashes()
    
    def _search_crashes(self):
        """Perform crash search."""
        self.results_text.setText("🔄 Searching...")
        QApplication.processEvents()
        
        result = self._handle_search()
        self.results_text.setText(result)
    
    def _handle_search(self):
        """
        Handler for the search event.
        Reads Windows Event Log and searches for crash events.
        """
        exe_path = self.exe_path_input.text()
        days_str = self.days_combo.currentText()
        
        days = DAYS_MAP.get(days_str, 2)
        
        if not exe_path:
            return "⚠️ Please select an executable file."
        
        if not os.path.exists(exe_path):
            return f"❌ File does not exist: {exe_path}"
        
        exe_name = os.path.basename(exe_path)
        exe_name_lower = exe_name.lower()
        exe_name_no_ext = os.path.splitext(exe_name)[0].lower()
        
        # Get game root folder for fuzzy matching
        game_root_path, game_folder_name = get_game_root_folder(exe_path)
        game_folder_lower = game_folder_name.lower()
        
        # Normalize path separators for matching
        game_root_normalized = game_root_path.replace('\\', '/').lower()
        
        # Build header
        result = f"""╔══════════════════════════════════════════════════════════════╗
║                    CRASH DETECTIVE                              ║
╚══════════════════════════════════════════════════════════════╝

📁 File: {exe_name}
📂 Path: {exe_path}
🎮 Game Folder: {game_root_path}
📅 Period: Last {days} days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Read event logs
        logs, error_msg = read_application_logs(days)
        
        # Check for errors
        if error_msg:
            result += f"\n{error_msg}\n"
            return result
        
        # Filter logs matching the executable
        matching_logs = []
        
        for log in logs:
            source_lower = log['source'].lower()
            message_lower = log['message'].lower()
            # Normalize path separators in message for path matching
            message_normalized = message_lower.replace('\\', '/')
            
            # Check for exact match in source or message
            is_match = False
            match_reason = ""
            
            if exe_name_lower in source_lower or exe_name_lower in message_lower:
                is_match = True
                match_reason = "exe name match"
            elif exe_name_no_ext in source_lower or exe_name_no_ext in message_lower:
                is_match = True
                match_reason = "exe name (no ext) match"
            
            # Fuzzy matching and game folder path matching (auto-fallback)
            if not is_match:
                # Check similarity ratio with source
                ratio_source = SequenceMatcher(None, exe_name_no_ext, source_lower).ratio()
                if ratio_source > 0.6:
                    is_match = True
                    match_reason = f"fuzzy match (source: {ratio_source:.0%})"
                
                # Check if game folder name appears in message
                if not is_match and len(game_folder_lower) > 3:
                    if game_folder_lower in message_lower:
                        is_match = True
                        match_reason = f"game folder name match ({game_folder_name})"
                
                # Check if game root path appears in message
                if not is_match and len(game_root_normalized) > 10:
                    if game_root_normalized in message_normalized:
                        is_match = True
                        match_reason = f"game path match"
                
                # Check any word in message matches exe name
                if not is_match:
                    words = message_lower.split()
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            ratio = SequenceMatcher(None, exe_name_no_ext, word).ratio()
                            if ratio > 0.6:
                                is_match = True
                                match_reason = f"fuzzy match (word: {ratio:.0%})"
                                break
            
            if is_match:
                log['match_reason'] = match_reason
                matching_logs.append(log)
        
        # Display results
        if not matching_logs:
            # Try general search as last resort
            general_logs, general_error = read_general_logs(days, game_folder_name, game_root_path)
            if general_error:
                result += f"\n{general_error}\n"
            elif general_logs:
                result += f"\n⚠️ No specific crash events found for the executable.\n"
                result += f"📂 General search: Found {len(general_logs)} error event(s) related to game folder '{game_folder_name}':\n"
                result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                
                for i, log in enumerate(general_logs, 1):
                    timestamp_str = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    result += f"\n📌 Event #{i} [{log['log_source_name']}]\n"
                    result += f"   ⏰ Time: {timestamp_str}\n"
                    result += f"   📋 Source: {log['source']}\n"
                    result += f"   🔢 Event ID: {log['event_id']}\n"
                    
                    # Show message (truncated if needed)
                    message = log['message']
                    if len(message) > 500:
                        message = message[:500] + "..."
                    if message:
                        result += f"   💬 Details: {message}\n"
                    
                    # Run interpret_crash on these
                    full_log_text = log['message'] + " " + log.get('raw_data', '')
                    translations = interpret_crash(full_log_text)
                    result += f"   🔍 Translation:\n"
                    for t in translations:
                        result += f"      ⚠️ {t}\n"
                    
                    result += "\n"
                
                result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                result += f"📊 Summary: {len(general_logs)} general error(s) found in Application+System logs.\n"
            else:
                # Truly nothing found
                result += f"\n✅ No crash events found for '{exe_name}' in the last {days} days.\n"
                result += f"   (Searched: exact match → fuzzy match → general folder search)\n"
                result += f"\n📊 Total crash events scanned: {len(logs)}\n"
        else:
            result += f"\n🔴 Found {len(matching_logs)} crash event(s) for '{exe_name}':\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for i, log in enumerate(matching_logs, 1):
                timestamp_str = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                match_reason = log.get('match_reason', 'direct match')
                result += f"\n📌 Event #{i}\n"
                result += f"   ⏰ Time: {timestamp_str}\n"
                result += f"   📋 Source: {log['source']}\n"
                result += f"   🔢 Event ID: {log['event_id']}\n"
                result += f"   🎯 Match: {match_reason}\n"
                
                # Format message with descriptive labels
                message = log['message']
                if len(message) > 800:
                    message = message[:800] + "..."
                
                # Parse message parts and assign descriptive labels
                # Windows Event Log 1000 format:
                # 0: Faulting application name
                # 1: Version
                # 2: Timestamp
                # 3: Faulting module name
                # 4: Module version
                # 5: Module timestamp
                # 6: Exception code
                # 7: Fault offset
                # 8: Faulting process ID
                # 9: Application start time
                # 10: Application path
                # 11: Module path
                # 12: Report ID
                
                DETAIL_LABELS = [
                    "Faulting application name",
                    "Application version",
                    "Application timestamp",
                    "Faulting module name",
                    "Module version",
                    "Module timestamp",
                    "Exception code",
                    "Fault offset",
                    "Faulting process ID",
                    "Application start time",
                    "Faulting application path",
                    "Faulting module path",
                    "Report ID"
                ]
                
                if message:
                    result += f"   💬 Crash Details:\n"
                    msg_parts = message.split(' | ')
                    for idx, part in enumerate(msg_parts[:13]):  # Up to 13 parts
                        if part.strip():
                            label = DETAIL_LABELS[idx] if idx < len(DETAIL_LABELS) else f"Field {idx}"
                            result += f"      • {label}: {part.strip()}\n"
                
                if log['raw_data']:
                    result += f"   📦 Raw Data: {log['raw_data'][:100]}...\n" if len(log['raw_data']) > 100 else f"   📦 Raw Data: {log['raw_data']}\n"
                
                # Get crash interpretation
                full_log_text = message + " " + log.get('raw_data', '')
                translations = interpret_crash(full_log_text)
                
                result += f"   🔍 Translation:\n"
                for translation in translations:
                    result += f"      ⚠️ {translation}\n"
                
                result += "\n"
            
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result += f"📊 Summary: {len(matching_logs)} crash(es) found out of {len(logs)} total error events.\n"
        
        return result
    
    def _copy_to_clipboard(self):
        """Copy results to clipboard."""
        results_text = self.results_text.toPlainText()
        
        if not results_text or results_text.strip() == '':
            QMessageBox.warning(self, "Warning", "⚠️ No results to copy")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(results_text)
        
        QMessageBox.information(self, "Success", "✅ Report copied to clipboard")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main function - Application entry point."""
    app = QApplication(sys.argv)
    
    # Apply custom style for better checkbox and combobox rendering
    custom_style = CustomStyle('Fusion')
    app.setStyle(custom_style)
    
    window = CrashDetectiveWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
