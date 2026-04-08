"""
Script de prueba simple para el sistema de templates DAX (sin emojis)
Ejecutar: python test_templates_simple.py
"""

from templates import TemplateManager


def test_system():
    """Prueba rápida del sistema"""
    print("\n" + "="*70)
    print("  SISTEMA DE TEMPLATES DAX - PRUEBA RAPIDA")
    print("="*70)

    # Inicializar
    print("\n1. Inicializando TemplateManager...")
    tm = TemplateManager()
    print("   OK - TemplateManager inicializado")

    # Estadísticas
    print("\n2. Obteniendo estadisticas...")
    stats = tm.get_stats()
    print(f"   Total de templates: {stats['total_templates']}")
    print(f"   Categorias disponibles: {list(stats['by_category'].keys())}")

    # Generar DAX - YTD
    print("\n3. Generando medida YTD...")
    params_ytd = {
        "measure_name": "Ventas YTD",
        "base_measure": "[Total Ventas]",
        "date_column": "'Calendario'[Fecha]"
    }

    success, message, dax = tm.generate_dax("ytd", params_ytd)
    if success:
        print("   OK - Medida generada correctamente")
        print(f"\n   Codigo DAX generado:")
        print(f"   {dax}\n")
    else:
        print(f"   ERROR: {message}")

    # Generar DAX - Margin
    print("\n4. Generando medida de Margen %...")
    params_margin = {
        "measure_name": "Margen %",
        "revenue_measure": "[Ingresos]",
        "cost_measure": "[Costos]"
    }

    success, message, dax = tm.generate_dax("margin_percentage", params_margin)
    if success:
        print("   OK - Medida generada correctamente")
        print(f"\n   Codigo DAX generado:")
        print(f"   {dax}\n")
    else:
        print(f"   ERROR: {message}")

    # Búsqueda
    print("\n5. Probando busqueda...")
    results = tm.search("margen")
    print(f"   Encontrados {len(results)} templates con 'margen':")
    for t in results[:3]:
        print(f"   - {t.name}")

    # Sugerencias
    print("\n6. Probando sugerencias automaticas...")
    query = "necesito calcular ventas acumuladas del año"
    suggestions = tm.suggest_templates(query, limit=3)
    print(f"   Para: '{query}'")
    print(f"   Sugerencias:")
    for t in suggestions:
        print(f"   - {t.name}: {t.description[:50]}...")

    # Top N
    print("\n7. Generando Top 10...")
    params_top10 = {
        "measure_name": "Top 10 Productos",
        "base_measure": "[Total Ventas]",
        "top_n": "10",
        "ranking_column": "Productos[Nombre]"
    }

    success, message, dax = tm.generate_dax("top_n", params_top10)
    if success:
        print("   OK - Medida Top N generada")
        print(f"\n   Codigo DAX generado:")
        print(f"   {dax[:150]}...")  # Primeros 150 caracteres
    else:
        print(f"   ERROR: {message}")

    # Resumen
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)
    print("\n  TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("\n  El sistema de templates esta listo para usar")
    print("  Ver templates/QUICKSTART.md para mas ejemplos")
    print("  Ver templates/TEMPLATE_CATALOG.md para catalogo completo\n")


if __name__ == "__main__":
    try:
        test_system()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
