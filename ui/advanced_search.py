"""
UI de Búsqueda Avanzada de Templates
Componente con filtros múltiples, ordenamiento y preview
"""

import streamlit as st
from typing import List, Dict, Optional
from templates import TemplateManager
from templates.base_template import DAXTemplate


class AdvancedTemplateSearch:
    """
    Sistema de búsqueda avanzada de templates con filtros múltiples
    """

    def __init__(self, template_manager: TemplateManager):
        self.tm = template_manager

    def show_search_interface(self) -> Optional[str]:
        """
        Muestra interfaz completa de búsqueda avanzada

        Returns:
            template_id seleccionado o None
        """
        st.markdown("### 🔍 Búsqueda Avanzada de Templates")

        # Inicializar estado de búsqueda
        if 'search_filters' not in st.session_state:
            st.session_state.search_filters = {
                'text': '',
                'categories': [],
                'difficulties': [],
                'requires_date': None,
                'tags': [],
                'sort_by': 'name'
            }

        # Panel de filtros
        with st.expander("⚙️ Filtros de Búsqueda", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                # Búsqueda de texto
                text_query = st.text_input(
                    "🔎 Buscar por nombre o descripción:",
                    value=st.session_state.search_filters['text'],
                    placeholder="Ej: YTD, suma, margen...",
                    key="search_text_input"
                )
                st.session_state.search_filters['text'] = text_query

                # Filtro por categoría
                all_categories = self.tm.get_categories()
                selected_categories = st.multiselect(
                    "📂 Categorías:",
                    all_categories,
                    default=st.session_state.search_filters['categories'],
                    key="search_categories"
                )
                st.session_state.search_filters['categories'] = selected_categories

            with col2:
                # Filtro por dificultad
                difficulties = ['basic', 'intermediate', 'advanced']
                difficulty_labels = {
                    'basic': '🟢 Básico',
                    'intermediate': '🟡 Intermedio',
                    'advanced': '🔴 Avanzado'
                }

                selected_difficulties = st.multiselect(
                    "📊 Nivel de Dificultad:",
                    difficulties,
                    format_func=lambda x: difficulty_labels[x],
                    default=st.session_state.search_filters['difficulties'],
                    key="search_difficulties"
                )
                st.session_state.search_filters['difficulties'] = selected_difficulties

                # Filtro tabla de fechas
                requires_date_options = {
                    'Cualquiera': None,
                    'Solo con tabla de fechas': True,
                    'Sin tabla de fechas': False
                }

                date_requirement = st.selectbox(
                    "📅 Requiere Tabla de Fechas:",
                    list(requires_date_options.keys()),
                    index=0,
                    key="search_date_req"
                )
                st.session_state.search_filters['requires_date'] = requires_date_options[date_requirement]

            # Opciones de ordenamiento
            col3, col4 = st.columns(2)
            with col3:
                sort_options = {
                    'Nombre (A-Z)': 'name',
                    'Categoría': 'category',
                    'Dificultad': 'difficulty',
                    'Más Usados': 'usage'
                }

                sort_by = st.selectbox(
                    "📋 Ordenar por:",
                    list(sort_options.keys()),
                    index=0,
                    key="search_sort"
                )
                st.session_state.search_filters['sort_by'] = sort_options[sort_by]

            with col4:
                # Botón limpiar filtros
                if st.button("🗑️ Limpiar Filtros", use_container_width=True):
                    st.session_state.search_filters = {
                        'text': '',
                        'categories': [],
                        'difficulties': [],
                        'requires_date': None,
                        'tags': [],
                        'sort_by': 'name'
                    }
                    st.rerun()

        # Aplicar filtros y obtener resultados
        results = self._apply_filters()

        # Mostrar resultados
        st.markdown("---")
        st.markdown(f"### 📋 Resultados ({len(results)} templates)")

        if not results:
            st.info("🔍 No se encontraron templates que coincidan con los filtros.")
            st.markdown("💡 **Sugerencia:** Intenta reducir o cambiar los filtros.")
            return None

        # Mostrar templates
        selected_template_id = self._show_template_results(results)

        return selected_template_id

    def _apply_filters(self) -> List[DAXTemplate]:
        """
        Aplica filtros actuales y retorna templates filtrados
        """
        filters = st.session_state.search_filters
        templates = self.tm.list_all_templates()

        # Filtro de texto
        if filters['text']:
            templates = self.tm.search(filters['text'])

        # Filtro por categoría
        if filters['categories']:
            templates = [t for t in templates if t.category in filters['categories']]

        # Filtro por dificultad
        if filters['difficulties']:
            templates = [t for t in templates if t.difficulty in filters['difficulties']]

        # Filtro por tabla de fechas
        if filters['requires_date'] is not None:
            templates = [t for t in templates if t.requires_date_table == filters['requires_date']]

        # Ordenamiento
        sort_by = filters['sort_by']
        if sort_by == 'name':
            templates = sorted(templates, key=lambda t: t.name.lower())
        elif sort_by == 'category':
            templates = sorted(templates, key=lambda t: (t.category, t.name.lower()))
        elif sort_by == 'difficulty':
            difficulty_order = {'basic': 0, 'intermediate': 1, 'advanced': 2}
            templates = sorted(templates, key=lambda t: (
                difficulty_order.get(t.difficulty, 999),
                t.name.lower()
            ))
        elif sort_by == 'usage':
            # Si tenemos historial, ordenar por uso
            if hasattr(st.session_state, 'measure_history'):
                usage_stats = self._get_usage_stats()
                templates = sorted(
                    templates,
                    key=lambda t: usage_stats.get(t.id, 0),
                    reverse=True
                )
            else:
                templates = sorted(templates, key=lambda t: t.name.lower())

        return templates

    def _get_usage_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de uso de templates desde el historial
        """
        usage = {}
        if hasattr(st.session_state, 'measure_history'):
            history = st.session_state.measure_history
            all_entries = history.get_all_entries()

            for entry in all_entries:
                template_id = entry.template_id
                usage[template_id] = usage.get(template_id, 0) + 1

        return usage

    def _show_template_results(self, templates: List[DAXTemplate]) -> Optional[str]:
        """
        Muestra resultados de búsqueda con preview
        """
        # Vista en grid o lista
        view_mode = st.radio(
            "Vista:",
            ["🔲 Grid", "📃 Lista Detallada"],
            horizontal=True,
            key="search_view_mode"
        )

        if view_mode == "🔲 Grid":
            return self._show_grid_view(templates)
        else:
            return self._show_list_view(templates)

    def _show_grid_view(self, templates: List[DAXTemplate]) -> Optional[str]:
        """
        Muestra templates en vista de grid (3 columnas)
        """
        # Mostrar en grupos de 3
        for i in range(0, len(templates), 3):
            cols = st.columns(3)
            batch = templates[i:i+3]

            for idx, template in enumerate(batch):
                with cols[idx]:
                    if self._show_template_card(template):
                        return template.id

        return None

    def _show_list_view(self, templates: List[DAXTemplate]) -> Optional[str]:
        """
        Muestra templates en vista de lista detallada
        """
        for template in templates:
            if self._show_template_detailed(template):
                return template.id

        return None

    def _show_template_card(self, template: DAXTemplate) -> bool:
        """
        Muestra una tarjeta de template (vista compacta)
        """
        # Iconos
        difficulty_icon = {
            'basic': '🟢',
            'intermediate': '🟡',
            'advanced': '🔴'
        }
        icon = difficulty_icon.get(template.difficulty, '⚪')
        date_icon = ' 📅' if template.requires_date_table else ''

        # Tarjeta
        with st.container():
            st.markdown(f"**{icon} {template.name}**{date_icon}")
            st.caption(template.category)
            st.caption(template.description[:80] + "..." if len(template.description) > 80 else template.description)

            # Botón seleccionar
            if st.button(
                "✅ Seleccionar",
                key=f"select_card_{template.id}",
                use_container_width=True
            ):
                return True

            # Botón preview
            if st.button(
                "👁️ Preview",
                key=f"preview_card_{template.id}",
                use_container_width=True
            ):
                st.session_state[f'show_preview_{template.id}'] = True

            # Mostrar preview si se solicitó
            if st.session_state.get(f'show_preview_{template.id}', False):
                with st.expander("📖 Detalles", expanded=True):
                    st.markdown(f"**Descripción:** {template.description}")
                    st.markdown(f"**Dificultad:** {template.difficulty}")
                    st.markdown(f"**Tags:** {', '.join(template.tags)}")
                    st.markdown("**Ejemplo:**")
                    st.code(template.example, language="dax")

                    if st.button("❌ Cerrar", key=f"close_preview_{template.id}"):
                        st.session_state[f'show_preview_{template.id}'] = False
                        st.rerun()

            st.markdown("---")

        return False

    def _show_template_detailed(self, template: DAXTemplate) -> bool:
        """
        Muestra template en formato detallado
        """
        # Iconos
        difficulty_icon = {
            'basic': '🟢',
            'intermediate': '🟡',
            'advanced': '🔴'
        }
        icon = difficulty_icon.get(template.difficulty, '⚪')
        date_icon = ' 📅' if template.requires_date_table else ''

        # Contenedor expandible
        with st.expander(f"{icon} {template.name}{date_icon}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Categoría:** {template.category}")
                st.markdown(f"**Descripción:** {template.description}")
                st.markdown(f"**Dificultad:** {template.difficulty}")
                st.markdown(f"**Tags:** {', '.join(template.tags)}")

                # Parámetros
                st.markdown("**Parámetros requeridos:**")
                for param in template.parameters:
                    required = " *" if param.required else ""
                    st.markdown(f"- `{param.name}` ({param.type}): {param.description}{required}")

                # Ejemplo
                st.markdown("**Ejemplo:**")
                st.code(template.example, language="dax")

            with col2:
                if st.button(
                    "✅ Usar este Template",
                    key=f"select_detail_{template.id}",
                    use_container_width=True,
                    type="primary"
                ):
                    return True

                # Estadísticas de uso
                if hasattr(st.session_state, 'measure_history'):
                    usage_stats = self._get_usage_stats()
                    usage_count = usage_stats.get(template.id, 0)
                    if usage_count > 0:
                        st.metric("Veces usado", usage_count)

        return False


def show_advanced_search() -> Optional[str]:
    """
    Función helper para mostrar búsqueda avanzada

    Returns:
        template_id seleccionado o None
    """
    if 'template_manager' not in st.session_state:
        st.error("Template Manager no inicializado")
        return None

    search = AdvancedTemplateSearch(st.session_state.template_manager)
    return search.show_search_interface()


def show_quick_search(placeholder: str = "Buscar template...") -> Optional[str]:
    """
    Búsqueda rápida simplificada para sidebar

    Args:
        placeholder: Texto del placeholder

    Returns:
        template_id si se selecciona algo, None si no
    """
    if 'template_manager' not in st.session_state:
        return None

    tm = st.session_state.template_manager

    # Input de búsqueda
    query = st.text_input(
        "🔎",
        placeholder=placeholder,
        key="quick_search_input",
        label_visibility="collapsed"
    )

    if query and len(query) >= 2:
        # Buscar
        results = tm.search(query)

        if results:
            st.caption(f"{len(results)} resultado(s):")

            # Mostrar primeros 5 resultados
            for template in results[:5]:
                difficulty_icon = {
                    'basic': '🟢',
                    'intermediate': '🟡',
                    'advanced': '🔴'
                }
                icon = difficulty_icon.get(template.difficulty, '⚪')

                if st.button(
                    f"{icon} {template.name}",
                    key=f"quick_{template.id}",
                    use_container_width=True
                ):
                    return template.id

            if len(results) > 5:
                st.caption(f"... y {len(results) - 5} más")
        else:
            st.caption("No se encontraron resultados")

    return None
