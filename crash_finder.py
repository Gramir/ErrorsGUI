#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crash Detective - Windows Event Log Crash Finder
Tool to search for application crashes in Windows Event Log.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import PySimpleGUI as sg
import win32evtlog
import win32con
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import os
import ctypes
import base64

# ============================================================================
# CONSTANTS
# ============================================================================

# Magnifying glass icon embedded in base64 (16x16 PNG)
ICON_BASE64 = b'''
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAALEwAACxMBAJqcGAAAActJREFUOI2Nkz1oU2EUhp/v3ptfk5sm1dZWi4ODoKCDg4uDdBAHBxcn
wUEQcXFwcHRxcXBwEAQRBxdxcHBwcHBxcBAEBRERFBFBsP5ga2yS5t57v+NwE5LWtnThwOU9533O
+c4RVWUzG3Dz7F7buz7lXWPF/0REUX4r8YqI/PXMZvbR3cLHYGD+QL0xTaE4Sjy1lc7OH1RKH/gy
90LfvZy/1p+5x3d1l3GcCJXKILnCdnbsOkqmsI1CoUx3bprZ2Wf09n5i33Qjt2/Mq3e/xXON75iD
B4/huRdnwmDxYiLhzlWrUK1W8P2QWq1GOh2wsLBI6/6tZDINwuCvOE7wMBpbOFGtNKbjMRu7xm5i
c4NEIkFMrI8oXEMsDtfNvAfYCxCJxPHDgEajRr1eR8MQEYeEm0bcBIlEAt/38f2ARj0gDEMC3ycI
AoLAJwwaax3cRIJEIkkymaZR9/E8Hy8IWcY1x0GcOIlkkmQqheO4eJ6H7/vUPY8g8PG9QCpLJ/B6
WmKJZBLXjZNKpUkk06RSaRxdvKN1f0Vj1cbS5MpzlMCdJpHMsMVN8+p1g9kFOHK0Fy8ycPn8O/F7
Zxi5/3nD5+i/9hcw78hwPeFCaAAAAABJRU5ErkJggg==
'''

# Days options for dropdown
DAYS_OPTIONS = ['2 days', '3 days', '7 days', '14 days']
DAYS_MAP = {'2 days': 2, '3 days': 3, '7 days': 7, '14 days': 14}

# Application version
APP_VERSION = "1.0.0"
APP_TITLE = "Crash Detective"

# ============================================================================
# GUI LAYOUT
# ============================================================================

def create_layout():
    """Creates and returns the graphical interface layout."""
    
    # Dark theme
    sg.theme('DarkBlue3')
    
    # File selection section
    file_section = [
        [sg.Text('Executable file:', font=('Segoe UI', 10))],
        [
            sg.Input(key='-EXE_PATH-', size=(50, 1), enable_events=True),
            sg.FileBrowse(
                'Browse...', 
                file_types=(("Executables", "*.exe"), ("All files", "*.*")),
                key='-BROWSE-'
            )
        ]
    ]
    
    # Options section
    options_section = [
        [
            sg.Text('Search period:', font=('Segoe UI', 10)),
            sg.Combo(
                DAYS_OPTIONS, 
                default_value='2 days', 
                key='-DAYS-', 
                size=(10, 1),
                readonly=True
            ),
            sg.Push(),
            sg.Checkbox(
                'Deep Scan (fuzzy matching)', 
                key='-DEEP_SCAN-', 
                font=('Segoe UI', 10),
                tooltip='Enable approximate search to find name variants'
            )
        ]
    ]
    
    # Search button
    search_section = [
        [
            sg.Button(
                '🔍 Search Crashes', 
                key='-SEARCH-', 
                size=(20, 1),
                font=('Segoe UI', 11, 'bold'),
                button_color=('white', '#1a5fb4')
            )
        ]
    ]
    
    # Results area
    results_section = [
        [sg.Text('Results:', font=('Segoe UI', 10, 'bold'))],
        [
            sg.Multiline(
                size=(70, 20),
                key='-RESULTS-',
                font=('Consolas', 9),
                disabled=True,
                autoscroll=True,
                expand_x=True,
                expand_y=True
            )
        ]
    ]
    
    # Copy button
    copy_section = [
        [
            sg.Button(
                '📋 Copy Report to Clipboard',
                key='-COPY-',
                size=(30, 2),
                font=('Segoe UI', 11, 'bold'),
                button_color=('white', '#26a269')
            )
        ]
    ]
    
    # Complete layout
    layout = [
        [sg.Text(f'🔎 {APP_TITLE}', font=('Segoe UI', 16, 'bold'), text_color='#62a0ea')],
        [sg.HorizontalSeparator()],
        *file_section,
        [sg.Text('')],  # Spacer
        *options_section,
        [sg.Text('')],  # Spacer
        *search_section,
        [sg.HorizontalSeparator()],
        *results_section,
        [sg.HorizontalSeparator()],
        *copy_section,
        [sg.Text(f'v{APP_VERSION}', font=('Segoe UI', 8), text_color='gray', justification='right', expand_x=True)]
    ]
    
    return layout


