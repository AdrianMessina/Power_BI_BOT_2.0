"""
Script de Prueba - Mejoras Grupo B
Prueba las 3 mejoras implementadas
"""

print("="*70)
print("  PRUEBA DE MEJORAS - GRUPO B")
print("="*70)

# Test 1: Imports
print("\n1. Verificando imports...")
try:
    from ui.advanced_search import AdvancedTemplateSearch, show_advanced_search, show_quick_search
    print("   OK - Advanced Search")

    from ui.enhanced_validation import EnhancedParameterValidator, show_parameter_form_enhanced
    print("   OK - Enhanced Validation")

    from templates.ypf_business import YPFBusinessTemplates
    print("   OK - YPF Business Templates")

    from templates import TemplateManager
    print("   OK - Template Manager")

    print("   Todos los imports OK!")

except ImportError as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 2: Templates YPF
print("\n2. Probando Templates YPF...")
try:
    tm = TemplateManager()

    # Verificar que se cargaron los templates YPF
    all_templates = tm.list_all_templates()
    ypf_templates = [t for t in all_templates if t.category == 'YPF Business']

    print(f"   OK - {len(ypf_templates)} templates YPF cargados")

    if len(ypf_templates) < 15:
        print(f"   ADVERTENCIA - Se esperaban 15 templates, se encontraron {len(ypf_templates)}")

    # Verificar algunos templates específicos
    expected_templates = [
        'ypf_volumen_total',
        'ypf_precio_promedio',
        'ypf_margen_contribucion',
        'ypf_ticket_promedio',
        'ypf_top_estaciones'
    ]

    for template_id in expected_templates:
        template = tm.get_template(template_id)
        if template:
            print(f"   OK - Template '{template.name}' encontrado")
        else:
            print(f"   ERROR - Template '{template_id}' no encontrado")

    # Generar medida de prueba
    success, message, dax_code = tm.generate_dax(
        'ypf_volumen_total',
        {
            'measure_name': 'Volumen Test',
            'volumen_column': 'Ventas[Litros]'
        }
    )

    if success:
        print("   OK - Generación de DAX exitosa")
        print(f"   Preview: {dax_code[:50]}...")
    else:
        print(f"   ERROR - {message}")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 3: Búsqueda Avanzada
print("\n3. Probando AdvancedTemplateSearch...")
try:
    tm = TemplateManager()
    search = AdvancedTemplateSearch(tm)

    # Verificar que se puede crear la instancia
    print("   OK - AdvancedTemplateSearch creado")

    # Probar métodos de filtrado
    all_templates = tm.list_all_templates()
    print(f"   OK - {len(all_templates)} templates totales")

    # Buscar por texto
    results = tm.search("volumen")
    print(f"   OK - Búsqueda 'volumen': {len(results)} resultados")

    # Filtrar por categoría
    ypf_category = tm.list_by_category('YPF Business')
    print(f"   OK - Categoría 'YPF Business': {len(ypf_category)} templates")

    # Filtrar por dificultad
    basic_templates = tm.list_by_difficulty('basic')
    print(f"   OK - Dificultad 'basic': {len(basic_templates)} templates")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 4: Validación Mejorada
print("\n4. Probando EnhancedParameterValidator...")
try:
    # Sin modelo
    validator = EnhancedParameterValidator(model_data=None)
    print("   OK - Validator creado (sin modelo)")

    # Validar medida
    is_valid, error = validator.validator.validate_parameter(
        'test_measure',
        '[Total Ventas]',
        'measure'
    )
    if is_valid:
        print("   OK - Validación de medida: formato correcto")
    else:
        print(f"   ERROR - {error}")

    # Validar columna
    is_valid, error = validator.validator.validate_parameter(
        'test_column',
        'Ventas[Fecha]',
        'column'
    )
    if is_valid:
        print("   OK - Validación de columna: formato correcto")
    else:
        print(f"   ERROR - {error}")

    # Validar formato incorrecto
    is_valid, error = validator.validator.validate_parameter(
        'test_measure',
        'Medida Sin Corchetes',
        'measure'
    )
    if not is_valid:
        print("   OK - Validación detecta formato incorrecto")
    else:
        print("   ERROR - No detectó formato incorrecto")

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 5: Estructura de archivos
print("\n5. Verificando estructura de archivos...")
import os

files_to_check = [
    "templates/ypf_business.py",
    "ui/advanced_search.py",
    "ui/enhanced_validation.py"
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

# Test 6: Integración con template_manager.py
print("\n6. Verificando integración en template_manager.py...")
try:
    with open("templates/template_manager.py", 'r', encoding='utf-8') as f:
        manager_content = f.read()

    checks = {
        "YPFBusinessTemplates import": "from .ypf_business import YPFBusinessTemplates" in manager_content,
        "YPF collection": "'ypf_business': YPFBusinessTemplates()" in manager_content
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
        ui_content = f.read()

    checks = {
        "advanced_search import": "from ui.advanced_search import" in ui_content,
        "enhanced_validation import": "from ui.enhanced_validation import" in ui_content,
        "show_advanced_search": "show_advanced_search()" in ui_content,
        "show_parameter_form_enhanced": "show_parameter_form_enhanced" in ui_content,
        "use_advanced checkbox": "use_advanced" in ui_content,
        "use_enhanced checkbox": "use_enhanced" in ui_content
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
        "quick_search import": "from ui.advanced_search import show_quick_search" in app_content,
        "show_quick_search call": "show_quick_search(" in app_content,
        "Búsqueda Rápida header": "Búsqueda Rápida" in app_content
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

# Test 9: Estadísticas del catálogo
print("\n9. Verificando estadísticas del catálogo...")
try:
    tm = TemplateManager()
    stats = tm.get_stats()

    print(f"   Total templates: {stats['total_templates']}")
    print(f"   Categorías:")
    for category, count in stats['by_category'].items():
        print(f"      - {category}: {count}")

    print(f"   Por dificultad:")
    for difficulty, count in stats['by_difficulty'].items():
        print(f"      - {difficulty}: {count}")

    print(f"   Requieren tabla de fechas: {stats['requires_date_table']}")

    # Verificar que tenemos más templates que antes
    if stats['total_templates'] >= 61:  # 46 originales + 15 YPF
        print(f"   OK - Catálogo expandido ({stats['total_templates']} templates)")
    else:
        print(f"   ADVERTENCIA - Esperábamos al menos 61 templates, tenemos {stats['total_templates']}")

except Exception as e:
    print(f"   ERROR: {e}")

# Resumen
print("\n" + "="*70)
print("  RESUMEN")
print("="*70)
print("\n  PRUEBAS DEL GRUPO B COMPLETADAS")
print("\n  Mejoras implementadas:")
print("  1. Búsqueda Avanzada de Templates")
print("  2. Validación Mejorada con Feedback Visual")
print("  3. Templates Personalizados YPF (15 templates)")
print("\n  Para probar en vivo:")
print("  streamlit run app.py")
print("")
