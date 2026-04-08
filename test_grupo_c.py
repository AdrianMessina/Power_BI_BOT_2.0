"""
Script de Prueba - Mejoras Grupo C
Prueba las 4 mejoras técnicas implementadas
"""

print("="*70)
print("  PRUEBA DE MEJORAS - GRUPO C")
print("="*70)

# Test 1: Imports
print("\n1. Verificando imports...")
try:
    from core.dax_analyzer import DAXAnalyzer, DAXAnalysis
    print("   OK - DAX Analyzer")

    from ui.enriched_preview import EnrichedPreview, show_enriched_preview_ui
    print("   OK - Enriched Preview")

    from core.custom_templates import CustomTemplateManager
    print("   OK - Custom Templates Manager")

    from ui.custom_template_ui import show_custom_template_manager
    print("   OK - Custom Template UI")

    from core.favorites import FavoritesManager
    print("   OK - Favorites Manager")

    from ui.favorites_ui import show_favorites_sidebar, show_favorite_button
    print("   OK - Favorites UI")

    print("   Todos los imports OK!")

except ImportError as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 2: DAX Analyzer
print("\n2. Probando DAX Analyzer...")
try:
    analyzer = DAXAnalyzer()

    # Analizar código simple
    simple_code = "Total Ventas = SUM(Ventas[Importe])"
    analysis = analyzer.analyze(simple_code)

    print(f"   OK - Análisis completado")
    print(f"   Complejidad: {analysis.complexity_level} ({analysis.complexity_score}/100)")
    print(f"   Funciones: {len(analysis.functions_used)}")
    print(f"   Performance: {analysis.estimated_performance}")

    # Analizar código complejo
    complex_code = """
    YTD Sales =
    VAR CurrentDate = MAX(Calendar[Date])
    VAR YTDDates = DATESYTD(Calendar[Date])
    RETURN
    CALCULATE(
        SUM(Sales[Amount]),
        YTDDates,
        FILTER(Products, Products[Category] = "A")
    )
    """

    complex_analysis = analyzer.analyze(complex_code)
    print(f"   OK - Análisis complejo completado")
    print(f"   Complejidad: {complex_analysis.complexity_level} ({complex_analysis.complexity_score}/100)")
    print(f"   Variables: {'Sí' if complex_analysis.has_variables else 'No'}")
    print(f"   Time Intelligence: {'Sí' if complex_analysis.has_time_intelligence else 'No'}")

    # Categorización de funciones
    if complex_analysis.functions_used:
        categories = analyzer.get_function_categories(complex_analysis.functions_used)
        print(f"   OK - Funciones categorizadas: {len(categories)} categorías")

    # Explicación
    explanation = analyzer.explain_measure(complex_analysis, "YTD Sales")
    print(f"   OK - Explicación generada: {explanation[:60]}...")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Custom Templates Manager
print("\n3. Probando Custom Templates Manager...")
try:
    import os
    import tempfile

    # Crear manager con archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    manager = CustomTemplateManager(storage_path=tmp_path)

    print("   OK - Manager creado")

    # Crear template
    success = manager.create_template(
        template_id='test_custom',
        name='Test Custom Template',
        description='Template de prueba',
        category='Custom Templates',
        template_code='{measure_name} = {expression}',
        parameters=[
            {'name': 'measure_name', 'type': 'text', 'description': 'Nombre', 'required': True},
            {'name': 'expression', 'type': 'text', 'description': 'Expresión', 'required': True}
        ],
        author='Test User'
    )

    if success:
        print("   OK - Template creado")
    else:
        print("   ERROR - No se pudo crear template")

    # Verificar
    template = manager.get_template('test_custom')
    if template:
        print(f"   OK - Template recuperado: {template['name']}")
    else:
        print("   ERROR - Template no encontrado")

    # Estadísticas
    stats = manager.get_stats()
    print(f"   OK - Stats: {stats['total']} template(s)")

    # Exportar
    export_path = tmp_path.replace('.json', '_export.json')
    if manager.export_template('test_custom', export_path):
        print(f"   OK - Template exportado")
        os.unlink(export_path)

    # Limpiar
    os.unlink(tmp_path)
    print("   OK - Limpieza completada")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Favorites Manager
