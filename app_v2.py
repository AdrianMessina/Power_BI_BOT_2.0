"""
Power BI Bot 2.0 - Buscador de Reportes del Tenant
Aplicación Streamlit independiente para consultar el catálogo de Power BI.
NO modifica ni depende de app.py (Power BI Bot 1.0).
"""

import sys
import os
from pathlib import Path

# Asegurar paths
current_dir = str(Path(__file__).resolve().parent)
sys.path = [p for p in sys.path if not (p.endswith('.py') or p.endswith('.exe'))]
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
os.chdir(current_dir)

import importlib
for _pkg in ['core', 'utils']:
    try:
        importlib.import_module(_pkg)
    except Exception:
        pass

import streamlit as st
import logging
from datetime import datetime
from core.pbi_catalog import PBICatalog
from core.catalog_search import CatalogSearch

# ── Configuración de página ────────────────────────────────

st.set_page_config(
    page_title="Power BI Bot 2.0 - Buscador de Reportes",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

logger = logging.getLogger(__name__)


# ── Session State ──────────────────────────────────────────

def init_session_state():
    if "catalog" not in st.session_state:
        st.session_state.catalog = PBICatalog()
    if "search_engine" not in st.session_state:
        st.session_state.search_engine = CatalogSearch(st.session_state.catalog)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "scan_in_progress" not in st.session_state:
        st.session_state.scan_in_progress = False


init_session_state()


# ── Sidebar ────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.title("Power BI Bot 2.0")
        st.caption("Buscador de Reportes del Tenant")
        st.divider()

        # Estado del catálogo
        catalog = st.session_state.catalog
        if catalog.is_empty():
            st.warning("Catálogo vacío. Ejecutá un scan primero.")
        else:
            stats = catalog.get_stats()
            st.success(f"Catálogo activo")
            col1, col2 = st.columns(2)
            col1.metric("Workspaces", stats["workspaces"])
            col2.metric("Reportes", stats["reports"])
            col1.metric("Datasets", stats["datasets"])
            col2.metric("Tablas", stats["tables"])
            col1.metric("Medidas", stats["measures"])
            col2.metric("Data Sources", stats["datasources"])

            last_scan = stats.get("last_scan_date", "")
            if last_scan:
                st.caption(f"Último scan: {last_scan[:19]}")

        st.divider()

        # Acciones
        st.subheader("Acciones")

        if st.button("Escanear Tenant", type="primary", use_container_width=True,
                      disabled=st.session_state.scan_in_progress):
            st.session_state.show_scan_dialog = True

        if st.button("Importar JSON", use_container_width=True):
            st.session_state.show_import_dialog = True

        if not catalog.is_empty():
            if st.button("Limpiar Catálogo", use_container_width=True):
                st.session_state.show_clear_dialog = True

        st.divider()

        # Ejemplos de preguntas
        st.subheader("Ejemplos de preguntas")
        examples = [
            "¿Hay algún tablero de Serviclub?",
            "¿Quién es el dueño del reporte de ventas?",
            "¿Qué reportes usan la tabla DimClientes?",
            "Listar workspaces",
            "¿Cuántos reportes hay?",
            "Reportes de Juan Pérez",
            "¿Qué reportes hay en el workspace Comercial?",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": ex})
                result = st.session_state.search_engine.search(ex)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["summary"],
                    "data": result,
                })
                st.rerun()


# ── Diálogo de Scan ────────────────────────────────────────

