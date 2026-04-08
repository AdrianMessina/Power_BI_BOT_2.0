"""
Power BI Bot - Asistente Conversacional
Interfaz Streamlit principal - v2.0
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio actual esté en el PYTHONPATH
current_dir = str(Path(__file__).resolve().parent)
sys.path = [p for p in sys.path if not (p.endswith('.py') or p.endswith('.exe'))]
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
os.chdir(current_dir)

import importlib
for _pkg in ['core', 'templates', 'ui', 'utils']:
    try:
        importlib.import_module(_pkg)
    except Exception:
        pass

import streamlit as st
from datetime import datetime
from core.xmla_connector import XMLAConnector
from core.pbix_file_reader import PBIXFileReader
from core.measure_history import MeasureHistory
from templates import TemplateManager
from ui.template_ui import show_template_workflow
from ui.history_ui import show_history_sidebar, show_full_history
from ui.tutorial import show_tutorial, show_tutorial_button, show_first_time_welcome
from ui.advanced_search import show_quick_search
from ui.custom_template_ui import show_custom_template_manager, show_custom_template_quick_access
from ui.favorites_ui import show_favorites_sidebar, show_favorites_manager
from loguru import logger
from core.adomd_query import AdomdQueryEngine, ADOMD_AVAILABLE
import tempfile
import re

# ── Configuracion de pagina ──
st.set_page_config(
    page_title="Power BI Bot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS profesional: Data-Dense Dashboard ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600&display=swap');

    /* Tipografia general */
    .stApp, .stMarkdown, .stText {
        font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header compacto */
    .app-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E293B;
        padding: 0.3rem 0;
        border-bottom: 2px solid #3B82F6;
        margin-bottom: 0.5rem;
    }

    /* KPI cards */
    .kpi-row {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }
    .kpi-card {
        flex: 1;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.6rem 0.8rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #3B82F6;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.7rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-connected {
        background: #DCFCE7;
        color: #166534;
    }
    .status-disconnected {
        background: #FEE2E2;
        color: #991B1B;
    }

    /* Sidebar mas limpio */
    section[data-testid="stSidebar"] {
        background: #F8FAFC;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1rem;
        font-weight: 600;
        color: #1E293B;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
    }

    /* Reducir padding del main content - chat mas arriba */
    .stMainBlockContainer {
        padding-top: 0.3rem;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }
    header[data-testid="stHeader"] {
        height: 2rem;
    }

    /* Tabla de datos */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .data-table th {
        background: #F1F5F9;
        padding: 0.4rem 0.6rem;
        text-align: left;
        font-weight: 600;
        color: #475569;
        border-bottom: 2px solid #E2E8F0;
    }
    .data-table td {
        padding: 0.35rem 0.6rem;
        border-bottom: 1px solid #F1F5F9;
        color: #1E293B;
    }
    .data-table tr:hover td {
        background: #EFF6FF;
    }

    /* Chat input siempre visible */
    .stChatInput {
        position: sticky;
        bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ──
def init_state():
    defaults = {
        'chat_history': [],
        'connector': None,
        'is_connected': False,
        'file_reader': None,
        'model_data': None,
        'mode': None,
        'template_manager': TemplateManager(),
        'show_template_ui': False,
        'measure_history': MeasureHistory(),
        'show_tutorial': False,
        'show_full_history': False,
        # ADOMD query engine
        'adomd': None,
        # Cache DMV metadata (much richer than TOM)
        '_dmv_metadata': None,
        '_cached_tables': None,
        '_cached_measures': None,
        '_cached_relationships': None,
        '_cached_summary': None,
        '_auto_connected': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Auto-conexion ──
def auto_connect():
    """Intenta conectar automaticamente a Power BI Desktop al inicio"""
    if st.session_state._auto_connected:
        return
    st.session_state._auto_connected = True

    if st.session_state.is_connected:
        return

    try:
        connector = XMLAConnector()
        if connector.connect():
            st.session_state.connector = connector
            st.session_state.is_connected = True
            st.session_state.mode = 'xmla'
            _init_adomd(connector.port)
            _cache_model_data()
    except Exception:
        pass

auto_connect()


def _init_adomd(port=None):
    """Inicializa el engine ADOMD para consultas DAX/DMV"""
    if not ADOMD_AVAILABLE:
        return
    try:
        engine = AdomdQueryEngine(port=port)
        if engine.connect():
            st.session_state.adomd = engine
            # Cachear metadata rica via DMVs
            st.session_state._dmv_metadata = engine.get_full_model_metadata()
            logger.info("ADOMD engine inicializado con DMV metadata")
    except Exception as e:
        logger.error(f"Error inicializando ADOMD: {e}")


def _cache_model_data():
    """Cachea datos del modelo para respuestas rapidas"""
    if st.session_state.mode == 'xmla':
        connector = st.session_state.connector
        tom = connector.get_tom_wrapper() if connector else None
        if tom and tom.is_connected:
            try:
                st.session_state._cached_tables = tom.get_tables()
                st.session_state._cached_measures = tom.get_measures()
                st.session_state._cached_relationships = tom.get_relationships()
                st.session_state._cached_summary = tom.get_model_summary()
            except Exception as e:
                logger.error(f"Error cacheando datos: {e}")


def _dmv():
    """Acceso rapido a DMV metadata cacheada"""
    return st.session_state._dmv_metadata


def get_model_tables():
    """Obtiene tablas del modelo (DMV > TOM > file)"""
    dmv = _dmv()
    if dmv:
        return dmv['tables']
    if st.session_state.mode == 'file' and st.session_state.model_data:
        return st.session_state.model_data.tables
    if st.session_state._cached_tables is not None:
        return st.session_state._cached_tables
    return []


def get_model_measures():
    """Obtiene medidas del modelo (DMV > TOM > file)"""
    dmv = _dmv()
    if dmv:
        return dmv['measures']
    if st.session_state.mode == 'file' and st.session_state.model_data:
        return st.session_state.model_data.measures
    if st.session_state._cached_measures is not None:
        return st.session_state._cached_measures
    return []


def get_model_relationships():
    """Obtiene relaciones (DMV > TOM > file)"""
    dmv = _dmv()
    if dmv:
        return dmv['relationships']
    if st.session_state.mode == 'file' and st.session_state.model_data:
        return st.session_state.model_data.relationships
    if st.session_state._cached_relationships is not None:
        return st.session_state._cached_relationships
    return []


def get_model_columns():
    """Obtiene columnas del modelo (DMV > file)"""
    dmv = _dmv()
    if dmv:
        return dmv['columns']
    if st.session_state.mode == 'file' and st.session_state.model_data:
        return st.session_state.model_data.columns
    return []


def get_columns_for_table(table_name: str) -> list:
    """Columnas de una tabla especifica"""
    dmv = _dmv()
    if dmv:
        return dmv.get('columns_by_table', {}).get(table_name, [])
    cols = get_model_columns()
    return [c for c in cols if _m_attr(c, 'table', '') == table_name or _m_attr(c, 'TableName', '') == table_name]


def _m_attr(obj, attr, default=''):
    """Accede atributo como dict o dataclass, case-insensitive para dicts"""
    if isinstance(obj, dict):
        # Intento exacto primero
        if attr in obj:
            return obj[attr]
        # Intento case-insensitive
        attr_lower = attr.lower()
        for k, v in obj.items():
            if k.lower() == attr_lower:
                return v
        return default
    return getattr(obj, attr, default)


# ── Sidebar ──
def display_sidebar():
    with st.sidebar:
        # Conexion
        st.markdown("## Conexion")

        # File uploader
        uploaded_file = st.file_uploader(
            "Archivo .pbix",
            type=['pbix'],
            help="Carga un archivo .pbix para analizar",
            label_visibility="collapsed"
        )

        if uploaded_file:
            if st.session_state.file_reader is None or st.session_state.mode != 'file':
                with st.spinner("Extrayendo modelo..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pbix') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    reader = PBIXFileReader(tmp_path)
                    st.session_state.model_data = reader.extract_model()
                    st.session_state.file_reader = reader
                    st.session_state.mode = 'file'
                    os.unlink(tmp_path)
                st.success("Modelo cargado desde archivo")

        # Boton conexion XMLA
        if st.button("Detectar Power BI Desktop", use_container_width=True):
            with st.spinner("Detectando..."):
                try:
                    connector = XMLAConnector()
                    if connector.connect():
                        st.session_state.connector = connector
                        st.session_state.is_connected = True
                        st.session_state.mode = 'xmla'
                        _init_adomd(connector.port)
                        _cache_model_data()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # Status
        has_model = _has_model()
        if has_model:
            mode_label = "Archivo" if st.session_state.mode == 'file' else "XMLA"
            st.markdown(f'<span class="status-badge status-connected">Conectado ({mode_label})</span>',
                        unsafe_allow_html=True)

            # KPIs compactos
            summary = _get_summary()
            if summary:
                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-value">{summary.get('tables_count', 0)}</div>
                        <div class="kpi-label">Tablas</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{summary.get('measures_count', 0)}</div>
                        <div class="kpi-label">Medidas</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{summary.get('relationships_count', 0)}</div>
                        <div class="kpi-label">Relaciones</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.mode == 'xmla':
                port = st.session_state.connector.port if st.session_state.connector else '-'
                st.caption(f"Puerto: {port}")
        else:
            st.markdown('<span class="status-badge status-disconnected">No conectado</span>',
                        unsafe_allow_html=True)
            st.caption("Abre un .pbix en Power BI Desktop o carga un archivo.")

        st.markdown("---")

        # Historial
        show_history_sidebar()

        # Favoritos
        show_favorites_sidebar()

        # Custom templates
        show_custom_template_quick_access()

        st.markdown("---")
        st.caption("Power BI Bot v2.0 | YPF - Equipo RTIC")


def _has_model():
    return (st.session_state.mode == 'file' and st.session_state.model_data) or \
           (st.session_state.mode == 'xmla' and st.session_state.is_connected)


def _get_summary():
    dmv = _dmv()
    if dmv:
        return dmv['stats']
    if st.session_state._cached_summary:
        return st.session_state._cached_summary
    if st.session_state.mode == 'file' and st.session_state.file_reader:
        return st.session_state.file_reader.get_summary()
    return {}


# ── Chat principal ──
def display_chat():
    # Sub-paginas
    if st.session_state.get('show_tutorial', False):
        show_tutorial()
        return
    if st.session_state.get('show_custom_templates', False):
        show_custom_template_manager()
        if st.button("Volver al Chat", key="back_custom"):
            st.session_state.show_custom_templates = False
            st.rerun()
        return
    if st.session_state.get('show_favorites', False):
        show_favorites_manager()
        if st.button("Volver al Chat", key="back_fav"):
            st.session_state.show_favorites = False
            st.rerun()
        return
    if st.session_state.get('show_full_history', False):
        show_full_history()
        if st.button("Volver al Chat", key="back_hist"):
            st.session_state.show_full_history = False
            st.rerun()
        return

    # Template workflow
    if st.session_state.get('show_template_ui', False) and _has_model():
        st.markdown("## Crear Nueva Medida DAX")
        if st.button("Cerrar", key="close_template_ui"):
            st.session_state.show_template_ui = False
            st.rerun()
        show_template_workflow()
        st.markdown("---")

    # Header
    st.markdown('<div class="app-header">Power BI Bot</div>', unsafe_allow_html=True)

    if not _has_model():
        _show_welcome()
        return

    # ── Chat ──
    history = st.session_state.chat_history

    # Limpiar
    if len(history) > 0:
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Limpiar chat", key="clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    # Mensaje inicial
    if len(history) == 0:
        with st.chat_message("assistant"):
            summary = _get_summary()
            tc = summary.get('tables_count', 0)
            mc = summary.get('measures_count', 0)
            rc = summary.get('relationships_count', 0)
            mode = "archivo" if st.session_state.mode == 'file' else "XMLA"
            has_dax = st.session_state.adomd is not None
            dax_note = " | DAX Engine activo" if has_dax else ""
            st.markdown(f"""**Modelo conectado** via {mode} &mdash; {tc} tablas, {mc} medidas, {rc} relaciones{dax_note}

