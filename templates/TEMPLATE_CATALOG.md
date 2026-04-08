# Catálogo de Templates DAX

Sistema rule-based de generación de medidas DAX para Power BI Bot.

## Resumen

**Total de Templates:** 50+

### Por Categoría

- **Time Intelligence:** 10 templates
- **Aggregations:** 13 templates
- **Calculations:** 13 templates
- **Advanced:** 10 templates

### Por Dificultad

- 🟢 **Básico:** 22 templates
- 🟡 **Intermedio:** 18 templates
- 🔴 **Avanzado:** 10 templates

---

## Time Intelligence

### 🟢 Year to Date (YTD)
**ID:** `ytd`

Calcula el acumulado desde el inicio del año hasta la fecha actual.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base a acumular
- `date_column` (date_column): Columna de fecha

**Ejemplo:**
```dax
Ventas YTD =
CALCULATE(
    [Total Ventas],
    DATESYTD('Calendario'[Fecha])
)
```

**Requiere:** 📅 Tabla de fechas

---

### 🟢 Month to Date (MTD)
**ID:** `mtd`

Calcula el acumulado del mes hasta la fecha actual.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base
- `date_column` (date_column): Columna de fecha

**Ejemplo:**
```dax
Ventas MTD =
CALCULATE(
    [Total Ventas],
    DATESMTD('Calendario'[Fecha])
)
```

**Requiere:** 📅 Tabla de fechas

---

### 🟡 Year over Year Growth
**ID:** `yoy_growth`

Calcula el crecimiento porcentual comparado con el año anterior.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base
- `date_column` (date_column): Columna de fecha

**Ejemplo:**
```dax
Crecimiento YoY % =
VAR CurrentValue = [Total Ventas]
VAR PreviousYearValue =
    CALCULATE(
        [Total Ventas],
        SAMEPERIODLASTYEAR('Calendario'[Fecha])
    )
RETURN
    DIVIDE(
        CurrentValue - PreviousYearValue,
        PreviousYearValue
    )
```

**Requiere:** 📅 Tabla de fechas

---

## Aggregations

### 🟢 Sum
**ID:** `sum`

Suma simple de una columna.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `table_column` (column): Tabla y columna (ej: Ventas[Importe])

**Ejemplo:**
```dax
Total Ventas = SUM(Ventas[Importe])
```

---

### 🟢 Average
**ID:** `average`

Calcula el promedio de una columna.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `table_column` (column): Tabla y columna

**Ejemplo:**
```dax
Precio Promedio = AVERAGE(Productos[Precio])
```

---

### 🟢 Distinct Count
**ID:** `distinctcount`

Cuenta el número de valores únicos.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `table_column` (column): Tabla y columna

**Ejemplo:**
```dax
Clientes Únicos = DISTINCTCOUNT(Ventas[ClienteID])
```

---

### 🟡 Weighted Average
**ID:** `weighted_avg`

Calcula un promedio ponderado.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `table` (table): Tabla sobre la que iterar
- `value_column` (column): Columna con valores
- `weight_column` (column): Columna con pesos

**Ejemplo:**
```dax
Precio Promedio Ponderado =
DIVIDE(
    SUMX(Ventas, Ventas[Precio] * Ventas[Cantidad]),
    SUM(Ventas[Cantidad])
)
```

---

## Calculations

### 🟢 Percentage
**ID:** `percentage`

Calcula el porcentaje de una medida sobre otra.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `numerator` (measure): Medida numerador
- `denominator` (measure): Medida denominador

**Ejemplo:**
```dax
Margen % =
DIVIDE(
    [Utilidad],
    [Ventas]
)
```

---

### 🟡 Percentage of Total
**ID:** `percentage_of_total`

Calcula el porcentaje que representa sobre el total.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base

**Ejemplo:**
```dax
% del Total Ventas =
DIVIDE(
    [Total Ventas],
    CALCULATE([Total Ventas], ALL())
)
```

---

### 🟢 Margin Percentage
**ID:** `margin_percentage`

Calcula el margen como porcentaje de los ingresos.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `revenue_measure` (measure): Medida de ingresos
- `cost_measure` (measure): Medida de costos

**Ejemplo:**
```dax
Margen % =
DIVIDE(
    [Total Ventas] - [Total Costos],
    [Total Ventas]
)
```

---

### 🟢 Variance Percentage
**ID:** `variance_percentage`

Calcula la varianza como porcentaje.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `actual_measure` (measure): Medida actual/real
- `target_measure` (measure): Medida objetivo/presupuesto

**Ejemplo:**
```dax
Varianza % =
DIVIDE(
    [Ventas Reales] - [Presupuesto Ventas],
    [Presupuesto Ventas]
)
```

---

## Advanced

### 🟡 Rank
**ID:** `rank`

Asigna un ranking basado en una medida.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `ranking_measure` (measure): Medida a rankear
- `ranking_column` (column): Columna sobre la que rankear

**Ejemplo:**
```dax
Ranking Productos =
RANKX(
    ALL(Productos[Nombre]),
    [Total Ventas],
    ,
    DESC
)
```

---

### 🟡 Top N
**ID:** `top_n`

Muestra solo los Top N elementos por una medida.

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base
- `top_n` (text): Número de elementos (ej: 10)
- `ranking_column` (column): Columna sobre la que rankear

**Ejemplo:**
```dax
Top 10 Ventas =
IF(
    RANKX(
        ALL(Productos[Nombre]),
        [Total Ventas],
        ,
        DESC
    ) <= 10,
    [Total Ventas],
    BLANK()
)
```

---

### 🔴 ABC Classification
**ID:** `abc_classification`

