# 🔎 Crash Detective

**A Windows desktop tool to diagnose why your games and applications crash.**

Crash Detective reads the Windows Event Log, finds crash events related to your selected executable, and translates cryptic error codes into plain, actionable explanations.

---

## ✨ Features

- **One-click crash diagnosis** — Select a `.exe`, get instant results
- **Smart game folder detection** — Automatically identifies the game's root folder, even when the `.exe` is nested in `bin/`, `Win64/`, etc.
- **100+ error pattern translations** — Covers NTSTATUS codes, GPU driver crashes (NVIDIA/AMD/Intel), anti-cheat systems, game engines, DRM, audio, network, and more
- **Fuzzy matching** — Finds related crashes even when the event log doesn't reference the exact executable name
- **General fallback search** — Searches both Application and System logs when no specific crash is found
- **Copy to clipboard** — One click to copy the full report and share it
- **Dark theme** — Modern Catppuccin-inspired dark UI

## 📸 How It Works

1. Click **Browse** and select the game/application `.exe`
2. Choose a search period (2, 3, 7, or 14 days)
3. Click **🔍 Search Crashes**
4. Read the translated results — each crash shows the faulting module, error code, and a plain-language explanation
5. Click **📋 Copy Report to Clipboard** to share

## 🛠️ Build

### Prerequisites

- Python 3.10+
- Virtual environment with dependencies:

```bash
pip install PyQt6 pywin32 pyinstaller
```

### Build the executable

```bash
pyinstaller --clean CrashDetective.spec
```

The output `.exe` will be in the `dist/` folder. No Python installation needed on the target machine.

## 📁 Project Structure

```
ErrorsGUI/
├── crash_finder.py         # Main application (single file)
├── CrashDetective.spec     # PyInstaller build configuration
├── icon.ico                # Application icon
├── .agent/workflows/       # Build workflow
└── plans/                  # Development notes
```

## ⚙️ Technical Details

- **GUI Framework:** PyQt6
- **Event Log Access:** pywin32 (`win32evtlog`, `win32con`)
- **Matching Strategy:** Exact match → fuzzy match (SequenceMatcher) → general folder search
- **Monitored Event IDs:** 1000 (Application Error), 1001 (Windows Error Reporting), 1002 (Application Hang)

---

# 🔎 Crash Detective (Español)

**Herramienta de escritorio para Windows que diagnostica por qué tus juegos y aplicaciones crashean.**

Crash Detective lee el Registro de Eventos de Windows, encuentra eventos de crash relacionados con el ejecutable seleccionado y traduce los códigos de error crípticos en explicaciones claras y accionables.

---

## ✨ Características

- **Diagnóstico de crash con un click** — Selecciona un `.exe`, obtén resultados al instante
- **Detección inteligente de carpeta del juego** — Identifica automáticamente la carpeta raíz del juego, incluso cuando el `.exe` está dentro de subcarpetas como `bin/`, `Win64/`, etc.
- **100+ traducciones de patrones de error** — Cubre códigos NTSTATUS, crashes de drivers GPU (NVIDIA/AMD/Intel), sistemas anti-cheat, motores de juego, DRM, audio, red, y más
- **Coincidencia difusa (fuzzy matching)** — Encuentra crashes relacionados incluso cuando el log de eventos no referencia el nombre exacto del ejecutable
- **Búsqueda general de respaldo** — Busca en los logs de Application y System cuando no se encuentra un crash específico
- **Copiar al portapapeles** — Un click para copiar el reporte completo y compartirlo
- **Tema oscuro** — Interfaz oscura moderna inspirada en Catppuccin

## 📸 Cómo Funciona

1. Haz click en **Browse** y selecciona el `.exe` del juego/aplicación
2. Elige un período de búsqueda (2, 3, 7 o 14 días)
3. Haz click en **🔍 Search Crashes**
4. Lee los resultados traducidos — cada crash muestra el módulo que falló, el código de error y una explicación en lenguaje simple
5. Haz click en **📋 Copy Report to Clipboard** para compartir

## 🛠️ Compilar

### Requisitos

- Python 3.10+
- Entorno virtual con dependencias:

```bash
pip install PyQt6 pywin32 pyinstaller
```

### Generar el ejecutable

```bash
pyinstaller --clean CrashDetective.spec
```

El `.exe` resultante estará en la carpeta `dist/`. No se necesita Python instalado en la máquina destino.

## ⚙️ Detalles Técnicos

- **Framework GUI:** PyQt6
- **Acceso al Event Log:** pywin32 (`win32evtlog`, `win32con`)
- **Estrategia de búsqueda:** Coincidencia exacta → coincidencia difusa (SequenceMatcher) → búsqueda general por carpeta
- **Event IDs monitoreados:** 1000 (Error de Aplicación), 1001 (Windows Error Reporting), 1002 (Aplicación Colgada)
