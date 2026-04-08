# Templates DAX - Sistema Rule-Based

Sistema profesional de generación de medidas DAX sin necesidad de API de IA externa.

## 📁 Estructura

```
templates/
├── __init__.py                    # Exports principales
├── base_template.py               # Clase base para todos los templates
├── template_manager.py            # Gestor central
├── parameter_validator.py         # Validador de parámetros
│
├── time_intelligence.py           # Templates de Time Intelligence (10)
├── aggregations.py                # Templates de Agregaciones (13)
├── calculations.py                # Templates de Cálculos (13)
├── advanced.py                    # Templates Avanzados (10)
│
├── TEMPLATE_CATALOG.md            # Catálogo completo de templates
├── QUICKSTART.md                  # Guía rápida de uso
└── README.md                      # Este archivo
```

## 🚀 Inicio Rápido

### Instalación

No requiere dependencias adicionales. El sistema usa solo Python estándar.

### Uso Básico

```python
from templates import TemplateManager

# Inicializar
tm = TemplateManager()

# Generar una medida YTD
success, message, dax_code = tm.generate_dax("ytd", {
    "measure_name": "Ventas YTD",
    "base_measure": "[Total Ventas]",
    "date_column": "'Calendario'[Fecha]"
})

if success:
    print(dax_code)
    # Output: Ventas YTD = CALCULATE([Total Ventas], DATESYTD('Calendario'[Fecha]))
```

## 📊 Catálogo de Templates

### 50+ Templates Disponibles

| Categoría | Templates | Ejemplos |
|-----------|-----------|----------|
| **Time Intelligence** | 10 | YTD, YoY, MTD, QTD, SPLY, Running Total |
| **Aggregations** | 13 | SUM, AVG, COUNT, DISTINCTCOUNT, SUMX |
| **Calculations** | 13 | Margin %, Variance, Growth Rate, Pareto |
| **Advanced** | 10 | Ranking, Top N, ABC, Dynamic calculations |

Ver [TEMPLATE_CATALOG.md](TEMPLATE_CATALOG.md) para lista completa.

## 🎯 Casos de Uso

### 1. Búsqueda de Templates

```python
# Por palabra clave
templates = tm.search("margen")

# Por categoría
time_templates = tm.list_by_category("Time Intelligence")

# Por dificultad
basic_templates = tm.list_by_difficulty("basic")

# Sugerencias automáticas
suggestions = tm.suggest_templates("necesito calcular ventas acumuladas")
```

### 2. Generación de DAX

```python
# Obtener información del template
help_text = tm.get_template_info("ytd")

# Preparar parámetros
params = {
    "measure_name": "Mi Medida",
    "base_measure": "[Ventas]",
    "date_column": "'Fecha'[Fecha]"
}

# Generar código
success, message, dax = tm.generate_dax("ytd", params)
```

### 3. Validación

```python
from templates.parameter_validator import ParameterValidator

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

## 🧪 Pruebas

Ejecutar suite de pruebas completa:

```bash
cd powerbi-bot
python test_templates.py
```

Esto ejecutará 9 pruebas que validan:
- ✅ Inicialización y estadísticas
- ✅ Generación de DAX
- ✅ Búsqueda de templates
- ✅ Sugerencias automáticas
- ✅ Filtros por categoría/dificultad
- ✅ Información detallada
- ✅ Validación de parámetros
- ✅ Manejo de errores
- ✅ Flujo completo de uso

## 📖 Documentación

### Guías

- **[QUICKSTART.md](QUICKSTART.md)** - Inicio rápido (5 min)
- **[TEMPLATE_CATALOG.md](TEMPLATE_CATALOG.md)** - Catálogo completo con ejemplos

### API Reference

#### TemplateManager

```python
class TemplateManager:
    def get_template(template_id: str) -> DAXTemplate
    def list_all_templates() -> List[DAXTemplate]
    def list_by_category(category: str) -> List[DAXTemplate]
    def list_by_difficulty(difficulty: str) -> List[DAXTemplate]
    def search(query: str) -> List[DAXTemplate]
    def generate_dax(template_id: str, params: Dict) -> Tuple[bool, str, str]
    def suggest_templates(user_input: str, limit: int) -> List[DAXTemplate]
    def get_stats() -> Dict
