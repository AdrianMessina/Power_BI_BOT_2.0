"""
Script de prueba para el sistema de templates DAX
Ejecutar: python test_templates.py
"""

from templates import TemplateManager
from templates.parameter_validator import ParameterValidator


def print_separator(title=""):
    """Imprime separador visual"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)
    else:
        print('-'*70)


def test_basic_functionality():
    """Prueba funcionalidad básica del sistema"""
    print_separator("PRUEBA 1: Inicialización y Estadísticas")

    # Inicializar
    tm = TemplateManager()
    print("✅ TemplateManager inicializado")

    # Estadísticas
    stats = tm.get_stats()
    print(f"\n📊 Estadísticas:")
    print(f"   Total de templates: {stats['total_templates']}")
    print(f"\n📁 Por categoría:")
    for category, count in stats['by_category'].items():
        print(f"   - {category}: {count}")

    print(f"\n🎯 Por dificultad:")
    for difficulty, count in stats['by_difficulty'].items():
        print(f"   - {difficulty}: {count}")

    print(f"\n📅 Requieren tabla de fechas: {stats['requires_date_table']}")


def test_generate_dax():
    """Prueba generación de código DAX"""
    print_separator("PRUEBA 2: Generación de DAX")

    tm = TemplateManager()

    # Ejemplo 1: YTD
    print("\n🔹 Generando medida YTD...")
    params_ytd = {
        "measure_name": "Ventas YTD",
        "base_measure": "[Total Ventas]",
        "date_column": "'Calendario'[Fecha]"
    }

    success, message, dax = tm.generate_dax("ytd", params_ytd)
    print(f"{'✅' if success else '❌'} {message}")
    if success:
        print(f"\n```dax\n{dax}\n```")

    # Ejemplo 2: Margin Percentage
    print("\n🔹 Generando margen porcentual...")
    params_margin = {
        "measure_name": "Margen %",
        "revenue_measure": "[Ingresos]",
        "cost_measure": "[Costos]"
    }

    success, message, dax = tm.generate_dax("margin_percentage", params_margin)
    print(f"{'✅' if success else '❌'} {message}")
    if success:
        print(f"\n```dax\n{dax}\n```")

    # Ejemplo 3: Top 10
    print("\n🔹 Generando Top 10...")
    params_top10 = {
        "measure_name": "Top 10 Productos",
        "base_measure": "[Total Ventas]",
        "top_n": "10",
        "ranking_column": "Productos[Nombre]"
    }

    success, message, dax = tm.generate_dax("top_n", params_top10)
    print(f"{'✅' if success else '❌'} {message}")
    if success:
        print(f"\n```dax\n{dax}\n```")


def test_search():
    """Prueba funcionalidad de búsqueda"""
    print_separator("PRUEBA 3: Búsqueda de Templates")

    tm = TemplateManager()

    # Búsqueda 1: "margen"
    print("\n🔍 Buscando 'margen'...")
    results = tm.search("margen")
    print(f"Encontrados: {len(results)} templates")
    for t in results[:5]:
        print(f"   - {t.name} ({t.category})")

    # Búsqueda 2: "year"
    print("\n🔍 Buscando 'year'...")
    results = tm.search("year")
    print(f"Encontrados: {len(results)} templates")
    for t in results[:5]:
        print(f"   - {t.name} ({t.category})")

    # Búsqueda 3: "ranking"
    print("\n🔍 Buscando 'ranking'...")
    results = tm.search("ranking")
    print(f"Encontrados: {len(results)} templates")
    for t in results[:5]:
        print(f"   - {t.name} ({t.category})")


def test_suggestions():
    """Prueba sistema de sugerencias automáticas"""
    print_separator("PRUEBA 4: Sugerencias Automáticas")

    tm = TemplateManager()

    test_queries = [
        "necesito calcular las ventas acumuladas del año",
        "quiero el promedio ponderado de precios",
        "mostrar top 10 clientes por ventas",
        "calcular el margen de contribución",
        "ventas del año pasado"
    ]

    for query in test_queries:
        print(f"\n💬 Usuario: '{query}'")
        suggestions = tm.suggest_templates(query, limit=3)

        if suggestions:
            print("   Sugerencias:")
            for t in suggestions:
                print(f"   - {t.name} ({t.difficulty})")
        else:
            print("   No se encontraron sugerencias")


def test_categories_and_filters():
    """Prueba filtrado por categoría y dificultad"""
    print_separator("PRUEBA 5: Filtros")

    tm = TemplateManager()

    # Por categoría
    print("\n📁 Templates de Time Intelligence:")
    time_templates = tm.list_by_category("Time Intelligence")
    for t in time_templates[:5]:
        print(f"   - {t.name}")

    # Por dificultad
    print("\n🎯 Templates básicos:")
    basic_templates = tm.list_by_difficulty("basic")
    print(f"   Total: {len(basic_templates)}")
    for t in basic_templates[:5]:
        print(f"   - {t.name}")


def test_template_info():
    """Prueba información detallada de templates"""
    print_separator("PRUEBA 6: Información Detallada")

    tm = TemplateManager()

    # Info de YTD
    print("\n📖 Información de YTD:")
    help_text = tm.get_template_info("ytd")
    print(help_text)


def test_validation():
    """Prueba validación de parámetros"""
    print_separator("PRUEBA 7: Validación de Parámetros")

    validator = ParameterValidator()

    # Test 1: Measure válida
    print("\n✅ Validando medida: [Total Ventas]")
    is_valid, error = validator.validate_parameter(
        "base_measure",
        "[Total Ventas]",
        "measure"
    )
    print(f"   Resultado: {'Válido' if is_valid else f'Error - {error}'}")

    # Test 2: Measure inválida
    print("\n❌ Validando medida: Total Ventas (sin corchetes)")
    is_valid, error = validator.validate_parameter(
        "base_measure",
        "Total Ventas",
        "measure"
    )
    print(f"   Resultado: {'Válido' if is_valid else f'Error - {error}'}")

    # Test 3: Column válida
    print("\n✅ Validando columna: Ventas[Fecha]")
    is_valid, error = validator.validate_parameter(
        "date_column",
        "Ventas[Fecha]",
        "column"
    )
    print(f"   Resultado: {'Válido' if is_valid else f'Error - {error}'}")

    # Test 4: Column inválida
    print("\n❌ Validando columna: [Fecha] (sin tabla)")
    is_valid, error = validator.validate_parameter(
        "date_column",
        "[Fecha]",
        "column"
    )
    print(f"   Resultado: {'Válido' if is_valid else f'Error - {error}'}")


def test_error_handling():
    """Prueba manejo de errores"""
    print_separator("PRUEBA 8: Manejo de Errores")

    tm = TemplateManager()

    # Test 1: Template inexistente
    print("\n❌ Intentando usar template inexistente...")
    success, message, dax = tm.generate_dax("template_que_no_existe", {})
    print(f"   {message}")

    # Test 2: Parámetros faltantes
    print("\n❌ Intentando generar sin parámetros requeridos...")
    success, message, dax = tm.generate_dax("ytd", {
        "measure_name": "Ventas YTD"
        # Faltan base_measure y date_column
    })
    print(f"   {message}")


def test_complete_workflow():
    """Prueba flujo completo de uso"""
    print_separator("PRUEBA 9: Flujo Completo")

    tm = TemplateManager()

    print("\n📝 Simulando flujo completo:")

    # 1. Usuario pide ayuda
    print("\n1️⃣ Usuario: 'necesito calcular ventas del año'")

    # 2. Sistema sugiere templates
    suggestions = tm.suggest_templates("necesito calcular ventas del año")
    print(f"   Sistema sugiere: {suggestions[0].name}")

    # 3. Seleccionar template
    template = suggestions[0]
    print(f"   Template seleccionado: {template.id}")

    # 4. Mostrar parámetros requeridos
    print(f"   Parámetros requeridos:")
    for param in template.parameters:
        req = "✅" if param.required else "⚪"
        print(f"      {req} {param.name}: {param.description}")

    # 5. Usuario completa parámetros
    params = {
        "measure_name": "Ventas YTD",
        "base_measure": "[Total Ventas]",
        "date_column": "'Calendario'[Fecha]"
    }
    print(f"\n   Usuario completa parámetros ✅")

    # 6. Generar DAX
    success, message, dax = tm.generate_dax(template.id, params)
    print(f"\n   {message}")

    # 7. Mostrar preview
    if success:
        print(f"\n   Preview del código:\n")
        print(f"   ```dax\n   {dax}\n   ```")
        print(f"\n   ✅ Usuario confirma → Aplicar al modelo")


def main():
    """Función principal que ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("  SISTEMA DE TEMPLATES DAX - SUITE DE PRUEBAS")
    print("="*70)

    try:
        test_basic_functionality()
        test_generate_dax()
        test_search()
        test_suggestions()
        test_categories_and_filters()
        test_template_info()
        test_validation()
        test_error_handling()
        test_complete_workflow()

        print_separator("RESUMEN")
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\n📚 El sistema de templates está listo para usar")
        print("📖 Ver QUICKSTART.md para ejemplos de uso")
        print("📘 Ver TEMPLATE_CATALOG.md para catálogo completo\n")

    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
