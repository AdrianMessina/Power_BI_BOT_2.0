# Guía Rápida - Templates DAX

## Inicio Rápido (5 minutos)

### 1. Importar el Sistema

```python
from templates import TemplateManager

# Crear instancia
tm = TemplateManager()
```

### 2. Ver Templates Disponibles

```python
# Resumen completo
print(tm.list_templates_summary())

# Estadísticas
stats = tm.get_stats()
print(f"Total: {stats['total_templates']} templates")
print(f"Por categoría: {stats['by_category']}")
```

### 3. Generar Tu Primera Medida DAX

```python
# Parámetros para YTD
params = {
    "measure_name": "Ventas YTD",
    "base_measure": "[Total Ventas]",
    "date_column": "'Calendario'[Fecha]"
}

# Generar código
success, message, dax_code = tm.generate_dax("ytd", params)

if success:
    print("✅", message)
    print(dax_code)
else:
    print("❌", message)
```

**Output:**
```
✅ Medida 'Ventas YTD' generada correctamente
Ventas YTD = CALCULATE([Total Ventas], DATESYTD('Calendario'[Fecha]))
```

---

## Casos de Uso Comunes

### 📊 Medida de Ventas YTD

```python
success, message, dax = tm.generate_dax("ytd", {
    "measure_name": "Ventas YTD",
    "base_measure": "[Total Ventas]",
    "date_column": "'Calendario'[Fecha]"
})
```

### 📈 Crecimiento Año sobre Año

```python
success, message, dax = tm.generate_dax("yoy_growth", {
    "measure_name": "Crecimiento YoY %",
    "base_measure": "[Total Ventas]",
    "date_column": "'Calendario'[Fecha]"
})
```

### 💰 Margen Porcentual

```python
success, message, dax = tm.generate_dax("margin_percentage", {
    "measure_name": "Margen %",
    "revenue_measure": "[Ingresos]",
    "cost_measure": "[Costos]"
})
```

### 🏆 Top 10 Productos

```python
success, message, dax = tm.generate_dax("top_n", {
    "measure_name": "Top 10 Productos",
    "base_measure": "[Total Ventas]",
    "top_n": "10",
    "ranking_column": "Productos[Nombre]"
})
```

### 📊 Clasificación ABC

```python
success, message, dax = tm.generate_dax("abc_classification", {
    "measure_name": "ABC Clientes",
    "base_measure": "[Total Ventas]",
    "item_column": "Clientes[Nombre]"
})
```

---

## Búsqueda Inteligente

### Por Palabra Clave

```python
# Buscar templates relacionados con "año"
results = tm.search("año")

for template in results:
    print(f"- {template.name}: {template.description}")
```

### Por Categoría

```python
# Ver todas las categorías
categories = tm.get_categories()
# ['Advanced', 'Aggregations', 'Calculations', 'Time Intelligence']

# Templates de Time Intelligence
time_templates = tm.list_by_category("Time Intelligence")
```

### Por Dificultad

```python
# Solo templates básicos
basic = tm.list_by_difficulty("basic")

# Templates avanzados
advanced = tm.list_by_difficulty("advanced")
```

### Sugerencias Automáticas

```python
# Sugerir basado en input del usuario
suggestions = tm.suggest_templates(
    "necesito calcular las ventas del mes pasado"
)

# Retorna templates más relevantes (ej: prior_month, mtd, etc.)
```

---

## Validación de Parámetros

```python
from templates.parameter_validator import ParameterValidator

# Crear validador (opcionalmente con datos del modelo)
validator = ParameterValidator(model_data)

# Validar un parámetro
is_valid, error = validator.validate_parameter(
    param_name="base_measure",
    param_value="[Total Ventas]",
    param_type="measure"
)

if not is_valid:
    print(f"Error: {error}")

# Sugerir valores válidos
suggestions = validator.suggest_values(
    param_type="measure",
    query="ventas"
)
# Retorna: ['[Total Ventas]', '[Ventas YTD]', ...]
```

---

## Información de Templates

### Ver Ayuda de un Template

```python
help_text = tm.get_template_info("ytd")
print(help_text)
```

**Output:**
```
**Year to Date (YTD)**
Calcula el acumulado desde el inicio del año hasta la fecha actual

**Categoría:** Time Intelligence
**Dificultad:** basic

**Parámetros:**
- **measure_name** (text): Nombre de la nueva medida [✅ Requerido]
- **base_measure** (measure): Medida base a acumular [✅ Requerido]
- **date_column** (date_column): Columna de fecha [✅ Requerido]

**Ejemplo:**
Ventas YTD =
CALCULATE(
    [Total Ventas],
    DATESYTD('Calendario'[Fecha])
)

⚠️ **Requiere tabla de calendario/fechas**
```