print("\n4. Probando Favorites Manager...")
try:
    import os
    import tempfile

    # Crear manager con archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    fav_manager = FavoritesManager(storage_path=tmp_path)

    print("   OK - Favorites Manager creado")

    # Agregar favoritos
    fav_manager.add_favorite('template_1', 'Template One')
    fav_manager.add_favorite('template_2', 'Template Two')
    print("   OK - Favoritos agregados")

    # Verificar
    if fav_manager.is_favorite('template_1'):
        print("   OK - Favorito verificado")
    else:
        print("   ERROR - Favorito no encontrado")

    # Contar
    count = fav_manager.get_favorites_count()
    print(f"   OK - Total favoritos: {count}")

    # Incrementar acceso
    fav_manager.increment_access('template_1')
    fav_manager.increment_access('template_1')
    print("   OK - Contador de acceso incrementado")

    # Más accedidos
    most_accessed = fav_manager.get_most_accessed(limit=5)
    print(f"   OK - Más accedidos: {len(most_accessed)} resultado(s)")

    # Stats
    stats = fav_manager.get_stats()
    print(f"   OK - Stats: {stats['total']} favorito(s), {stats['total_access']} accesos")

    # Toggle
    was_favorite = fav_manager.toggle_favorite('template_1')
    print(f"   OK - Toggle ejecutado: {'Removido' if not was_favorite else 'Agregado'}")

    # Limpiar
    os.unlink(tmp_path)
    print("   OK - Limpieza completada")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Estructura de archivos
print("\n5. Verificando estructura de archivos...")
import os

files_to_check = [
    "core/dax_analyzer.py",
    "ui/enriched_preview.py",
    "core/custom_templates.py",
    "ui/custom_template_ui.py",
    "core/favorites.py",
    "ui/favorites_ui.py"
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

# Test 6: Integración con ui/__init__.py
print("\n6. Verificando integración en ui/__init__.py...")
try:
    with open("ui/__init__.py", 'r', encoding='utf-8') as f:
        ui_init_content = f.read()

    checks = {
        "enriched_preview import": "from .enriched_preview import" in ui_init_content,
        "custom_template_ui import": "from .custom_template_ui import" in ui_init_content,
        "favorites_ui import": "from .favorites_ui import" in ui_init_content,
        "EnrichedPreview export": "'EnrichedPreview'" in ui_init_content,
        "show_custom_template_manager export": "'show_custom_template_manager'" in ui_init_content,
        "show_favorites_sidebar export": "'show_favorites_sidebar'" in ui_init_content
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

# Test 7: Integración en template_ui.py
print("\n7. Verificando integración en template_ui.py...")
try:
    with open("ui/template_ui.py", 'r', encoding='utf-8') as f:
        template_ui_content = f.read()

    checks = {
        "enriched_preview import": "from ui.enriched_preview import" in template_ui_content,
        "favorites_ui import": "from ui.favorites_ui import" in template_ui_content,
        "show_enriched_preview_ui": "show_enriched_preview_ui" in template_ui_content,
        "show_quick_analysis": "show_quick_analysis" in template_ui_content,
        "show_favorite_button": "show_favorite_button" in template_ui_content,
        "preview_mode toggle": "preview_mode" in template_ui_content
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

# Test 8: Integración en app.py
print("\n8. Verificando integración en app.py...")
try:
    with open("app.py", 'r', encoding='utf-8') as f:
        app_content = f.read()

    checks = {
        "custom_template_ui import": "from ui.custom_template_ui import" in app_content,
        "favorites_ui import": "from ui.favorites_ui import" in app_content,
        "show_favorites_sidebar call": "show_favorites_sidebar()" in app_content,
        "show_custom_template_quick_access call": "show_custom_template_quick_access()" in app_content,
        "Templates Personalizados button": "Templates Personalizados" in app_content,
        "Gestionar Favoritos button": "Gestionar Favoritos" in app_content,
        "show_custom_templates view": "show_custom_templates" in app_content,
        "show_favorites view": "show_favorites" in app_content,
        "version 0.4.0": "0.4.0" in app_content
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
print("\n  PRUEBAS DEL GRUPO C COMPLETADAS")
print("\n  Mejoras implementadas:")
print("  1. Preview Enriquecido con Análisis DAX")
print("  2. Gestión de Templates Personalizados")
print("  3. Import/Export de Templates JSON")
print("  4. Sistema de Favoritos")
print("\n  Para probar en vivo:")
print("  streamlit run app.py")
print("")