Clasifica elementos en categorías A (top 80%), B (siguiente 15%), C (último 5%).

**Parámetros:**
- `measure_name` (text): Nombre de la nueva medida
- `base_measure` (measure): Medida base para clasificar
- `item_column` (column): Columna de items a clasificar

**Ejemplo:**
```dax
Clasificación ABC Productos =
VAR CurrentTotal = ...
VAR GrandTotal = ...
VAR CumulativePercentage = DIVIDE(CurrentTotal, GrandTotal)
RETURN
    SWITCH(
        TRUE(),
        CumulativePercentage <= 0.80, "A",
        CumulativePercentage <= 0.95, "B",
        "C"
    )
```

---

## Uso del Sistema

### 1. Importar TemplateManager

```python
from templates import TemplateManager

# Inicializar
tm = TemplateManager()
```

### 2. Buscar Templates

```python
# Buscar por keyword
templates = tm.search("año anterior")

# Por categoría
time_templates = tm.list_by_category("Time Intelligence")

# Por dificultad
basic_templates = tm.list_by_difficulty("basic")

# Sugerir automáticamente
suggestions = tm.suggest_templates("necesito calcular ventas acumuladas del año")
```

### 3. Generar DAX

```python
# Obtener template
template = tm.get_template("ytd")

# Parámetros
params = {
    "measure_name": "Ventas YTD",
    "base_measure": "[Total Ventas]",
    "date_column": "'Calendario'[Fecha]"
}

# Generar código
success, message, dax_code = tm.generate_dax("ytd", params)

if success:
    print(dax_code)
    # Output: Ventas YTD = CALCULATE([Total Ventas], DATESYTD('Calendario'[Fecha]))
```

### 4. Validar Parámetros

```python
from templates.parameter_validator import ParameterValidator

# Crear validador con datos del modelo
validator = ParameterValidator(model_data)

# Validar parámetro
is_valid, error = validator.validate_parameter(
    "base_measure",
    "[Total Ventas]",
    "measure"
)

# Sugerir valores
suggestions = validator.suggest_values("measure", query="ventas")
```

### 5. Ver Información de Template

```python
# Ayuda detallada
help_text = tm.get_template_info("ytd")
print(help_text)

# Estadísticas del catálogo
stats = tm.get_stats()
print(f"Total templates: {stats['total_templates']}")
```

---

## Integración con Power BI Bot

### Flujo Conversacional

```
Usuario: "Necesito calcular las ventas acumuladas del año"

Bot:
1. Detecta intención → tm.suggest_templates(user_input)
2. Encuentra template "ytd"
3. Solicita parámetros faltantes:
   - ¿En qué tabla creo la medida?
   - ¿Cuál es la medida base? (sugiere: [Total Ventas])
   - ¿Cuál es la columna de fecha? (sugiere: 'Calendario'[Fecha])

4. Usuario completa parámetros

5. Genera y muestra preview:
   ```dax
   Ventas YTD = CALCULATE([Total Ventas], DATESYTD('Calendario'[Fecha]))
   ```

6. Usuario confirma → Aplica al modelo
```

### Ejemplo de Interfaz UI

```python
import streamlit as st
from templates import TemplateManager

tm = TemplateManager()

# Selector de template
template_id = st.selectbox(
    "Selecciona tipo de medida",
    options=[t.id for t in tm.list_all_templates()],
    format_func=lambda x: tm.get_template(x).name
)

# Formulario de parámetros
template = tm.get_template(template_id)
params = {}

for param in template.parameters:
    params[param.name] = st.text_input(
        f"{param.description} ({param.type})",
        help=format_parameter_help(param.type)
    )

# Generar y mostrar
if st.button("Generar DAX"):
    success, message, dax_code = tm.generate_dax(template_id, params)

    if success:
        st.code(dax_code, language="dax")
        if st.button("✅ Aplicar al modelo"):
            # Aplicar usando TOM
            pass
```

---

## Extensión del Catálogo

### Agregar Nuevo Template

```python
# En el archivo correspondiente (ej: time_intelligence.py)

self.templates.append(DAXTemplate(
    id="my_custom_template",
    name="My Custom Template",
    description="Descripción de lo que hace",
    category="Time Intelligence",
    difficulty="intermediate",
    parameters=[
        TemplateParameter(
            name="param1",
            description="Descripción del parámetro",
            type="measure",
            required=True
        )
    ],
    dax_template="""{measure_name} =
CALCULATE(
    [{param1}],
    ...
)""",
    example="""...""",
    tags=["tag1", "tag2"],
    requires_date_table=True
))
```

### Agregar Nueva Categoría

1. Crear archivo `templates/my_category.py`
2. Heredar de `BaseTemplateCollection`
3. Implementar `_load_templates()`
4. Registrar en `TemplateManager.__init__()`

---

## Ventajas del Sistema

✅ **Sin API externa:** Funciona offline, sin costos
✅ **Predecible:** Código DAX consistente y correcto
✅ **Rápido:** Generación instantánea
✅ **Extensible:** Fácil agregar nuevos templates
✅ **Validado:** Parámetros verificados antes de generar
✅ **Documentado:** Cada template incluye ayuda y ejemplos

---

## Limitaciones

⚠️ **No entiende lenguaje natural complejo:** Requiere selección de template
⚠️ **Código fijo:** No optimiza según contexto específico
⚠️ **Sin razonamiento:** No sugiere mejoras automáticas

**Solución futura:** Integrar con Claude API para análisis inteligente mientras se mantienen los templates como fallback.

---

**Versión:** 1.0
**Fecha:** Marzo 2026
**Mantenido por:** Equipo RTIC - YPF