**Explorar modelo:**
- **"medidas"** / **"medidas de #AA_Medidas"** &mdash; ver medidas (todas o por tabla)
- **"expresion Total Ventas"** &mdash; formula DAX de una medida
- **"tablas"** / **"columnas de Dim_Material"** / **"relaciones"**
- **"buscar ventas"** &mdash; busca en medidas, tablas y columnas
- **"folders"** / **"jerarquias"** / **"roles"** / **"fuentes"**
- **"resumen"** &mdash; estadisticas completas del modelo

**Ejecutar DAX** (requiere XMLA):
- **"EVALUATE TOPN(5, 'Dim_Material')"** &mdash; consulta DAX directa
- **"preview Dim_Material"** &mdash; vista previa de datos

**Crear medidas:** **"crear medida"** &mdash; asistente interactivo""")

    # Mostrar ultimos 20 mensajes
    MAX_VISIBLE = 20
    visible = history[-MAX_VISIBLE:] if len(history) > MAX_VISIBLE else history
    if len(history) > MAX_VISIBLE:
        st.caption(f"Mostrando los ultimos {MAX_VISIBLE} de {len(history)} mensajes")

    for msg in visible:
        role = "user" if msg['role'] == 'user' else "assistant"
        with st.chat_message(role):
            st.markdown(msg['content'])

    # Botones rapidos (solo sin historial)
    if len(history) == 0:
        cols = st.columns(4)
        quick_row1 = [
            ("Medidas", "medidas"),
            ("Tablas", "tablas"),
            ("Relaciones", "relaciones"),
            ("Resumen", "resumen detallado"),
        ]
        for col, (label, question) in zip(cols, quick_row1):
            with col:
                if st.button(label, key=f"q_{label}", use_container_width=True):
                    _add_and_process(question)

        cols2 = st.columns(4)
        quick_row2 = [
            ("Folders", "folders"),
            ("Fuentes", "fuentes"),
            ("Jerarquias", "jerarquias"),
            ("Roles", "roles"),
        ]
        for col, (label, question) in zip(cols2, quick_row2):
            with col:
                if st.button(label, key=f"q2_{label}", use_container_width=True):
                    _add_and_process(question)

    # Chat input
    user_input = st.chat_input("Pregunta sobre tu modelo...")
    if user_input:
        _add_and_process(user_input)


def _show_welcome():
    st.info("""
    **Para comenzar:**
    1. Carga un archivo .pbix desde el panel izquierdo
    2. O conecta a Power BI Desktop (se intenta auto-detectar)
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Consultas:**
        - Medidas, tablas, columnas, relaciones
        - Buscar por nombre o contenido
        - Ver expresiones DAX
        - Resumen y estadisticas
        """)
    with col2:
        st.markdown("""
        **Crear medidas:**
        - Time Intelligence (YTD, YoY...)
        - Agregaciones (SUM, AVG...)
        - Calculos (Margen, %)
        - Avanzados (Ranking, ABC...)
        """)


def _add_and_process(user_input: str):
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    })
    bot_response = process_message(user_input)
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': bot_response,
        'timestamp': datetime.now()
    })
    st.rerun()


# ══════════════════════════════════════════════════════
# ══  MOTOR DE PROCESAMIENTO DE CONSULTAS  ═══════════
# ══════════════════════════════════════════════════════

def process_message(user_input: str) -> str:
    """Procesa el mensaje del usuario con NLP mejorado"""
    q = user_input.strip()
    ql = q.lower()

    # ── Crear medida ──
    create_kw = ["crea", "crear", "nueva medida", "generar medida", "agregar medida",
                 "necesito una medida", "quiero crear", "haz una medida"]
    if any(k in ql for k in create_kw):
        st.session_state.show_template_ui = True
        return ("**Abriendo asistente de creacion de medidas DAX.**\n\n"
                "Selecciona el tipo de medida en el panel superior.")

    # ── Saludos ──
    if any(w in ql for w in ["hola", "buenos", "buenas", "hi", "hello"]):
        summary = _get_summary()
        return (f"Hola! Modelo conectado con {summary.get('measures_count', 0)} medidas "
                f"y {summary.get('tables_count', 0)} tablas. Preguntame lo que necesites.")

    # ── Ayuda ──
    if any(w in ql for w in ["ayuda", "help", "que puedo", "capacidades", "comandos"]):
        return _help_response()

    # ── Verificar modelo ──
    if not _has_model():
        return "Carga un archivo .pbix o conecta a Power BI Desktop para comenzar."

    # ── Ejecutar DAX directo ──
    dax_match = re.match(r'(?:evaluate|ejecutar dax|ejecuta dax|run dax|dax query|evaluar)\s+(.+)', ql, re.DOTALL)
    if dax_match or ql.startswith('evaluate '):
        dax_expr = dax_match.group(1).strip() if dax_match else q.strip()
        return _execute_dax_query(dax_expr)

    # ── Preview de datos de una tabla ──
    preview_match = re.match(r'(?:preview|datos|data|ver datos|muestra datos|sample)\s+(?:de\s+)?(.+)', ql)
    if preview_match:
        return _table_preview(preview_match.group(1).strip())

    # ── Expresion/formula de una medida ──
    expr_match = re.match(r'(?:expresi[oó]n|formula|dax|codigo|c[oó]digo)\s+(?:de\s+)?(.+)', ql)
    if expr_match:
        return _search_measure_expression(expr_match.group(1).strip())

    # ── Buscar (generico) ──
    search_match = re.match(r'(?:buscar?|busca|encontrar?|encuentra|search|filtrar?|filtra)\s+(.+)', ql)
    if search_match:
        return _global_search(search_match.group(1).strip())

    # ── Medidas de una tabla especifica ──
    table_measures_match = re.match(
        r'(?:medidas?|measures?)\s+(?:de|en|from|tabla|table)\s+(.+)', ql)
    if table_measures_match:
        return _measures_for_table(table_measures_match.group(1).strip())

    # ── Columnas de una tabla especifica ──
    table_cols_match = re.match(
        r'(?:columnas?|columns?|campos?)\s+(?:de|en|from|tabla|table)\s+(.+)', ql)
    if table_cols_match:
        return _columns_for_table_query(table_cols_match.group(1).strip())

    # ── Display folders ──
    if any(w in ql for w in ["folder", "folders", "carpeta", "carpetas", "display folder"]):
        return _display_folders()

    # ── Power Query / M expressions ──
    if any(w in ql for w in ["power query", "query", "m expression", "fuente", "fuentes",
                              "origen", "source", "sources", "particion", "particiones"]):
        return _power_query_info()

    # ── Jerarquias ──
    if any(w in ql for w in ["jerarquia", "jerarquias", "hierarchy", "hierarchies"]):
        return _hierarchies_info()

    # ── Roles / seguridad ──
    if any(w in ql for w in ["rol", "roles", "seguridad", "security", "rls"]):
        return _roles_info()

    # ── Medidas (general) ──
    if any(w in ql for w in ["medida", "medidas", "measure", "measures"]):
        return _all_measures()

    # ── Tablas ──
    if any(w in ql for w in ["tabla", "tablas", "table", "tables", "entidad"]):
        return _all_tables()

    # ── Relaciones ──
    if any(w in ql for w in ["relacion", "relaciones", "relationship", "relationships",
                              "vinculo", "vinculos"]):
        return _all_relationships()

    # ── Columnas (general) ──
    if any(w in ql for w in ["columna", "columnas", "column", "columns", "campo", "campos"]):
        return _all_columns()

    # ── Resumen / estadisticas ──
    if any(w in ql for w in ["resumen", "estadistica", "estadisticas", "summary", "stats",
                              "cuantas", "cuantos", "overview", "modelo", "info"]):
        return _detailed_summary()

    # ── Intento de busqueda implicita ──
    if len(ql) >= 3:
        result = _global_search(ql)
        if "No se encontraron resultados" not in result:
            return result

    return _fallback_response()


# ── Respuestas ──

def _help_response() -> str:
    mode = "archivo" if st.session_state.mode == 'file' else "XMLA"
    has_adomd = st.session_state.adomd is not None
    dax_status = "Disponible" if has_adomd else "No disponible"
    return f"""**Power BI Bot** &mdash; Modo: {mode} | DAX Engine: {dax_status}

