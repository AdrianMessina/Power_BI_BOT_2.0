"""
Test rápido del file reader
"""

from core.pbix_file_reader import PBIXFileReader
import sys

if len(sys.argv) < 2:
    print("Uso: python test_file_reader.py <ruta_al_pbix>")
    sys.exit(1)

pbix_path = sys.argv[1]

print(f"Leyendo: {pbix_path}")

reader = PBIXFileReader(pbix_path)
model_data = reader.extract_model()

print(f"\n✓ Modelo extraído")
print(f"  Tablas: {len(model_data.tables)}")
print(f"  Medidas: {len(model_data.measures)}")
print(f"  Relaciones: {len(model_data.relationships)}")

# Mostrar primeras tablas
if model_data.tables:
    print(f"\n📋 Primeras 5 tablas:")
    for table in model_data.tables[:5]:
        print(f"  - {table['name']} ({table['measures_count']} medidas)")

# Mostrar primeras medidas
if model_data.measures:
    print(f"\n📊 Primeras 5 medidas:")
    for measure in model_data.measures[:5]:
        print(f"  - {measure['table']}.{measure['name']}")

print("\n✓ Test completo")
