"""
UI para Sistema de Favoritos
Interfaz para marcar y acceder a templates favoritos
"""

import streamlit as st
from typing import Optional, List
from core.favorites import FavoritesManager


def init_favorites_manager():
    """Inicializa el manager de favoritos si no existe"""
    if 'favorites_manager' not in st.session_state:
        st.session_state.favorites_manager = FavoritesManager()
    return st.session_state.favorites_manager


def show_favorite_button(template_id: str, template_name: str) -> bool:
    """
    Muestra botón para marcar/desmarcar favorito

    Args:
        template_id: ID del template
        template_name: Nombre del template

    Returns:
        True si es favorito después de la acción
    """
    manager = init_favorites_manager()
    is_fav = manager.is_favorite(template_id)

    icon = "⭐" if is_fav else "☆"
    label = f"{icon} Favorito" if is_fav else f"{icon} Marcar"

    if st.button(label, key=f"fav_btn_{template_id}", use_container_width=True):
        return manager.toggle_favorite(template_id, template_name)

    return is_fav


def show_favorites_sidebar():
    """
    Muestra favoritos en sidebar
    """
    manager = init_favorites_manager()
    favorites = manager.get_favorites()

    if not favorites:
        return

    st.markdown("---")
    st.markdown("### ⭐ Favoritos")

    # Obtener templates favoritos (necesitamos acceder al template manager)
    if 'template_manager' not in st.session_state:
        return

    tm = st.session_state.template_manager

    # Ordenar por más accedidos
    most_accessed = manager.get_most_accessed(limit=5)

    for template_id, access_count in most_accessed:
        template = tm.get_template(template_id)

        # También buscar en custom templates
        if not template and 'custom_template_manager' in st.session_state:
            custom_manager = st.session_state.custom_template_manager
            custom_template_data = custom_manager.get_template(template_id)
            if custom_template_data:
                template_name = custom_template_data['name']
            else:
                template_name = manager.metadata.get(template_id, {}).get('name', template_id)
        else:
            template_name = template.name if template else manager.metadata.get(template_id, {}).get('name', template_id)

        # Botón para usar
        if st.button(
            f"⭐ {template_name}",
            key=f"fav_sidebar_{template_id}",
            use_container_width=True
        ):
            st.session_state.selected_template_id = template_id
            st.session_state.template_step = 'parameters'
            st.session_state.show_template_ui = True

            # Incrementar contador
            manager.increment_access(template_id)

            # Determinar si es custom template
            if 'custom_template_manager' in st.session_state:
                custom_manager = st.session_state.custom_template_manager
                if custom_manager.get_template(template_id):
                    st.session_state.use_custom_template = True

            st.rerun()


def show_favorites_manager():
    """
    Muestra interfaz completa de gestión de favoritos
    """
    st.markdown("## ⭐ Gestión de Favoritos")

    manager = init_favorites_manager()
    stats = manager.get_stats()

    # Estadísticas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Templates Favoritos", stats['total'])

    with col2:
        st.metric("Accesos Totales", stats['total_access'])

    with col3:
        st.metric("Promedio Accesos", f"{stats['avg_access']:.1f}")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "⭐ Mis Favoritos",
        "📊 Estadísticas",
        "⚙️ Gestión"
    ])

    with tab1:
        _show_favorites_list(manager)

    with tab2:
        _show_favorites_stats(manager)

    with tab3:
        _show_favorites_management(manager)


def _show_favorites_list(manager: FavoritesManager):
    """Lista de favoritos"""
    st.markdown("### ⭐ Mis Templates Favoritos")

    favorites = manager.get_favorites()

    if not favorites:
        st.info("☆ No tienes favoritos todavía. Marca templates como favoritos para acceso rápido.")
        return

    # Ordenamiento
    sort_by = st.radio(
        "Ordenar por:",
        ["Más Accedidos", "Agregados Recientemente", "Nombre"],
        horizontal=True
    )

    if sort_by == "Más Accedidos":
        sorted_favorites = [fav_id for fav_id, _ in manager.get_most_accessed(limit=len(favorites))]
    elif sort_by == "Agregados Recientemente":
        sorted_favorites = manager.get_recently_added(limit=len(favorites))
    else:
        sorted_favorites = sorted(favorites)

    # Obtener managers
    tm = st.session_state.get('template_manager')
    custom_manager = st.session_state.get('custom_template_manager')

    # Mostrar favoritos
    for template_id in sorted_favorites:
        template = None
        is_custom = False

        # Buscar en templates estándar
        if tm:
            template = tm.get_template(template_id)

        # Buscar en custom templates
        if not template and custom_manager:
            custom_template_data = custom_manager.get_template(template_id)
            if custom_template_data:
                is_custom = True
                template = custom_template_data

        # Si no se encuentra, usar metadata
        if not template:
            template_name = manager.metadata.get(template_id, {}).get('name', template_id)
            template_desc = "Template no encontrado"
            template_category = "N/A"
        else:
            if is_custom:
                template_name = template['name']
                template_desc = template['description']
                template_category = template.get('category', 'Custom Templates')
            else:
                template_name = template.name
                template_desc = template.description
                template_category = template.category

        # Metadata de favorito
        metadata = manager.metadata.get(template_id, {})
        access_count = metadata.get('access_count', 0)
        added_at = metadata.get('added_at', 'Unknown')

        # Card del favorito
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                badge = "🎨 Custom" if is_custom else "📦 Standard"
                st.markdown(f"**⭐ {template_name}** {badge}")
                st.caption(f"📂 {template_category}")
                st.caption(template_desc[:100] + "..." if len(template_desc) > 100 else template_desc)
                st.caption(f"📊 Usado {access_count} veces")

            with col2:
                # Botón usar
                if st.button("📋 Usar", key=f"use_fav_{template_id}", use_container_width=True, type="primary"):
                    st.session_state.selected_template_id = template_id
                    st.session_state.template_step = 'parameters'
                    st.session_state.show_template_ui = True

                    if is_custom:
                        st.session_state.use_custom_template = True

                    manager.increment_access(template_id)
                    st.rerun()

                # Botón quitar
                if st.button("❌ Quitar", key=f"remove_fav_{template_id}", use_container_width=True):
                    manager.remove_favorite(template_id)
                    st.rerun()

            st.markdown("---")