def render_scan_dialog():
    if not st.session_state.get("show_scan_dialog"):
        return

    st.subheader("Escanear Tenant de Power BI")

    try:
        from core.pbi_scanner import PBIAuthenticator, PBITenantScanner, MSAL_AVAILABLE
        if not MSAL_AVAILABLE:
            st.error("Falta instalar `msal`. Ejecutar: `pip install msal`")
            if st.button("Cancelar"):
                st.session_state.show_scan_dialog = False
                st.rerun()
            return
    except ImportError as e:
        st.error(f"Error importando scanner: {e}")
        return

    st.info(
        "Se va a abrir una ventana del navegador para iniciar sesión con tu usuario de Power BI.\n\n"
        "**Requisitos:**\n"
        "- Usuario con permisos de Admin de Power BI\n"
        "- Acceso al tenant de la organización"
    )

    tenant_id = st.text_input(
        "Tenant ID (opcional, dejar vacío para auto-detectar)",
        value="organizations",
        help="ID del tenant Azure AD. 'organizations' funciona para la mayoría de los casos."
    )

    scan_type = st.radio(
        "Tipo de scan",
        ["Admin (tenant completo)", "Estándar (solo mis workspaces)"],
        help="Admin requiere permisos de administrador de Power BI. Estándar solo muestra los workspaces a los que tenés acceso."
    )

    col1, col2 = st.columns(2)
    start_scan = col1.button("Iniciar Scan", type="primary")
    if col2.button("Cancelar"):
        st.session_state.show_scan_dialog = False
        st.rerun()

    if start_scan:
        st.session_state.scan_in_progress = True
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(message, progress):
            progress_bar.progress(min(progress, 1.0))
            status_text.text(message)

        try:
            # Autenticar
            status_text.text("Abriendo ventana de autenticación...")
            auth = PBIAuthenticator(tenant_id=tenant_id)

            # Device code flow (más compatible con Streamlit)
            device_code_placeholder = st.empty()

            def show_device_code(message):
                device_code_placeholder.warning(message)

            if not auth.authenticate_device_code(callback=show_device_code):
                st.error("Error de autenticación. Verificar credenciales.")
                st.session_state.scan_in_progress = False
                return

            device_code_placeholder.empty()
            st.success("Autenticación exitosa!")

            # Escanear
            scanner = PBITenantScanner(auth)
            scanner.set_progress_callback(update_progress)

            is_admin = "Admin" in scan_type
            if is_admin:
                workspaces = scanner.scan_tenant()
            else:
                workspaces = scanner.scan_standard()

            if not workspaces:
                st.warning("No se encontraron workspaces.")
                st.session_state.scan_in_progress = False
                return

            # Guardar raw
            raw_file = scanner.save_raw_results()
            st.info(f"Backup guardado: {raw_file}")

            # Importar al catálogo
            status_text.text("Importando al catálogo...")
            catalog = st.session_state.catalog
            catalog.clear_catalog()
            scan_id = catalog.import_scan_results(
                workspaces,
                scan_type="admin" if is_admin else "standard",
                raw_file=raw_file,
                progress_callback=update_progress,
            )

            # Reinicializar search engine
            st.session_state.search_engine = CatalogSearch(catalog)

            stats = catalog.get_stats()
            st.success(
                f"Scan completado!\n\n"
                f"- {stats['workspaces']} workspaces\n"
                f"- {stats['reports']} reportes\n"
                f"- {stats['datasets']} datasets\n"
                f"- {stats['tables']} tablas\n"
                f"- {stats['measures']} medidas"
            )

        except Exception as e:
            st.error(f"Error durante el scan: {e}")
            logger.exception("Error en scan")
        finally:
            st.session_state.scan_in_progress = False
            st.session_state.show_scan_dialog = False


# ── Diálogo de Import JSON ─────────────────────────────────

