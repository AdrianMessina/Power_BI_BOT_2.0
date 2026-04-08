# Power BI Bot - Asistente BI Conversacional

Bot conversacional que se integra con Power BI Desktop para crear medidas DAX, renombrar elementos, optimizar código y consultar el modelo mediante chat en lenguaje natural.

## 🎯 Concepto

Una aplicación de chat que funciona como **compañero de Power BI Desktop**:

1. El usuario abre su archivo `.pbix` en Power BI Desktop
2. Ejecuta la aplicación Power BI Bot
3. La app se conecta automáticamente al modelo en memoria vía XMLA
4. El usuario conversa con el bot para modificar el modelo
5. Los cambios se reflejan **inmediatamente** en Power BI Desktop

### ¿Por qué este enfoque?

✅ **Cambios en tiempo real** - Las modificaciones aparecen instantáneamente
✅ **Reversible** - Ctrl+Z deshace cualquier cambio
✅ **Sin archivos temporales** - Todo en memoria
✅ **API oficial** - Usa XMLA/TOM de Microsoft
✅ **Más confiable** - No manipula archivos binarios directamente

## ✨ Características

### Consultas sobre el Modelo
```
Usuario: "¿Qué medidas usan la tabla Ventas?"
Bot: "Encontré 12 medidas que referencian la tabla Ventas: Total Ventas, Ventas YTD, ..."

Usuario: "¿Cuántas relaciones tiene el modelo?"
Bot: "Tu modelo tiene 15 relaciones activas y 2 inactivas."
```

### Creación de Medidas DAX
```
Usuario: "Crea una medida de ventas del año pasado"
Bot: "¿En qué tabla la creo?"
Usuario: "En la tabla _Medidas"
Bot: "✓ Creada medida 'Ventas Año Pasado' con:
     Ventas Año Pasado = CALCULATE([Total Ventas], SAMEPERIODLASTYEAR('Calendario'[Fecha]))"
```

### Renombrado Inteligente
```
Usuario: "Renombra la medida TotalSales a 'Total de Ventas'"
Bot: "Renombraré 'TotalSales' → 'Total de Ventas' y actualizaré 3 referencias. ¿Confirmas?"
```

### Optimización de DAX
```
Usuario: "Optimiza la medida Top10Products"
Bot: "Detecté 2 oportunidades: 1) Usar variables 2) TOPN en lugar de RANKX + FILTER"
```

## 🏗️ Arquitectura

### Modo de Operación: External Tool

```
┌─────────────────────┐
│  Power BI Desktop   │
│   (archivo.pbix)    │
│  XMLA Endpoint      │◄──────┐
│  localhost:xxxxx    │       │ XMLA/TOM Connection
└─────────────────────┘       │
                              │
┌─────────────────────────────┴──────┐
│     Power BI Bot App               │
│   ┌──────────────────────────┐     │
│   │   Streamlit Chat UI      │     │
│   └───────────┬──────────────┘     │
│               │                    │
│   ┌───────────▼──────────────┐     │
│   │   Claude Client (MCP)    │     │
│   └───────────┬──────────────┘     │
│               │                    │
│   ┌───────────▼──────────────┐     │
│   │  XMLA Connector + TOM    │     │
│   │  - Query Model           │     │
│   │  - Create Measures       │     │
│   │  - Rename Elements       │     │
│   └──────────────────────────┘     │
└────────────────────────────────────┘
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.10+
- Power BI Desktop instalado
- Claude API Key
- Red corporativa YPF (para instalación)

### Pasos

```bash
# 1. Clonar/descargar el proyecto
cd powerbi-bot

# 2. Configurar proxy (red YPF)
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure

# 3. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar Claude API Key
echo "ANTHROPIC_API_KEY=tu-api-key-aqui" > .env
```

## 💻 Uso

### 1. Abrir Power BI Desktop

Abre tu archivo `.pbix` en Power BI Desktop normalmente.

### 2. Ejecutar Power BI Bot

```bash
streamlit run app.py
```

Se abrirá en tu navegador (http://localhost:8501).

### 3. Conectar al Modelo

La aplicación detectará automáticamente el puerto XMLA de Power BI Desktop.

Verás en el panel lateral:
- ✅ Estado de conexión
- 📊 Nombre del modelo
- 📈 Tablas, medidas, relaciones

### 4. Conversar con el Bot

**Consultas:**
- "¿Qué medidas tengo?"
- "¿Qué tablas están relacionadas con Ventas?"
- "Muéstrame todas las medidas que usan CALCULATE"

**Creación:**
- "Crea una medida de ventas del mes pasado"
- "Necesito una medida que calcule el promedio de precio"

**Renombrado:**
- "Renombra la tabla tbl_ventas a Ventas"

**Optimización:**
- "Optimiza la medida TopProducts"
- "Analiza el rendimiento de las medidas de Ventas"

## 📁 Estructura del Proyecto

```
powerbi-bot/
├── app.py                          # Interfaz Streamlit principal
├── requirements.txt                # Dependencias Python
├── .env                            # API keys
│
├── core/                           # Lógica de negocio
│   ├── xmla_connector.py           # Conexión XMLA a Power BI Desktop
│   ├── tom_wrapper.py              # Wrapper TOM (.NET via pythonnet)
│   └── model_context.py            # Contexto del modelo para Claude
│
├── mcp_server/                     # Servidor MCP
│   ├── powerbi_bot_server.py       # Servidor MCP principal
│   └── tools/                      # Herramientas MCP
│       ├── query_tools.py          # Consultas sobre el modelo
│       ├── dax_tools.py            # Crear/modificar DAX
│       ├── rename_tools.py         # Renombrar elementos
│       └── optimize_tools.py       # Optimizar DAX
│
├── ai/                             # Integración con Claude
│   ├── claude_client.py            # Cliente Claude API
│   └── prompt_templates.py         # Templates de prompts
│
├── config/                         # Configuración
│   └── settings.yaml
│
├── tests/                          # Tests
├── output/                         # Archivos generados
└── logs/                           # Logs
```

## 🔐 Seguridad

- ✅ **No modifica el archivo .pbix directamente**: todos los cambios son en memoria
- ✅ **Requiere confirmación**: antes de aplicar cambios críticos
- ✅ **Reversible**: Ctrl+Z en Power BI Desktop deshace cualquier cambio
- ✅ **Logs detallados**: todas las operaciones se registran

## 🛠️ Desarrollo

### XMLA Connector (`core/xmla_connector.py`)

```python
class XMLAConnector:
    def connect_to_local() -> Connection
        """Detecta y conecta al puerto XMLA de Power BI Desktop"""

    def get_model_metadata() -> ModelMetadata
        """Extrae metadata del modelo"""

    def execute_tmsl(script: str) -> None
        """Ejecuta script TMSL para modificar el modelo"""
```

### TOM Wrapper (`core/tom_wrapper.py`)

```python
class TOMWrapper:
    def create_measure(table: str, name: str, expression: str)
    def rename_measure(old_name: str, new_name: str)
    def find_dependencies(measure_name: str) -> List[str]
    def validate_dax(expression: str) -> ValidationResult
```

### Herramientas MCP (`mcp_server/tools/`)

- `query_model_structure()`: Info sobre tablas, medidas, relaciones
- `create_dax_measure()`: Crear medida
- `rename_element()`: Renombrar
- `suggest_optimizations()`: Sugerencias

## 🧪 Testing

```bash
pytest tests/

# Con modelo de ejemplo
pytest tests/test_integration.py
```

## 🚧 Limitaciones

1. **Requiere Power BI Desktop abierto**: no puede modificar archivos cerrados
2. **XMLA debe estar habilitado**: viene por defecto en versiones modernas
3. **Modelos grandes**: >1GB pueden ser lentos

## 🗺️ Roadmap

### MVP (Actual)
- [x] Conexión XMLA
- [x] Consultas sobre modelo
- [ ] Crear medidas DAX
- [ ] Chat conversacional

### v1.0
- [ ] Renombrado con actualización de referencias
- [ ] Optimización de DAX
- [ ] Validación de sintaxis DAX

### v2.0
- [ ] Análisis de performance
- [ ] Generación de documentación
- [ ] Integración como External Tool oficial

## 📝 Licencia

Uso interno - YPF

## 📧 Soporte

Para reportar bugs o solicitar funcionalidades, contactar al equipo RTIC.

---

**Desarrollado por:** Equipo RTIC - YPF
**Versión:** 0.1.0-MVP
**Fecha:** Marzo 2026