**Explorar modelo:**

| Comando | Ejemplo |
|---------|---------|
| Medidas | "medidas" o "medidas de #AA_Medidas" |
| Ver expresion DAX | "expresion Total Ventas" |
| Tablas | "tablas" |
| Columnas de tabla | "columnas de Dim_Material" |
| Relaciones | "relaciones" |
| Resumen completo | "resumen" |
| Display folders | "folders" |
| Power Query / fuentes | "fuentes" o "power query" |
| Jerarquias | "jerarquias" |
| Roles / RLS | "roles" |
| Buscar en todo | "buscar ventas" |

**Ejecutar DAX** (solo XMLA):

| Comando | Ejemplo |
|---------|---------|
| Consulta DAX | "EVALUATE TOPN(5, 'Dim_Material')" |
| Preview datos | "preview Dim_Material" |

**Crear medidas:**

| Comando | Ejemplo |
|---------|---------|
| Crear medida | "crear medida de ventas YTD" |

Escribe en lenguaje natural."""


def _fallback_response() -> str:
    return """No encontre informacion para esa consulta.

Prueba con:
- **"medidas"** / **"tablas"** / **"relaciones"** / **"resumen"**
- **"buscar [termino]"** para buscar en todo el modelo
- **"expresion [nombre medida]"** para ver una formula DAX
- **"medidas de [tabla]"** para filtrar por tabla
- **"ayuda"** para ver todas las opciones"""


def _all_measures() -> str:
    measures = get_model_measures()
    if not measures:
        return "No se encontraron medidas en el modelo."

    # Agrupar por tabla (DMV usa TableName, file usa table)
    by_table = {}
    for m in measures:
        table = _m_attr(m, 'TableName', '') or _m_attr(m, 'table', '') or '(sin tabla)'
        if table not in by_table:
            by_table[table] = []
        by_table[table].append(m)

    lines = [f"**{len(measures)} medidas** en {len(by_table)} tablas:\n"]

    for table in sorted(by_table.keys()):
        tms = by_table[table]
        lines.append(f"\n**{table}** ({len(tms)} medidas)")
        for m in tms[:15]:
            name = _m_attr(m, 'Name', '') or _m_attr(m, 'name', '')
            expr = _m_attr(m, 'Expression', '') or _m_attr(m, 'expression', '')
            if expr:
                preview = str(expr).replace('\n', ' ').strip()[:60]
                lines.append(f"- `{name}` &mdash; `{preview}...`" if len(str(expr)) > 60 else f"- `{name}` &mdash; `{preview}`")
            else:
                lines.append(f"- `{name}`")
        if len(tms) > 15:
            lines.append(f"  *... y {len(tms) - 15} mas (usa \"medidas de {table}\" para ver todas)*")

    return '\n'.join(lines)


def _measures_for_table(table_query: str) -> str:
    measures = get_model_measures()
    if not measures:
        return "No se encontraron medidas."

    # Buscar tabla (fuzzy)
    table_query_clean = table_query.strip().strip('"\'')
    matching = []
    for m in measures:
        tname = _m_attr(m, 'TableName', '') or _m_attr(m, 'table', '')
        if table_query_clean.lower() in tname.lower():
            matching.append(m)

    if not matching:
        all_tables = set()
        for m in measures:
            all_tables.add(_m_attr(m, 'TableName', '') or _m_attr(m, 'table', ''))
        suggestions = [t for t in all_tables if table_query_clean.lower()[:3] in t.lower()][:5]
        resp = f"No encontre medidas en tabla \"{table_query_clean}\"."
        if suggestions:
            resp += "\n\nTablas similares: " + ", ".join(f"`{s}`" for s in suggestions)
        return resp

    real_table = _m_attr(matching[0], 'TableName', '') or _m_attr(matching[0], 'table', '')
    lines = [f"**{len(matching)} medidas en {real_table}:**\n"]

    for m in matching:
        name = _m_attr(m, 'Name', '') or _m_attr(m, 'name', '')
        expr = _m_attr(m, 'Expression', '') or _m_attr(m, 'expression', '')
        desc = _m_attr(m, 'Description', '') or _m_attr(m, 'description', '')
        fmt = _m_attr(m, 'FormatString', '') or _m_attr(m, 'format_string', '')

        lines.append(f"**`{name}`**")
        if desc:
            lines.append(f"  Desc: {desc}")
        if expr:
            lines.append(f"```dax\n{str(expr).strip()}\n```")
        if fmt:
            lines.append(f"  Formato: `{fmt}`")
        lines.append("")

    return '\n'.join(lines)


def _search_measure_expression(query: str) -> str:
    measures = get_model_measures()
    if not measures:
        return "No hay medidas en el modelo."

    query_clean = query.strip().strip('"\'').lower()

    def mname(m):
        return (_m_attr(m, 'Name', '') or _m_attr(m, 'name', '')).lower()

    exact = [m for m in measures if mname(m) == query_clean]
    if not exact:
        exact = [m for m in measures if query_clean in mname(m)]

    if not exact:
        close = [_m_attr(m, 'Name', '') or _m_attr(m, 'name', '') for m in measures
                 if any(w in mname(m) for w in query_clean.split())][:5]
        resp = f"No encontre medida \"{query}\"."
        if close:
            resp += "\n\nMedidas similares:\n" + "\n".join(f"- `{c}`" for c in close)
        return resp

    lines = []
    for m in exact[:5]:
        name = _m_attr(m, 'Name', '') or _m_attr(m, 'name', '')
        table = _m_attr(m, 'TableName', '') or _m_attr(m, 'table', '')
        expr = _m_attr(m, 'Expression', '') or _m_attr(m, 'expression', '')
        desc = _m_attr(m, 'Description', '') or _m_attr(m, 'description', '')
        fmt = _m_attr(m, 'FormatString', '') or _m_attr(m, 'format_string', '')

        lines.append(f"**{name}** (tabla: `{table}`)")
        if desc:
            lines.append(f"Descripcion: {desc}")
        if fmt:
            lines.append(f"Formato: `{fmt}`")
        if expr:
            lines.append(f"```dax\n{str(expr).strip()}\n```")
        else:
            lines.append("*Sin expresion DAX*")
        lines.append("")

    if len(exact) > 5:
        lines.append(f"*... y {len(exact) - 5} medidas mas con ese nombre*")

    return '\n'.join(lines)


def _global_search(query: str) -> str:
    query_clean = query.strip().lower()

    # Buscar en medidas
    measures = get_model_measures()
    matching_measures = []
    for m in measures:
        name = (_m_attr(m, 'Name', '') or _m_attr(m, 'name', '')).lower()
        expr = str(_m_attr(m, 'Expression', '') or _m_attr(m, 'expression', '') or '').lower()
        desc = str(_m_attr(m, 'Description', '') or _m_attr(m, 'description', '') or '').lower()
        if query_clean in name or query_clean in expr or query_clean in desc:
            matching_measures.append(m)

    # Buscar en tablas
    tables = get_model_tables()
    matching_tables = []
    for t in tables:
        tname = (_m_attr(t, 'Name', '') or _m_attr(t, 'name', '') or '').lower()
        tdesc = str(_m_attr(t, 'Description', '') or _m_attr(t, 'description', '') or '').lower()
        if query_clean in tname or query_clean in tdesc:
            matching_tables.append(t)

    # Buscar en columnas
    columns = get_model_columns()
    matching_columns = []
    for c in columns:
        cname = (_m_attr(c, 'Name', '') or _m_attr(c, 'name', '')).lower()
        if query_clean in cname:
            matching_columns.append(c)

    if not matching_measures and not matching_tables and not matching_columns:
        return f'No se encontraron resultados para "{query}".\n\nPrueba con otro termino o escribe **"medidas"** para ver todas.'

    lines = [f'**Resultados para "{query}":**\n']

    if matching_tables:
        lines.append(f"**Tablas ({len(matching_tables)}):**")
        for t in matching_tables[:10]:
            tname = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
            lines.append(f"- `{tname}`")
        lines.append("")

    if matching_measures:
        lines.append(f"**Medidas ({len(matching_measures)}):**")
        for m in matching_measures[:20]:
            name = _m_attr(m, 'Name', '') or _m_attr(m, 'name', '')
            table = _m_attr(m, 'TableName', '') or _m_attr(m, 'table', '')
            expr = str(_m_attr(m, 'Expression', '') or _m_attr(m, 'expression', '') or '')
            preview = expr.replace('\n', ' ').strip()[:50] if expr else ''
            if preview:
                lines.append(f"- `{name}` ({table}) &mdash; `{preview}...`")
            else:
                lines.append(f"- `{name}` ({table})")
        if len(matching_measures) > 20:
            lines.append(f"\n*... y {len(matching_measures) - 20} mas*")

    if matching_columns:
        lines.append(f"\n**Columnas ({len(matching_columns)}):**")
        for c in matching_columns[:15]:
            cname = _m_attr(c, 'Name', '') or _m_attr(c, 'name', '')
            ctable = _m_attr(c, 'TableName', '') or _m_attr(c, 'table', '')
            lines.append(f"- `{ctable}`.`{cname}`")
        if len(matching_columns) > 15:
            lines.append(f"  *... y {len(matching_columns) - 15} mas*")

    return '\n'.join(lines)


def _all_tables() -> str:
    tables = get_model_tables()
    if not tables:
        return "No se encontraron tablas."

    # Contar columnas y medidas por tabla desde DMV
    dmv = _dmv()
    cols_by_table = {}
    meas_by_table = {}
    if dmv:
        for c in dmv.get('columns', []):
            tn = c.get('TableName', '')
            cols_by_table[tn] = cols_by_table.get(tn, 0) + 1
        for m in dmv.get('measures', []):
            tn = m.get('TableName', '')
            meas_by_table[tn] = meas_by_table.get(tn, 0) + 1

    # Separar visibles y ocultas
    visible = []
    hidden = []
    for t in tables:
        is_hidden = _m_attr(t, 'IsHidden', False) or _m_attr(t, 'is_hidden', False)
        if is_hidden:
            hidden.append(t)
        else:
            visible.append(t)

    lines = [f"**{len(tables)} tablas** ({len(visible)} visibles, {len(hidden)} ocultas):\n"]

    lines.append("| Tabla | Columnas | Medidas | Descripcion |")
    lines.append("|-------|----------|---------|-------------|")

    for t in sorted(visible, key=lambda x: _m_attr(x, 'Name', '') or _m_attr(x, 'name', '')):
        name = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
        cols = cols_by_table.get(name, _m_attr(t, 'columns_count', 0))
        meas = meas_by_table.get(name, _m_attr(t, 'measures_count', 0))
        desc = str(_m_attr(t, 'Description', '') or '')[:40]
        lines.append(f"| `{name}` | {cols} | {meas} | {desc} |")

    if hidden:
        lines.append(f"\n<details><summary>Tablas ocultas ({len(hidden)})</summary>\n")
        for t in sorted(hidden, key=lambda x: _m_attr(x, 'Name', '') or _m_attr(x, 'name', '')):
            name = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
            lines.append(f"- `{name}`")
        lines.append("</details>")

    return '\n'.join(lines)


def _all_relationships() -> str:
    rels = get_model_relationships()
    if not rels:
        return "No se encontraron relaciones en el modelo."

    # Para DMV, necesitamos resolver IDs a nombres
    dmv = _dmv()
    table_map = dmv.get('table_map', {}) if dmv else {}
    col_map = {}
    if dmv:
        for c in dmv.get('columns', []):
            cid = c.get('ID', '')
            if cid:
                col_map[cid] = c.get('Name', '')

    lines = [f"**{len(rels)} relaciones:**\n"]
    lines.append("| Desde | &rarr; | Hasta | Cardinalidad | Filtro | Estado |")
    lines.append("|-------|--------|-------|--------------|--------|--------|")

    for r in rels:
        # DMV keys (FromTableID, ToTableID, FromColumnID, ToColumnID)
        ft_id = _m_attr(r, 'FromTableID', '')
        tt_id = _m_attr(r, 'ToTableID', '')
        fc_id = _m_attr(r, 'FromColumnID', '')
        tc_id = _m_attr(r, 'ToColumnID', '')
        ft = table_map.get(ft_id, '') or _m_attr(r, 'from_table', '') or str(ft_id)
        tt = table_map.get(tt_id, '') or _m_attr(r, 'to_table', '') or str(tt_id)
        fc = col_map.get(fc_id, '') or _m_attr(r, 'from_column', '') or str(fc_id)
        tc = col_map.get(tc_id, '') or _m_attr(r, 'to_column', '') or str(tc_id)

        from_card = _m_attr(r, 'FromCardinality', '')
        to_card = _m_attr(r, 'ToCardinality', '')
        card = _m_attr(r, 'cardinality', '') or f"{from_card}:{to_card}"

        cross_filter = _m_attr(r, 'CrossFilteringBehavior', '')
        active = _m_attr(r, 'IsActive', True) if _m_attr(r, 'IsActive', None) is not None else _m_attr(r, 'is_active', True)
        status = "Activa" if active else "Inactiva"
        lines.append(f"| `{ft}`.{fc} | &rarr; | `{tt}`.{tc} | {card} | {cross_filter} | {status} |")

    return '\n'.join(lines)


def _all_columns() -> str:
    if st.session_state.mode == 'file':
        cols = get_model_columns()
        if not cols:
            return "No se encontraron columnas."

        by_table = {}
        for c in cols:
            t = c.get('table', '')
            if t not in by_table:
                by_table[t] = []
            by_table[t].append(c)

        lines = [f"**{len(cols)} columnas** en {len(by_table)} tablas:\n"]
        for table in sorted(by_table.keys()):
            tcols = by_table[table]
            lines.append(f"\n**{table}** ({len(tcols)} columnas)")
            for c in tcols[:10]:
                dtype = f" ({c.get('data_type', '')})" if c.get('data_type') else ""
                lines.append(f"- `{c['name']}`{dtype}")
            if len(tcols) > 10:
                lines.append(f"  *... y {len(tcols) - 10} mas*")
        return '\n'.join(lines)

    # XMLA mode: usar DMV data
    dmv = _dmv()
    if dmv:
        cols_by_table = dmv.get('columns_by_table', {})
        total = sum(len(v) for v in cols_by_table.values())
        lines = [f"**{total} columnas** en {len(cols_by_table)} tablas:\n"]
        lines.append("| Tabla | Columnas |")
        lines.append("|-------|----------|")
        for tname in sorted(cols_by_table.keys()):
            lines.append(f"| `{tname}` | {len(cols_by_table[tname])} |")
        lines.append(f"\nPara ver columnas de una tabla: **\"columnas de [nombre tabla]\"**")
        return '\n'.join(lines)

    tables = get_model_tables()
    if not tables:
        return "No se encontraron tablas."

    lines = ["**Columnas por tabla:**\n"]
    lines.append("| Tabla | Columnas |")
    lines.append("|-------|----------|")
    total = 0
    for t in sorted(tables, key=lambda x: _m_attr(x, 'Name', '') or _m_attr(x, 'name', '')):
        name = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
        count = _m_attr(t, 'columns_count', 0)
        total += count
        lines.append(f"| `{name}` | {count} |")

    lines.insert(0, f"**{total} columnas** en {len(tables)} tablas:\n")
    lines.append(f"\nPara ver columnas de una tabla: **\"columnas de [nombre tabla]\"**")
    return '\n'.join(lines)


def _columns_for_table(table_query: str) -> str:
    table_query_clean = table_query.strip().strip('"\'')

    if st.session_state.mode == 'file':
        cols = get_model_columns()
        matching = [c for c in cols if table_query_clean.lower() in c.get('table', '').lower()]
        if not matching:
            all_tables = sorted(set(c.get('table', '') for c in cols))
            suggestions = [t for t in all_tables if table_query_clean.lower()[:3] in t.lower()][:5]
            resp = f"No encontre columnas en tabla \"{table_query_clean}\"."
            if suggestions:
                resp += "\n\nTablas similares: " + ", ".join(f"`{s}`" for s in suggestions)
            return resp

        real_table = matching[0]['table']
        lines = [f"**{len(matching)} columnas en {real_table}:**\n"]
        lines.append("| Columna | Tipo |")
        lines.append("|---------|------|")
        for c in matching:
            dtype = c.get('data_type', '-')
            lines.append(f"| `{c['name']}` | {dtype} |")
        return '\n'.join(lines)

    # XMLA mode: intentar via TOM
    connector = st.session_state.connector
    tom = connector.get_tom_wrapper() if connector else None
    if tom and tom.is_connected:
        try:
            all_tables = tom.get_tables()
            target = None
            for t in all_tables:
                if table_query_clean.lower() in t.name.lower():
                    target = t
                    break
            if target:
                # Obtener columnas via TOM directo
                table_obj = None
                for t in tom.model.Tables:
                    if t.Name == target.name:
                        table_obj = t
                        break
                if table_obj:
                    lines = [f"**{table_obj.Columns.Count} columnas en {target.name}:**\n"]
                    lines.append("| Columna | Tipo | Oculta |")
                    lines.append("|---------|------|--------|")
                    for col in table_obj.Columns:
                        hidden = "Si" if col.IsHidden else "No"
                        dtype = str(col.DataType) if hasattr(col, 'DataType') else '-'
                        lines.append(f"| `{col.Name}` | {dtype} | {hidden} |")
                    return '\n'.join(lines)
            else:
                suggestions = [t.name for t in all_tables if table_query_clean.lower()[:3] in t.name.lower()][:5]
                resp = f"No encontre tabla \"{table_query_clean}\"."
                if suggestions:
                    resp += "\n\nTablas similares: " + ", ".join(f"`{s}`" for s in suggestions)
                return resp
        except Exception as e:
            return f"Error accediendo columnas: {e}"

    return "Columnas detalladas no disponibles en este modo."


def _execute_dax_query(dax: str) -> str:
    """Ejecuta una consulta DAX contra el modelo"""
    engine = st.session_state.adomd
    if not engine or not engine.is_connected:
        return "La ejecucion de DAX requiere conexion XMLA con ADOMD. Conecta a Power BI Desktop."

    try:
        rows = engine.execute_dax(dax)
        if not rows:
            return "La consulta no retorno resultados."

        # Formatear como tabla markdown
        cols = list(rows[0].keys())
        lines = [f"**Resultado DAX** ({len(rows)} filas):\n"]

        # Header
        lines.append("| " + " | ".join(str(c) for c in cols) + " |")
        lines.append("|" + "|".join("---" for _ in cols) + "|")

        # Rows (max 50)
        for r in rows[:50]:
            vals = []
            for c in cols:
                v = r.get(c, '')
                vals.append(str(v)[:50] if v is not None else '-')
            lines.append("| " + " | ".join(vals) + " |")

        if len(rows) > 50:
            lines.append(f"\n*... {len(rows) - 50} filas mas*")

        return '\n'.join(lines)
    except Exception as e:
        return f"Error ejecutando DAX:\n```\n{e}\n```"


def _table_preview(table_query: str) -> str:
    """Preview de datos de una tabla"""
    engine = st.session_state.adomd
    if not engine or not engine.is_connected:
        return "Preview de datos requiere conexion XMLA."

    # Buscar tabla
    tables = get_model_tables()
    target = None
    tq = table_query.strip().strip('"\'')
    for t in tables:
        tname = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
        if tq.lower() in tname.lower():
            target = tname
            break

    if not target:
        return f"No encontre tabla \"{tq}\". Escribe **tablas** para ver la lista."

    try:
        rows = engine.get_table_preview(target, top_n=10)
        if not rows:
            return f"Tabla `{target}` no tiene datos o no se pudo acceder."

        cols = list(rows[0].keys())
        lines = [f"**Preview de `{target}`** ({len(rows)} filas):\n"]

        # Limpiar nombres de columnas (quitar prefijo de tabla)
        clean_cols = [c.split(']')[-1].strip('[') if '][' in c else c.strip("[]'") for c in cols]

        lines.append("| " + " | ".join(clean_cols) + " |")
        lines.append("|" + "|".join("---" for _ in cols) + "|")

        for r in rows:
            vals = [str(r.get(c, '-'))[:30] for c in cols]
            lines.append("| " + " | ".join(vals) + " |")

        return '\n'.join(lines)
    except Exception as e:
        return f"Error obteniendo preview: {e}"


def _display_folders() -> str:
    """Muestra display folders de medidas"""
    measures = get_model_measures()
    if not measures:
        return "No hay medidas."

    folders = {}
    no_folder = []
    for m in measures:
        folder = _m_attr(m, 'DisplayFolder', '') or _m_attr(m, 'display_folder', '')
        name = _m_attr(m, 'Name', '') or _m_attr(m, 'name', '')
        if folder:
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(name)
        else:
            no_folder.append(name)

    lines = [f"**Display Folders** ({len(folders)} carpetas, {len(no_folder)} sin carpeta):\n"]

    for folder in sorted(folders.keys()):
        items = folders[folder]
        lines.append(f"**{folder}/** ({len(items)} medidas)")
        for m in items[:10]:
            lines.append(f"- `{m}`")
        if len(items) > 10:
            lines.append(f"  *... y {len(items) - 10} mas*")
        lines.append("")

    if no_folder:
        lines.append(f"**Sin carpeta** ({len(no_folder)} medidas)")
        for m in no_folder[:10]:
            lines.append(f"- `{m}`")
        if len(no_folder) > 10:
            lines.append(f"  *... y {len(no_folder) - 10} mas*")

    return '\n'.join(lines)


def _power_query_info() -> str:
    """Info de Power Query / fuentes / particiones"""
    engine = st.session_state.adomd
    if not engine or not engine.is_connected:
        return "Informacion de Power Query requiere conexion XMLA."

    lines = []

    # Expresiones M compartidas
    expressions = engine.dmv_expressions()
    if expressions:
        lines.append(f"**Expresiones Power Query compartidas** ({len(expressions)}):\n")
        for e in expressions:
            name = e.get('Name', '')
            kind = e.get('Kind', '')
            expr = str(e.get('Expression', ''))[:100]
            lines.append(f"**`{name}`** (tipo: {kind})")
            if expr:
                lines.append(f"```\n{expr}...\n```")
            lines.append("")

    # Particiones (fuentes de datos)
    partitions = engine.dmv_partitions()
    if partitions:
        # Agrupar por tipo
        by_type = {}
        for p in partitions:
            st_type = str(p.get('SourceType', ''))
            if st_type not in by_type:
                by_type[st_type] = []
            by_type[st_type].append(p)

        lines.append(f"**Particiones / Fuentes de datos** ({len(partitions)} total):\n")
        lines.append("| Tipo fuente | Cantidad |")
        lines.append("|-------------|----------|")
        for stype, parts in sorted(by_type.items()):
            lines.append(f"| {stype} | {len(parts)} |")

    if not lines:
        return "No se encontro informacion de Power Query."

    return '\n'.join(lines)


def _hierarchies_info() -> str:
    """Info de jerarquias"""
    engine = st.session_state.adomd
    if not engine or not engine.is_connected:
        return "Informacion de jerarquias requiere conexion XMLA."

    hierarchies = engine.dmv_hierarchies()
    if not hierarchies:
        return "No se encontraron jerarquias en el modelo."

    dmv = _dmv()
    table_map = dmv.get('table_map', {}) if dmv else {}

    lines = [f"**{len(hierarchies)} jerarquias:**\n"]
    lines.append("| Jerarquia | Tabla | Oculta |")
    lines.append("|-----------|-------|--------|")
    for h in hierarchies:
        name = h.get('Name', '')
        tid = h.get('TableID', '')
        tname = table_map.get(tid, f'Table_{tid}')
        hidden = "Si" if h.get('IsHidden') else "No"
        lines.append(f"| `{name}` | `{tname}` | {hidden} |")

    return '\n'.join(lines)


def _roles_info() -> str:
    """Info de roles de seguridad"""
    engine = st.session_state.adomd
    if not engine or not engine.is_connected:
        return "Informacion de roles requiere conexion XMLA."

    roles = engine.dmv_roles()
    if not roles:
        return "No se encontraron roles de seguridad (RLS) en el modelo."

    lines = [f"**{len(roles)} roles de seguridad:**\n"]
    lines.append("| Rol | Permiso | Descripcion |")
    lines.append("|-----|---------|-------------|")
    for r in roles:
        name = r.get('Name', '')
        perm = r.get('ModelPermission', '')
        desc = str(r.get('Description', '') or '')[:50]
        lines.append(f"| `{name}` | {perm} | {desc} |")

    return '\n'.join(lines)


def _columns_for_table_query(table_query: str) -> str:
    """Columnas de una tabla especifica usando DMV"""
    tq = table_query.strip().strip('"\'')
    tables = get_model_tables()

    # Buscar tabla
    target = None
    target_id = None
    for t in tables:
        tname = _m_attr(t, 'Name', '') or _m_attr(t, 'name', '')
        if tq.lower() in tname.lower():
            target = tname
            target_id = _m_attr(t, 'ID', None)
            break

    if not target:
        suggestions = [_m_attr(t, 'Name', '') or _m_attr(t, 'name', '') for t in tables
                       if tq.lower()[:3] in (_m_attr(t, 'Name', '') or _m_attr(t, 'name', '')).lower()][:5]
        resp = f"No encontre tabla \"{tq}\"."
        if suggestions:
            resp += "\n\nTablas similares: " + ", ".join(f"`{s}`" for s in suggestions)
        return resp

    cols = get_columns_for_table(target)
    if not cols:
        return f"No se encontraron columnas en `{target}`."

    # Separar tipos
    data_cols = []
    calc_cols = []
    for c in cols:
        ctype = _m_attr(c, 'Type', '') or _m_attr(c, 'column_type', '')
        if str(ctype) in ('2', 'CalculatedColumn', 'Calculated'):
            calc_cols.append(c)
        else:
            data_cols.append(c)

    lines = [f"**{len(cols)} columnas en `{target}`:**\n"]

    if data_cols:
        lines.append(f"**Columnas de datos ({len(data_cols)}):**\n")
        lines.append("| Columna | Tipo | Oculta | Formato |")
        lines.append("|---------|------|--------|---------|")
        for c in data_cols:
            name = _m_attr(c, 'Name', '') or _m_attr(c, 'name', '')
            dtype = _m_attr(c, 'ExplicitDataType', '') or _m_attr(c, 'data_type', '') or '-'
            hidden = "Si" if _m_attr(c, 'IsHidden', False) else "No"
            fmt = _m_attr(c, 'FormatString', '') or '-'
            lines.append(f"| `{name}` | {dtype} | {hidden} | {fmt} |")

    if calc_cols:
        lines.append(f"\n**Columnas calculadas ({len(calc_cols)}):**\n")
        for c in calc_cols:
            name = _m_attr(c, 'Name', '') or _m_attr(c, 'name', '')
            expr = _m_attr(c, 'Expression', '') or ''
            lines.append(f"**`{name}`**")
            if expr:
                lines.append(f"```dax\n{expr.strip()}\n```")

    return '\n'.join(lines)


def _detailed_summary() -> str:
    summary = _get_summary()
    if not summary:
        return "No hay modelo cargado."

    tc = summary.get('tables_count', 0)
    mc = summary.get('measures_count', 0)
    rc = summary.get('relationships_count', 0)
    hc = summary.get('hidden_tables_count', 0)
    mode = "Archivo" if st.session_state.mode == 'file' else "XMLA"

    lines = [f"**Resumen del Modelo** (modo: {mode})\n"]

    # KPIs
    lines.append("| Metrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Tablas totales | **{tc}** |")
    lines.append(f"| Tablas ocultas | {hc} |")
    lines.append(f"| Tablas visibles | {tc - hc} |")
    lines.append(f"| Medidas totales | **{mc}** |")
    lines.append(f"| Relaciones | **{rc}** |")

    # Top tablas por medidas
    measures = get_model_measures()
    if measures:
        by_table = {}
        for m in measures:
            t = _m_attr(m, 'TableName', '') or _m_attr(m, 'table', '')
            by_table[t] = by_table.get(t, 0) + 1

        top = sorted(by_table.items(), key=lambda x: x[1], reverse=True)[:10]
        lines.append(f"\n**Top tablas por cantidad de medidas:**\n")
        lines.append("| Tabla | Medidas |")
        lines.append("|-------|---------|")
        for t, count in top:
            lines.append(f"| `{t}` | {count} |")

    # Top tablas por columnas
    tables = get_model_tables()
    if tables:
        top_cols = sorted(tables, key=lambda x: _m_attr(x, 'columns_count', 0), reverse=True)[:5]
        lines.append(f"\n**Top tablas por columnas:**\n")
        for t in top_cols:
            name = _m_attr(t, 'name', '')
            c = _m_attr(t, 'columns_count', 0)
            lines.append(f"- `{name}` &mdash; {c} columnas")

    return '\n'.join(lines)


# ── Main ──
def main():
    display_sidebar()
    display_chat()

if __name__ == "__main__":
    logger.add("logs/app_{time}.log", rotation="1 day", retention="7 days", level="INFO")
    logger.info("Iniciando Power BI Bot...")
    main()
