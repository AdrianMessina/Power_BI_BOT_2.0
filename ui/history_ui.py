"""
UI para Historial de Medidas
Componentes de Streamlit para ver y gestionar el historial
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from core.measure_history import MeasureHistory, MeasureHistoryEntry


def show_history_sidebar():
    """
    Muestra panel lateral con historial de medidas
    """
    if 'measure_history' not in st.session_state:
        st.session_state.measure_history = MeasureHistory()

    history = st.session_state.measure_history

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📜 Historial de Medidas")

        entries = history.get_recent(5)

        if not entries:
            st.caption("No hay medidas en el historial")
            return

        for i, entry in enumerate(entries):
            with st.expander(f"📊 {entry.measure_name[:30]}...", expanded=False):
                st.caption(f"**Template:** {entry.template_name}")
                st.caption(f"**Fecha:** {entry.timestamp[:16]}")

                status_icon = "✅" if entry.applied else "📋"
                status_text = "Aplicada" if entry.applied else "Copiada"
                st.caption(f"**Estado:** {status_icon} {status_text}")

                if st.button("🔄 Reutilizar", key=f"reuse_history_{i}"):
                    # Cargar parámetros en el workflow
                    st.session_state.show_template_ui = True
                    st.session_state.template_step = 'parameters'
                    st.session_state.selected_template_id = entry.template_id
                    st.session_state.template_params = entry.parameters
                    st.rerun()

        if st.button("📂 Ver Todo el Historial", use_container_width=True):
            st.session_state.show_full_history = True
            st.rerun()


def show_full_history():
    """
    Muestra historial completo en página principal
    """
    if 'measure_history' not in st.session_state:
        st.session_state.measure_history = MeasureHistory()

    history = st.session_state.measure_history

    st.markdown("## 📜 Historial Completo de Medidas")

    # Estadísticas
    stats = history.get_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Medidas", stats['total'])
    with col2:
        st.metric("Aplicadas", stats['applied'])
    with col3:
        st.metric("Copiadas", stats['copied'])
    with col4:
        st.metric("Categorías", len(stats['by_category']))

    st.markdown("---")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input(
            "🔍 Buscar",
            placeholder="Nombre de medida o código...",
            key="history_search"
        )

    with col2:
        categories = list(stats['by_category'].keys())
        category_filter = st.selectbox(
            "📁 Categoría",
            ["Todas"] + categories,
            key="history_category_filter"
        )

    with col3:
        show_only = st.selectbox(
            "📊 Mostrar",
            ["Todas", "Solo Aplicadas", "Solo Copiadas"],
            key="history_show_filter"
        )

    # Aplicar filtros
    entries = history.get_all()

    if search_query:
        entries = history.search(search_query)

    if category_filter != "Todas":
        entries = [e for e in entries if e.category == category_filter]

    if show_only == "Solo Aplicadas":
        entries = [e for e in entries if e.applied]
    elif show_only == "Solo Copiadas":
        entries = [e for e in entries if not e.applied]

    st.markdown(f"### Resultados ({len(entries)} medidas)")

    # Botones de acción
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Exportar Todo", use_container_width=True):
            export_all_history(history)
    with col2:
        if st.button("🔄 Refrescar", use_container_width=True):
            st.rerun()
    with col3:
        if len(entries) > 0 and st.button("🗑️ Limpiar Historial", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                history.clear_history()
                st.success("Historial limpiado")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Haz clic nuevamente para confirmar")

    st.markdown("---")

    # Mostrar entradas
    if not entries:
        st.info("No hay medidas que coincidan con los filtros")
        return

    for i, entry in enumerate(entries):
        show_history_entry(entry, i)


def show_history_entry(entry: MeasureHistoryEntry, index: int):
    """
    Muestra una entrada individual del historial

    Args:
        entry: Entrada a mostrar
        index: Índice de la entrada
    """
    # Contenedor con borde
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### 📊 {entry.measure_name}")

        with col2:
            status_icon = "✅" if entry.applied else "📋"
            status_text = "Aplicada al modelo" if entry.applied else "Solo copiada"
            st.caption(f"{status_icon} {status_text}")

        with col3:
            timestamp_dt = datetime.fromisoformat(entry.timestamp)
            st.caption(timestamp_dt.strftime("%Y-%m-%d %H:%M"))

        # Info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"**Template:** {entry.template_name}")
        with col2:
            st.caption(f"**Categoría:** {entry.category}")
        with col3:
            st.caption(f"**ID:** {entry.template_id}")

        # Código DAX
        with st.expander("📄 Ver Código DAX", expanded=False):
            st.code(entry.dax_code, language="dax")

        # Parámetros
        with st.expander("⚙️ Ver Parámetros", expanded=False):
            for key, value in entry.parameters.items():
                st.text(f"{key}: {value}")

        # Notas
        if entry.notes:
            with st.expander("📝 Notas", expanded=False):
                st.text(entry.notes)

        # Acciones
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Reutilizar", key=f"reuse_{index}", use_container_width=True):
                reutilize_measure(entry)

        with col2:
            if st.button("📋 Copiar Código", key=f"copy_{index}", use_container_width=True):
                st.session_state[f'clipboard_{index}'] = entry.dax_code
                st.success("Código copiado!")

        with col3:
            if st.button("💾 Exportar", key=f"export_{index}", use_container_width=True):
                export_single_entry(entry, index)

        with col4:
            if st.button("🗑️", key=f"delete_{index}", use_container_width=True):
                delete_entry(index)

        st.markdown("---")


def reutilize_measure(entry: MeasureHistoryEntry):
    """
    Reutiliza una medida del historial

    Args:
        entry: Entrada a reutilizar
    """
    # Activar workflow con los parámetros guardados
    st.session_state.show_template_ui = True
    st.session_state.template_step = 'parameters'
    st.session_state.selected_template_id = entry.template_id
    st.session_state.template_params = entry.parameters.copy()
    st.session_state.show_full_history = False

    st.success(f"Cargando template '{entry.template_name}' con parámetros guardados")
    st.rerun()


def export_single_entry(entry: MeasureHistoryEntry, index: int):
    """
    Exporta una entrada individual a archivo

    Args:
        entry: Entrada a exportar
        index: Índice de la entrada
    """
    history = st.session_state.measure_history

    # Nombre de archivo seguro
    safe_name = "".join(c for c in entry.measure_name if c.isalnum() or c in (' ', '-', '_'))
    filename = f"output/{safe_name}_{index}.dax"

    try:
        history.export_entry_to_file(entry, filename)
        st.success(f"Exportado a: {filename}")

        # Mostrar contenido
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        with st.expander("📄 Ver archivo exportado"):
            st.code(content, language="dax")

    except Exception as e:
        st.error(f"Error al exportar: {e}")


def export_all_history(history: MeasureHistory):
    """
    Exporta todo el historial a un archivo

    Args:
        history: Instancia de MeasureHistory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/historial_completo_{timestamp}.dax"

    try:
        history.export_all_to_file(filename)
        st.success(f"Historial completo exportado a: {filename}")

        # Botón para descargar
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        st.download_button(
            label="⬇️ Descargar Archivo",
            data=content,
            file_name=f"historial_completo_{timestamp}.dax",
            mime="text/plain",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error al exportar: {e}")


def delete_entry(index: int):
    """
    Elimina una entrada del historial

    Args:
        index: Índice de la entrada
    """
    history = st.session_state.measure_history

    if st.session_state.get(f'confirm_delete_{index}', False):
        history.delete_entry(index)
        st.success("Entrada eliminada")
        st.session_state[f'confirm_delete_{index}'] = False
        st.rerun()
    else:
        st.session_state[f'confirm_delete_{index}'] = True
        st.warning("Haz clic nuevamente en 🗑️ para confirmar")


def add_to_history(
    measure_name: str,
    template_id: str,
    template_name: str,
    dax_code: str,
    parameters: dict,
    category: str,
    applied: bool = False,
    notes: str = ""
):
    """
    Agrega una medida al historial

    Args:
        measure_name: Nombre de la medida
        template_id: ID del template
        template_name: Nombre del template
        dax_code: Código DAX
        parameters: Parámetros usados
        category: Categoría
        applied: Si se aplicó al modelo
        notes: Notas adicionales
    """
    if 'measure_history' not in st.session_state:
        st.session_state.measure_history = MeasureHistory()

    history = st.session_state.measure_history

    history.add_entry(
        measure_name=measure_name,
        template_id=template_id,
        template_name=template_name,
        dax_code=dax_code,
        parameters=parameters,
        category=category,
        applied=applied,
        notes=notes
    )