```

#### DAXTemplate

```python
@dataclass
class DAXTemplate:
    id: str
    name: str
    description: str
    category: str
    difficulty: str
    parameters: List[TemplateParameter]
    dax_template: str
    example: str
    tags: List[str]
    requires_date_table: bool

    def validate_parameters(params: Dict) -> Tuple[bool, str]
    def generate(params: Dict) -> Tuple[str, str]
    def get_help() -> str
```

## 🔧 Extensión

### Agregar Nuevo Template

1. Editar archivo de categoría correspondiente (ej: `time_intelligence.py`)
2. Agregar nuevo `DAXTemplate` a `self.templates`
3. El template estará disponible automáticamente

```python
self.templates.append(DAXTemplate(
    id="my_template",
    name="My Template",
    description="What it does",
    category="Time Intelligence",
    difficulty="intermediate",
    parameters=[...],
    dax_template="""...""",
    example="""...""",
    tags=["tag1", "tag2"],
    requires_date_table=True
))
```

### Crear Nueva Categoría

1. Crear `templates/my_category.py`
2. Heredar de `BaseTemplateCollection`
3. Implementar `_load_templates()`
4. Registrar en `TemplateManager.__init__()`

## 💡 Ventajas del Sistema

✅ **Sin API Externa**
- Funciona offline
- Sin costos por uso
- Sin límites de llamadas

✅ **Predecible**
- Código DAX consistente
- Sintaxis validada
- Resultados confiables

✅ **Rápido**
- Generación instantánea
- Sin latencia de red
- No requiere procesamiento complejo

✅ **Extensible**
- Fácil agregar templates
- Estructura modular
- Documentación automática

✅ **Validado**
- Parámetros verificados
- Formato validado
- Errores claros

## 🔄 Integración con Power BI Bot

### 1. Importar en app.py

```python
from templates import TemplateManager

# En session_state
if 'template_manager' not in st.session_state:
    st.session_state.template_manager = TemplateManager()
```

### 2. Detectar Intención de Crear Medida

```python
def process_message(user_input: str) -> str:
    if any(word in user_input.lower() for word in ["crea", "crear", "nueva medida"]):
        # Sugerir templates
        tm = st.session_state.template_manager
        suggestions = tm.suggest_templates(user_input)

        # Mostrar selector
        return show_template_selector(suggestions)
```

### 3. Formulario de Parámetros

```python
def show_template_form(template_id: str):
    tm = st.session_state.template_manager
    template = tm.get_template(template_id)

    params = {}
    for param in template.parameters:
        params[param.name] = st.text_input(
            param.description,
            key=param.name
        )

    if st.button("Generar"):
        success, message, dax = tm.generate_dax(template_id, params)
        if success:
            st.code(dax, language="dax")
            # Botón para aplicar con TOM
```

### 4. Aplicar al Modelo

```python
from core.tom_wrapper import TOMWrapper

def apply_measure(measure_name: str, dax_expression: str, table_name: str):
    tom = get_tom_wrapper()  # Obtener conexión TOM

    success = tom.create_measure(
        table_name=table_name,
        measure_name=measure_name,
        expression=dax_expression
    )

    if success:
        st.success(f"✅ Medida '{measure_name}' creada!")
```

## 📈 Roadmap

### Versión Actual (1.0)
- ✅ 50+ templates implementados
- ✅ 4 categorías completas
- ✅ Sistema de búsqueda
- ✅ Validación de parámetros
- ✅ Documentación completa

### Próximas Mejoras (1.1)
- ⏳ Templates específicos de YPF
- ⏳ Historial de medidas generadas
- ⏳ Exportar/importar templates custom
- ⏳ Templates condicionales (if modelo tiene X entonces Y)

### Futuro (2.0)
- 🔮 Integración con Claude API (opcional)
  - Generación inteligente cuando esté disponible
  - Templates como fallback
  - Híbrido: AI para casos complejos, templates para casos comunes

## 🤝 Contribuir

Para agregar templates al catálogo:

1. Identificar necesidad/patrón común
2. Crear template en categoría apropiada
3. Incluir ejemplo real
4. Probar con `test_templates.py`
5. Documentar en `TEMPLATE_CATALOG.md`

## 📞 Soporte

Para dudas o sugerencias:
- Ver documentación en `TEMPLATE_CATALOG.md` y `QUICKSTART.md`
- Ejecutar `test_templates.py` para verificar funcionamiento
- Consultar código fuente (bien documentado)

---

**Desarrollado por:** Equipo RTIC - YPF
**Versión:** 1.0
**Fecha:** Marzo 2026
**Licencia:** Uso interno YPF