# ============================================================================
# EVENT HANDLERS (PLACEHOLDERS)
# ============================================================================

def handle_search(values):
    """
    Placeholder handler for the search event.
    TODO: Implement in Phase 2 - Event Log search.
    """
    exe_path = values['-EXE_PATH-']
    days_str = values['-DAYS-']
    deep_scan = values['-DEEP_SCAN-']
    
    days = DAYS_MAP.get(days_str, 2)
    
    if not exe_path:
        return "⚠️ Please select an executable file."
    
    if not os.path.exists(exe_path):
        return f"❌ File does not exist: {exe_path}"
    
    exe_name = os.path.basename(exe_path)
    
    # Placeholder - debug message
    result = f"""╔══════════════════════════════════════════════════════════════╗
║                    CRASH DETECTIVE                              ║
╚══════════════════════════════════════════════════════════════╝

📁 File: {exe_name}
📂 Path: {exe_path}
📅 Period: Last {days} days
🔬 Deep Scan: {'Enabled' if deep_scan else 'Disabled'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Searching for crashes in Windows Event Log...

[PLACEHOLDER] Search function will be implemented in Phase 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return result


def handle_copy(window, results_text):
    """
    Handler to copy results to clipboard.
    """
    if not results_text or results_text.strip() == '':
        sg.popup_quick_message(
            '⚠️ No results to copy',
            background_color='#c64600',
            text_color='white',
            font=('Segoe UI', 10)
        )
        return False
    
    try:
        # Use Tkinter clipboard via PySimpleGUI
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(results_text)
        window.TKroot.update()
        
        sg.popup_quick_message(
            '✅ Report copied to clipboard',
            background_color='#26a269',
            text_color='white',
            font=('Segoe UI', 10)
        )
        return True
    except Exception as e:
        sg.popup_error(f'Error copying: {str(e)}')
        return False


# ============================================================================
# MAIN WINDOW & EVENT LOOP
# ============================================================================

def create_window():
    """Creates and returns the main window."""
    layout = create_layout()
    
    window = sg.Window(
        APP_TITLE,
        layout,
        icon=ICON_BASE64,
        resizable=True,
        finalize=True,
        size=(700, 600),
        element_justification='center'
    )
    
    return window


def main():
    """Main function - Event Loop."""
    
    # Create window
    window = create_window()
    
    # Variable to store current results
    current_results = ""
    
    # Event Loop
    while True:
        event, values = window.read()
        
        # Close window
        if event in (sg.WIN_CLOSED, 'Exit', None):
            break
        
        # Event: Search
        if event == '-SEARCH-':
            window['-RESULTS-'].update('🔄 Searching...')
            window.refresh()
            
            current_results = handle_search(values)
            window['-RESULTS-'].update(current_results)
        
        # Event: Copy to clipboard
        if event == '-COPY-':
            current_results = values['-RESULTS-']
            handle_copy(window, current_results)
        
        # Event: File path change
        if event == '-EXE_PATH-':
            exe_path = values['-EXE_PATH-']
            if exe_path and os.path.exists(exe_path):
                exe_name = os.path.basename(exe_path)
                window['-RESULTS-'].update(f'📁 File selected: {exe_name}\n\nPress "Search Crashes" to start the search.')
    
    # Close window
    window.close()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    main()
