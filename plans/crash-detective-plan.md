## Plan: Crash Detective - Windows Crash Diagnosis Tool

Aplicación GUI standalone de Windows que ayuda a usuarios no técnicos a diagnosticar por qué un programa o juego se bloqueó. Lee los logs de eventos de Windows, busca errores relacionados con el ejecutable seleccionado, y proporciona traducciones amigables de los códigos de error técnicos.

**Tech Stack:** Python, PySimpleGUI (tema oscuro), pywin32 (win32evtlog), difflib

---

## Fases de Implementación

### Phase 1: Estructura Base y GUI
- **Objetivo:** Crear la estructura básica del archivo con la interfaz PySimpleGUI usando tema oscuro, incluyendo todos los elementos de UI requeridos.
- **Archivos a crear:** `crash_finder.py`
- **Tests a escribir:** 
  - `test_gui_elements_exist` - Verificar que todos los elementos de UI estén definidos
  - `test_theme_is_dark` - Verificar que se use tema oscuro
- **Pasos:**
  1. Crear archivo con imports necesarios (PySimpleGUI, win32evtlog, difflib, datetime)
  2. Definir layout con: file browser para .exe, dropdown de días, checkbox "Deep Scan", botón "Search", área de resultados multiline, botón "Copy Report"
  3. Crear icono simple de lupa embebido en base64
  4. Implementar loop de eventos básico
  5. Ejecutar para verificar que la GUI se renderiza correctamente

---

### Phase 2: Lectura de Windows Event Log
- **Objetivo:** Implementar la función para leer logs de eventos de Windows con filtros de tiempo y manejo de permisos.
- **Archivos a modificar:** `crash_finder.py`
- **Tests a escribir:**
  - `test_read_event_logs_returns_list` - Verificar que la función retorna una lista
  - `test_filter_by_days` - Verificar filtrado por rango de días
  - `test_permission_error_handling` - Verificar manejo graceful de errores de permisos
- **Pasos:**
  1. Crear función `read_application_logs(days)` que use `win32evtlog.OpenEventLog`
  2. Filtrar por Event IDs 1000, 1001, 1002 (errores de aplicación)
  3. Filtrar por rango de tiempo según días seleccionados
  4. Implementar try/catch para errores de permisos con mensaje "Run as Admin"
  5. Ejecutar tests para confirmar funcionalidad

---

### Phase 3: Lógica de Búsqueda y Matching
- **Objetivo:** Implementar búsqueda estricta y fuzzy matching para encontrar logs relacionados con el .exe seleccionado.
- **Archivos a modificar:** `crash_finder.py`
- **Tests a escribir:**
  - `test_strict_match_finds_exact_exe_name` - Verificar match exacto del nombre .exe
  - `test_fuzzy_match_finds_similar_names` - Verificar que fuzzy match encuentra nombres similares
  - `test_deep_scan_toggle` - Verificar que Deep Scan activa/desactiva fuzzy matching
- **Pasos:**
  1. Crear función `strict_match(exe_name, log_message)` que busque el nombre exacto
  2. Crear función `fuzzy_match(exe_name, source_name, threshold=0.6)` usando `difflib.SequenceMatcher`
  3. Integrar ambas funciones en el flujo de búsqueda
  4. Conectar checkbox "Deep Scan" para activar fuzzy matching
  5. Ejecutar tests para confirmar funcionalidad

---

### Phase 4: Intérprete de Crashes y Funcionalidad de Copia
- **Objetivo:** Implementar las traducciones de errores y el botón de copiar al portapapeles.
- **Archivos a modificar:** `crash_finder.py`
- **Tests a escribir:**
  - `test_translate_access_violation` - Verificar traducción de 0xc0000005
  - `test_translate_gpu_error` - Verificar traducción de nvwgf/d3d11
  - `test_translate_heap_corruption` - Verificar traducción de 0xc0000374
  - `test_translate_additional_errors` - Verificar traducciones adicionales
  - `test_copy_to_clipboard` - Verificar que el botón copia el contenido
- **Pasos:**
  1. Crear función `interpret_crash(log_text)` con reglas de traducción
  2. Implementar traducciones principales:
     - `0xc0000005` → "ACCESS VIOLATION: Likely corrupted files or memory issue."
     - `nvwgf` o `d3d11` → "GPU ERROR: Graphics driver crash."
     - `0xc0000374` → "HEAP CORRUPTION: Internal game error."
  3. Implementar traducciones adicionales para errores comunes de juegos:
     - `0xc0000409` → "STACK BUFFER OVERRUN: Game security or anti-cheat issue."
     - `0xc000001d` → "ILLEGAL INSTRUCTION: CPU incompatibility or corrupted game files."
     - `0xc0000142` → "DLL INIT FAILED: Missing Visual C++ Redistributable or corrupted DLLs."
     - `0xc00000fd` → "STACK OVERFLOW: Infinite loop or mod conflict."
     - `0x80000003` → "BREAKPOINT: Debugger attached or anti-tamper triggered."
     - `dxgi` → "DirectX ERROR: Graphics API crash, update DirectX."
     - `unity` → "UNITY ENGINE: Game engine crash, verify game files."
     - `unreal` o `ue4` → "UNREAL ENGINE: Game engine crash, verify game files."
  4. Conectar botón "Copy Report to Clipboard" usando clipboard nativo de Windows
  5. Formatear output final con traducciones amigables
  6. Ejecutar tests y verificar funcionalidad completa

---

## Compilación con PyInstaller

Una vez completado el desarrollo, usar el siguiente comando para crear el ejecutable:

```bash
pyinstaller --onefile --windowed --name "CrashDetective" --icon=icon.ico crash_finder.py
```

**Notas de compilación:**
- `--onefile`: Crea un único archivo .exe
- `--windowed`: Sin ventana de consola (aplicación GUI pura)
- `--name`: Nombre del ejecutable final
- `--icon`: Icono personalizado (opcional, se puede generar desde el base64 embebido)

**Dependencias a instalar antes de compilar:**
```bash
pip install PySimpleGUI pywin32 pyinstaller
```

---

## Decisiones de Diseño

1. **Icono:** Lupa simple embebida en base64 (modificable posteriormente)
2. **Fuzzy Threshold:** 60% (ajustable si es necesario)
3. **Traducciones:** Extensibles, se pueden agregar más códigos de error
4. **Archivo único:** Todo en `crash_finder.py` para facilitar compilación