def render_import_dialog():
    if not st.session_state.get("show_import_dialog"):
        return

    st.subheader("Importar resultados desde JSON")

    st.info(
        "Si ya tenés un archivo JSON de un scan previo (guardado en `output/`), "
        "podés importarlo directamente sin necesidad de re-escanear."
    )

    uploaded_file = st.file_uploader("Subir archivo JSON del scan", type=["json"])

    # También listar archivos existentes en output/
    output_dir = Path(__file__).parent / "output"
    json_files = sorted(output_dir.glob("scan_raw_*.json"), reverse=True) if output_dir.exists() else []

    selected_file = None
    if json_files:
        st.write("**O seleccionar un archivo existente:**")
        file_options = ["(ninguno)"] + [f.name for f in json_files]
        selected = st.selectbox("Archivos disponibles", file_options)
        if selected != "(ninguno)":
            selected_file = output_dir / selected

    col1, col2 = st.columns(2)
    if col1.button("Importar", type="primary"):
        import json

        try:
            if uploaded_file:
                data = json.loads(uploaded_file.read())
            elif selected_file:
                with open(selected_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                st.warning("Seleccioná un archivo para importar.")
                return

            workspaces = data.get("workspaces", [])
            if not workspaces:
                st.error("El archivo no contiene workspaces.")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(message, progress):
                progress_bar.progress(min(progress, 1.0))
                status_text.text(message)

            catalog = st.session_state.catalog
            catalog.clear_catalog()
            catalog.import_scan_results(
                workspaces,
                scan_type="imported",
                raw_file=str(selected_file) if selected_file else "uploaded",
                progress_callback=update_progress,
            )

            st.session_state.search_engine = CatalogSearch(catalog)
            stats = catalog.get_stats()
            st.success(
                f"Importación exitosa!\n\n"
                f"- {stats['workspaces']} workspaces, {stats['reports']} reportes, "
                f"{stats['datasets']} datasets, {stats['tables']} tablas"
            )
            st.session_state.show_import_dialog = False
            st.rerun()

        except Exception as e:
            st.error(f"Error importando: {e}")

    if col2.button("Cancelar"):
        st.session_state.show_import_dialog = False
        st.rerun()


# ── Diálogo Limpiar ────────────────────────────────────────

def render_clear_dialog():
    if not st.session_state.get("show_clear_dialog"):
        return

    st.warning("Estás seguro de que querés limpiar el catálogo? Se borrarán todos los datos escaneados.")
    col1, col2 = st.columns(2)
    if col1.button("Sí, limpiar", type="primary"):
        st.session_state.catalog.clear_catalog()
        st.session_state.search_engine = CatalogSearch(st.session_state.catalog)
        st.session_state.chat_history = []
        st.session_state.show_clear_dialog = False
        st.rerun()
    if col2.button("Cancelar "):
        st.session_state.show_clear_dialog = False
        st.rerun()


# ── Chat principal ─────────────────────────────────────────

def render_chat():
    st.title("Power BI Bot 2.0")
    st.caption("Preguntá sobre los reportes, datasets, dueños y tablas de tu tenant de Power BI")

    # Dialogs
    render_scan_dialog()
    render_import_dialog()
    render_clear_dialog()

    catalog = st.session_state.catalog
    if catalog.is_empty():
        st.info(
            "El catálogo está vacío. Para empezar:\n\n"
            "1. **Escanear Tenant**: Usá el botón en la barra lateral para escanear con tu usuario admin\n"
            "2. **Importar JSON**: Si ya tenés un archivo de scan previo, importalo desde la barra lateral\n\n"
            "Una vez cargado el catálogo, podés hacer preguntas como:\n"
            "- *¿Hay algún tablero de Serviclub?*\n"
            "- *¿Quién es el dueño del reporte de ventas?*\n"
            "- *¿Qué reportes usan la tabla DimClientes?*"
        )

    # Historial de chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Si hay datos extra, mostrar botón para expandir
            if msg.get("data") and msg["data"].get("results"):
                data = msg["data"]
                results = data["results"]
                if isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict):
                    with st.expander(f"Ver datos ({data.get('count', len(results))} resultados)"):
                        # Mostrar como tabla si es posible
                        import pandas as pd
                        try:
                            # Filtrar columnas relevantes
                            display_cols = ["name", "workspace", "workspace_name", "owner",
                                            "configured_by", "dataset_name", "web_url"]
                            df_data = []
                            for r in results[:50]:
                                row = {}
                                for col in display_cols:
                                    if col in r and r[col]:
                                        row[col] = r[col]
                                if row:
                                    df_data.append(row)
                            if df_data:
                                df = pd.DataFrame(df_data)
                                st.dataframe(df, use_container_width=True)
                        except Exception:
                            st.json(results[:10])

    # Input del chat
    if prompt := st.chat_input("Preguntá sobre tus reportes de Power BI..."):
        # Mostrar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Procesar búsqueda
        with st.chat_message("assistant"):
            if catalog.is_empty():
                response = "El catálogo está vacío. Primero necesitás escanear el tenant o importar un archivo JSON desde la barra lateral."
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                with st.spinner("Buscando..."):
                    result = st.session_state.search_engine.search(prompt)

                st.markdown(result["summary"])
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["summary"],
                    "data": result,
                })

                # Mostrar datos expandibles
                if result.get("results") and isinstance(result["results"], list):
                    results = result["results"]
                    if len(results) > 0 and isinstance(results[0], dict):
                        with st.expander(f"Ver datos ({result.get('count', len(results))} resultados)"):
                            import pandas as pd
                            try:
                                display_cols = ["name", "workspace", "workspace_name", "owner",
                                                "configured_by", "dataset_name", "web_url"]
                                df_data = []
                                for r in results[:50]:
                                    row = {}
                                    for col in display_cols:
                                        if col in r and r[col]:
                                            row[col] = r[col]
                                    if row:
                                        df_data.append(row)
                                if df_data:
                                    df = pd.DataFrame(df_data)
                                    st.dataframe(df, use_container_width=True)
                            except Exception:
                                st.json(results[:10])


# ── Main ───────────────────────────────────────────────────

def main():
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
else:
    main()