def _show_favorites_stats(manager: FavoritesManager):
    """Estadísticas de favoritos"""
    st.markdown("### 📊 Estadísticas de Uso")

    # Top 10 más usados
    st.markdown("#### 🏆 Top 10 Más Accedidos")

    most_accessed = manager.get_most_accessed(limit=10)

    if most_accessed:
        for i, (template_id, count) in enumerate(most_accessed, 1):
            template_name = manager.metadata.get(template_id, {}).get('name', template_id)
            st.markdown(f"{i}. **{template_name}** - {count} acceso(s)")
    else:
        st.info("No hay datos de uso todavía")

    st.markdown("---")

    # Agregados recientemente
    st.markdown("#### 📅 Agregados Recientemente")

    recent = manager.get_recently_added(limit=5)

    for template_id in recent:
        metadata = manager.metadata.get(template_id, {})
        template_name = metadata.get('name', template_id)
        added_at = metadata.get('added_at', 'Unknown')

        # Formatear fecha
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(added_at)
            formatted_date = dt.strftime('%d/%m/%Y %H:%M')
        except:
            formatted_date = added_at

        st.markdown(f"- **{template_name}** (agregado {formatted_date})")


def _show_favorites_management(manager: FavoritesManager):
    """Opciones de gestión"""
    st.markdown("### ⚙️ Gestión de Favoritos")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📤 Exportar Favoritos")
        st.markdown("Exporta tus favoritos a un archivo JSON")

        if st.button("📦 Exportar", use_container_width=True):
            output_path = "output/favorites_export.json"
            if manager.export_favorites(output_path):
                st.success(f"✅ Favoritos exportados a {output_path}")

                # Ofrecer descarga
                with open(output_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        "⬇️ Descargar Archivo",
                        f.read(),
                        file_name="favorites_export.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.error("❌ Error al exportar")

    with col2:
        st.markdown("#### 📥 Importar Favoritos")
        st.markdown("Importa favoritos desde un archivo JSON")

        uploaded_file = st.file_uploader(
            "Selecciona archivo",
            type=['json'],
            key="import_favorites_file"
        )

        if uploaded_file:
            merge = st.checkbox("Combinar con favoritos existentes", value=True)

            if st.button("📥 Importar", use_container_width=True):
                import tempfile
                import os

                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # Importar
                if manager.import_favorites(tmp_path, merge=merge):
                    st.success("✅ Favoritos importados!")
                    st.rerun()
                else:
                    st.error("❌ Error al importar")

                # Limpiar
                os.unlink(tmp_path)

    st.markdown("---")

    # Limpiar favoritos
    st.markdown("#### 🗑️ Limpiar Favoritos")
    st.warning("⚠️ Esta acción eliminará todos tus favoritos")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Eliminar Todos", use_container_width=True):
            st.session_state.confirm_clear_favorites = True

    with col2:
        if st.session_state.get('confirm_clear_favorites', False):
            if st.button("✅ Confirmar Eliminación", use_container_width=True, type="primary"):
                manager.clear_favorites()
                st.session_state.confirm_clear_favorites = False
                st.success("✅ Favoritos eliminados")
                st.rerun()


def show_favorite_indicator(template_id: str) -> str:
    """
    Muestra indicador de favorito (estrella)

    Args:
        template_id: ID del template

    Returns:
        Emoji de estrella si es favorito, vacío si no
    """
    manager = init_favorites_manager()
    return "⭐" if manager.is_favorite(template_id) else ""