### Listar Parámetros de un Template

```python
template = tm.get_template("ytd")

for param in template.parameters:
    print(f"- {param.name} ({param.type}): {param.description}")
    print(f"  Requerido: {param.required}")
```

---

## Integración con Streamlit

```python
import streamlit as st
from templates import TemplateManager

st.title("Generador de Medidas DAX")

# Inicializar manager
tm = TemplateManager()

# Selector de categoría
category = st.selectbox(
    "Categoría",
    tm.get_categories()
)

# Templates de la categoría
templates = tm.list_by_category(category)
template_options = {t.name: t.id for t in templates}

selected_name = st.selectbox(
    "Tipo de Medida",
    list(template_options.keys())
)

template_id = template_options[selected_name]
template = tm.get_template(template_id)

# Mostrar descripción
st.info(template.description)

# Formulario de parámetros
st.subheader("Parámetros")
params = {}

for param in template.parameters:
    label = f"{param.description}"
    if param.required:
        label += " *"

    params[param.name] = st.text_input(
        label,
        key=param.name,
        help=f"Tipo: {param.type}"
    )

# Generar
if st.button("Generar DAX"):
    success, message, dax_code = tm.generate_dax(template_id, params)

    if success:
        st.success(message)
        st.code(dax_code, language="dax")

        if st.button("✅ Aplicar al Modelo"):
            # Aquí integrar con TOMWrapper
            st.success("Medida creada en el modelo!")
    else:
        st.error(message)
```

---

## Script de Prueba Completo

```python
from templates import TemplateManager

def test_template_system():
    """Prueba el sistema de templates"""
    print("="*60)
    print("PRUEBA DEL SISTEMA DE TEMPLATES DAX")
    print("="*60)

    # Inicializar
    tm = TemplateManager()

    # Estadísticas
    stats = tm.get_stats()
    print(f"\n📊 Total de templates: {stats['total_templates']}")
    print(f"📁 Categorías: {list(stats['by_category'].keys())}")

    # Prueba 1: YTD
    print("\n" + "="*60)
    print("PRUEBA 1: Generar YTD")
    print("="*60)

    params_ytd = {
        "measure_name": "Ventas YTD",
        "base_measure": "[Total Ventas]",
        "date_column": "'Calendario'[Fecha]"
    }

    success, message, dax = tm.generate_dax("ytd", params_ytd)
    print(f"\n{'✅' if success else '❌'} {message}")
    if success:
        print(f"\n{dax}\n")

    # Prueba 2: Búsqueda
    print("="*60)
    print("PRUEBA 2: Búsqueda")
    print("="*60)

    results = tm.search("margen")
    print(f"\nEncontrados {len(results)} templates con 'margen':")
    for t in results:
        print(f"  - {t.name} ({t.category})")

    # Prueba 3: Sugerencias
    print("\n" + "="*60)
    print("PRUEBA 3: Sugerencias Automáticas")
    print("="*60)

    user_query = "quiero ver las ventas acumuladas del año"
    suggestions = tm.suggest_templates(user_query, limit=3)

    print(f"\nPara: '{user_query}'")
    print(f"Sugerencias:")
    for t in suggestions:
        print(f"  - {t.name}: {t.description}")

    print("\n" + "="*60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("="*60)

if __name__ == "__main__":
    test_template_system()
```

---

## Próximos Pasos

### 1. Integrar con UI de Power BI Bot

Agregar selector de templates en [app.py](../app.py):
```python
from templates import TemplateManager

tm = TemplateManager()

# En el chat, detectar solicitud de crear medida
if "crea" in user_input.lower() or "crear" in user_input.lower():
    # Mostrar selector de templates
    suggestions = tm.suggest_templates(user_input)
    # ...
```

### 2. Conectar con TOMWrapper

Para aplicar medidas generadas al modelo:
```python
from core.tom_wrapper import TOMWrapper

# Generar DAX
success, message, dax_code = tm.generate_dax(template_id, params)

if success:
    # Parsear nombre y expresión
    measure_name = params["measure_name"]

    # Aplicar con TOM
    tom = TOMWrapper(connection_string)
    tom.create_measure(
        table_name=target_table,
        measure_name=measure_name,
        expression=dax_code.split("=", 1)[1].strip()
    )
```

### 3. Agregar Más Templates

Extender el catálogo según necesidades:
- Templates específicos de YPF
- Medidas de negocio comunes
- Cálculos de KPIs

---

**¿Dudas?** Ver [TEMPLATE_CATALOG.md](TEMPLATE_CATALOG.md) para documentación completa.
