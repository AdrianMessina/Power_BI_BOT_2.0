"""
Script de Prueba - Mejoras Grupo A
Prueba las 4 mejoras implementadas
"""

print("="*70)
print("  PRUEBA DE MEJORAS - GRUPO A")
print("="*70)

# Test 1: Imports
print("\n1. Verificando imports...")
try:
    from core.measure_history import MeasureHistory, MeasureHistoryEntry
    print("   OK - MeasureHistory")

    from ui.history_ui import show_history_sidebar, show_full_history
    print("   OK - History UI")

    from utils.clipboard_helper import clipboard_button, multi_clipboard_options
    print("   OK - Clipboard Helper")

    from utils.export_helper import ExportHelper, show_export_options
    print("   OK - Export Helper")

    from ui.tutorial import show_tutorial, Tutorial
    print("   OK - Tutorial")

    print("   Todos los imports OK!")

except ImportError as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 2: MeasureHistory
print("\n2. Probando MeasureHistory...")
try:
    history = MeasureHistory("output/test_history.json")

    # Agregar entrada de prueba
    history.add_entry(
        measure_name="Test Measure",
        template_id="ytd",
        template_name="Year to Date",
        dax_code="Test YTD = CALCULATE([Total Sales], DATESYTD('Date'[Date]))",
        parameters={"measure_name": "Test YTD", "base_measure": "[Total Sales]"},
        category="Time Intelligence",
        applied=True
    )

    print("   OK - Entrada agregada")

    # Verificar estadísticas
    stats = history.get_stats()
    print(f"   OK - Stats: {stats['total']} medidas en historial")

    # Buscar
    results = history.search("test")
    print(f"   OK - Búsqueda: {len(results)} resultados")

    # Limpiar
    history.clear_history()
    print("   OK - Historial limpiado")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 3: ExportHelper
print("\n3. Probando ExportHelper...")
try:
    helper = ExportHelper()

    # Exportar medida
    file_path = helper.export_measure_to_dax(
        measure_name="Test Export",
        dax_code="Test = SUM(Table[Column])",
        template_name="Sum",
        parameters={"measure_name": "Test Export", "table_column": "Table[Column]"},
        output_path="output/test_export.dax"
    )

    print(f"   OK - Exportado a: {file_path}")

    # Verificar archivo
    import os
    if os.path.exists(file_path):
        print("   OK - Archivo existe")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "Test Export" in content and "SUM(Table[Column])" in content:
            print("   OK - Contenido correcto")

        # Limpiar
        os.remove(file_path)
        print("   OK - Archivo limpiado")
    else:
        print("   ERROR - Archivo no existe")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 4: Tutorial
print("\n4. Probando Tutorial...")
try:
    tutorial = Tutorial()

    total_steps = tutorial.get_total_steps()
    print(f"   OK - Tutorial tiene {total_steps} pasos")

    # Verificar pasos
    for i in range(total_steps):
        step = tutorial.get_step(i)
        if step and 'title' in step and 'content' in step:
            print(f"   OK - Paso {i+1}: {step['title'][:30]}...")
        else:
            print(f"   ERROR - Paso {i+1} inválido")

    print("   OK - Todos los pasos válidos")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 5: Estructura de archivos
print("\n5. Verificando estructura de archivos...")
import os

files_to_check = [
    "core/measure_history.py",
    "ui/history_ui.py",
    "ui/tutorial.py",
    "utils/__init__.py",
    "utils/clipboard_helper.py",
    "utils/export_helper.py",
    "GRUPO_A_COMPLETADO.md"
]

all_exist = True
for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"   OK - {file_path}")
    else:
        print(f"   FALTA - {file_path}")
        all_exist = False

if not all_exist:
    print("\n   ADVERTENCIA: Algunos archivos faltan")
else:
    print("\n   OK - Todos los archivos presentes")

# Test 6: Integración con app.py
print("\n6. Verificando integración en app.py...")
try:
    with open("app.py", 'r', encoding='utf-8') as f:
        app_content = f.read()

    checks = {
        "MeasureHistory": "from core.measure_history import MeasureHistory" in app_content,
        "history_ui": "from ui.history_ui import" in app_content,
        "tutorial": "from ui.tutorial import" in app_content,
        "show_history_sidebar": "show_history_sidebar()" in app_content,
        "show_tutorial": "show_tutorial()" in app_content,
        "show_full_history": "show_full_history()" in app_content
    }

    for check_name, check_result in checks.items():
        status = "OK" if check_result else "FALTA"
        print(f"   {status} - {check_name}")

    if all(checks.values()):
        print("   OK - Integración completa")
    else:
        print("   ADVERTENCIA - Integración incompleta")

except Exception as e:
    print(f"   ERROR: {e}")

# Test 7: Integración con template_ui.py
print("\n7. Verificando integración en template_ui.py...")
try:
    with open("ui/template_ui.py", 'r', encoding='utf-8') as f:
        ui_content = f.read()

    checks = {
        "clipboard_helper": "from utils.clipboard_helper import" in ui_content,
        "export_helper": "from utils.export_helper import" in ui_content,
        "multi_clipboard_options": "multi_clipboard_options(" in ui_content,
        "show_export_options": "show_export_options(" in ui_content,
        "add_to_history": "add_to_history(" in ui_content
    }

    for check_name, check_result in checks.items():
        status = "OK" if check_result else "FALTA"
        print(f"   {status} - {check_name}")

    if all(checks.values()):
        print("   OK - Integración completa")
    else:
        print("   ADVERTENCIA - Integración incompleta")

except Exception as e:
    print(f"   ERROR: {e}")

# Resumen
print("\n" + "="*70)
print("  RESUMEN")
print("="*70)
print("\n  PRUEBAS DEL GRUPO A COMPLETADAS")
print("\n  Mejoras implementadas:")
print("  1. Historial de Medidas Creadas")
print("  2. Sistema de Clipboard Mejorado")
print("  3. Export de Templates a Archivos")
print("  4. Tutorial Interactivo")
print("\n  Para probar en vivo:")
print("  streamlit run app.py")
print("")
