"""
UI para Gestión de Templates Personalizados
Interfaz completa para crear, editar y gestionar templates custom
"""

import streamlit as st
from typing import Optional, List, Dict
from core.custom_templates import CustomTemplateManager


def show_custom_template_manager():
    """
    Muestra interfaz completa de gestión de templates personalizados
    """
    st.markdown("## 🎨 Gestor de Templates Personalizados")

    # Inicializar manager si no existe
    if 'custom_template_manager' not in st.session_state:
        st.session_state.custom_template_manager = CustomTemplateManager()

    manager = st.session_state.custom_template_manager

    # Estadísticas
    stats = manager.get_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Templates Custom", stats['total'])
    with col2:
        st.metric("Usos Totales", stats['total_usage'])
    with col3:
        most_used_category = max(stats['by_category'].items(), key=lambda x: x[1])[0] if stats['by_category'] else 'N/A'
        st.metric("Categoría Popular", most_used_category)

    st.markdown("---")

    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Crear Nuevo",
        "📋 Mis Templates",
        "📤 Import/Export",
        "📊 Estadísticas"
    ])

    with tab1:
        _show_create_template_form(manager)

    with tab2:
        _show_template_list(manager)

    with tab3:
        _show_import_export(manager)

    with tab4:
        _show_template_stats(manager)


def _show_create_template_form(manager: CustomTemplateManager):
    """Formulario para crear nuevo template"""
    st.markdown("### ➕ Crear Nuevo Template")

    with st.form("create_template_form"):
        # Información básica
        st.markdown("#### 📝 Información Básica")

        col1, col2 = st.columns(2)

        with col1:
            template_id = st.text_input(
                "ID del Template *",
                placeholder="ej: custom_my_measure",
                help="ID único del template (sin espacios)"
            )

            name = st.text_input(
                "Nombre del Template *",
                placeholder="ej: Mi Medida Personalizada"
            )

            category = st.selectbox(
                "Categoría",
                ["Custom Templates", "YPF Custom", "Calculations", "Time Intelligence", "Advanced"],
                index=0
            )

        with col2:
            difficulty = st.selectbox(
                "Nivel de Dificultad",
                ["basic", "intermediate", "advanced"],
                index=1
            )

            author = st.text_input(
                "Autor",
                value="User",
                placeholder="Tu nombre"
            )

            requires_date = st.checkbox("Requiere Tabla de Fechas")

        description = st.text_area(
            "Descripción *",
            placeholder="Describe qué hace este template...",
            height=80
        )

        # Tags
        tags_input = st.text_input(
            "Tags (separados por coma)",
            placeholder="ej: ventas, kpi, margen"
        )

        st.markdown("---")
        st.markdown("#### 💻 Código DAX")

        template_code = st.text_area(
            "Código del Template *",
            placeholder="""Ejemplo:
{measure_name} =
CALCULATE(
    SUM({column}),
    {filter_condition}
)""",
            height=150,
            help="Usa {parameter_name} como placeholders para los parámetros"
        )

        example = st.text_area(
            "Ejemplo de Uso",
            placeholder="""Ejemplo:
Total Ventas Filtrado =
CALCULATE(
    SUM(Ventas[Importe]),
    Ventas[Categoria] = "A"
)""",
            height=100
        )

        st.markdown("---")
        st.markdown("#### ⚙️ Parámetros")

        # Cantidad de parámetros
        num_params = st.number_input("Número de parámetros", min_value=1, max_value=10, value=2)

        parameters = []
        for i in range(num_params):
            with st.expander(f"Parámetro {i+1}", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    param_name = st.text_input(
                        "Nombre",
                        key=f"param_name_{i}",
                        placeholder="ej: measure_name"
                    )

                with col2:
                    param_type = st.selectbox(
                        "Tipo",
                        ["text", "measure", "table", "column", "date_column"],
                        key=f"param_type_{i}"
                    )

                with col3:
                    param_required = st.checkbox(
                        "Requerido",
                        value=True,
                        key=f"param_required_{i}"
                    )

                param_desc = st.text_input(
                    "Descripción",
                    key=f"param_desc_{i}",
                    placeholder="Describe este parámetro..."
                )

                if param_name and param_desc:
                    parameters.append({
                        'name': param_name,
                        'type': param_type,
                        'description': param_desc,
                        'required': param_required
                    })

        # Botones
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("✅ Crear Template", use_container_width=True, type="primary")

        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

        if cancel:
            st.rerun()

        if submitted:
            # Validar campos requeridos
            if not template_id or not name or not description or not template_code:
                st.error("❌ Completa todos los campos obligatorios (*)")
                return

            if not parameters:
                st.error("❌ Debes definir al menos un parámetro")
                return

            # Validar ID
            if ' ' in template_id:
                st.error("❌ El ID no puede contener espacios")
                return

            # Crear tags
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

            # Crear template
            success = manager.create_template(
                template_id=template_id,
                name=name,
                description=description,
                category=category,
                template_code=template_code,
                parameters=parameters,
                difficulty=difficulty,
                tags=tags,
                example=example,
                requires_date_table=requires_date,
                author=author
            )

            if success:
                st.success(f"✅ Template '{name}' creado exitosamente!")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ Error: Template con ID '{template_id}' ya existe")


def _show_template_list(manager: CustomTemplateManager):
    """Lista de templates personalizados"""
    st.markdown("### 📋 Mis Templates Personalizados")

    templates = manager.list_templates()

    if not templates:
        st.info("📝 No tienes templates personalizados todavía. ¡Crea uno en la pestaña 'Crear Nuevo'!")
        return

    # Búsqueda
    search_query = st.text_input("🔎 Buscar template", placeholder="Nombre, descripción o tag...")

    if search_query:
        templates = manager.search_templates(search_query)

    # Mostrar templates
    for template in sorted(templates, key=lambda t: t['name']):
        with st.expander(f"**{template['name']}** ({template['id']})", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Descripción:** {template['description']}")
                st.markdown(f"**Categoría:** {template['category']}")
                st.markdown(f"**Dificultad:** {template['difficulty']}")
                st.markdown(f"**Tags:** {', '.join(template.get('tags', []))}")
                st.markdown(f"**Autor:** {template['metadata']['author']}")
                st.markdown(f"**Versión:** {template['metadata']['version']}")
                st.markdown(f"**Usos:** {template['metadata']['usage_count']}")

                # Código
                st.markdown("**Código:**")
                st.code(template['template_code'], language="dax")

                # Parámetros
                st.markdown("**Parámetros:**")
                for param in template['parameters']:
                    required = " *" if param.get('required', True) else ""
                    st.markdown(f"- `{param['name']}` ({param['type']}): {param['description']}{required}")

            with col2:
                # Botones de acción
                if st.button("✏️ Editar", key=f"edit_{template['id']}", use_container_width=True):
                    st.session_state['editing_template'] = template['id']
                    st.rerun()

                if st.button("📤 Exportar", key=f"export_{template['id']}", use_container_width=True):
                    output_path = f"output/{template['id']}.json"
                    if manager.export_template(template['id'], output_path):
                        st.success(f"✅ Exportado a {output_path}")
                    else:
                        st.error("❌ Error al exportar")

                if st.button("🗑️ Eliminar", key=f"delete_{template['id']}", use_container_width=True):
                    if manager.delete_template(template['id']):
                        st.success("✅ Template eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar")

                if st.button("📋 Usar", key=f"use_{template['id']}", use_container_width=True, type="primary"):
                    # Ir a workflow con este template
                    st.session_state.selected_template_id = template['id']
                    st.session_state.template_step = 'parameters'
                    st.session_state.show_template_ui = True
                    st.session_state.use_custom_template = True
                    st.rerun()

    # Mostrar formulario de edición si está activo
    if st.session_state.get('editing_template'):
        _show_edit_template_form(manager, st.session_state.editing_template)


def _show_edit_template_form(manager: CustomTemplateManager, template_id: str):
    """Formulario para editar template existente"""
    template = manager.get_template(template_id)
    if not template:
        st.error("❌ Template no encontrado")
        st.session_state.editing_template = None
        return

    st.markdown(f"### ✏️ Editando: {template['name']}")

    with st.form("edit_template_form"):
        # Información básica
        name = st.text_input("Nombre", value=template['name'])
        description = st.text_area("Descripción", value=template['description'])
        category = st.selectbox(
            "Categoría",
            ["Custom Templates", "YPF Custom", "Calculations", "Time Intelligence", "Advanced"],
            index=["Custom Templates", "YPF Custom", "Calculations", "Time Intelligence", "Advanced"].index(
                template.get('category', 'Custom Templates')
            )
        )
        difficulty = st.selectbox(
            "Dificultad",
            ["basic", "intermediate", "advanced"],
            index=["basic", "intermediate", "advanced"].index(template.get('difficulty', 'intermediate'))
        )

        template_code = st.text_area("Código", value=template['template_code'], height=150)
        example = st.text_area("Ejemplo", value=template.get('example', ''), height=100)

        tags_str = ', '.join(template.get('tags', []))
        tags_input = st.text_input("Tags", value=tags_str)

        # Botones
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary"):
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

                success = manager.update_template(
                    template_id,
                    name=name,
                    description=description,
                    category=category,
                    difficulty=difficulty,
                    template_code=template_code,
                    example=example,
                    tags=tags
                )

                if success:
                    st.success("✅ Template actualizado!")
                    st.session_state.editing_template = None
                    st.rerun()
                else:
                    st.error("❌ Error al actualizar")

        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.editing_template = None
                st.rerun()


def _show_import_export(manager: CustomTemplateManager):
    """UI para import/export de templates"""
    st.markdown("### 📤 Import/Export de Templates")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📥 Importar Template")
        uploaded_file = st.file_uploader(
            "Selecciona archivo JSON",
            type=['json'],
            key="import_template_file"
        )

        if uploaded_file:
            if st.button("📥 Importar", use_container_width=True, type="primary"):
                # Guardar temporalmente
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # Importar
                template_id = manager.import_template(tmp_path)

                # Limpiar
                import os
                os.unlink(tmp_path)

                if template_id:
                    st.success(f"✅ Template importado: {template_id}")
                    st.rerun()
                else:
                    st.error("❌ Error al importar template. Verifica el formato del archivo.")

    with col2:
        st.markdown("#### 📤 Exportar Todos")
        st.markdown("Exporta todos tus templates a un archivo JSON")

        if st.button("📦 Exportar Todos", use_container_width=True):
            import json
            import tempfile

            output_data = {
                'templates': list(manager.templates.values()),
                'exported_at': manager.templates.get('last_updated', 'unknown')
            }

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8') as tmp:
                json.dump(output_data, tmp, indent=2, ensure_ascii=False)
                tmp_path = tmp.name

            # Leer y ofrecer descarga
            with open(tmp_path, 'r', encoding='utf-8') as f:
                st.download_button(
                    "⬇️ Descargar Archivo",
                    f.read(),
                    file_name="custom_templates_export.json",
                    mime="application/json",
                    use_container_width=True
                )

            # Limpiar
            import os
            os.unlink(tmp_path)


def _show_template_stats(manager: CustomTemplateManager):
    """Estadísticas detalladas"""
    st.markdown("### 📊 Estadísticas Detalladas")

    stats = manager.get_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Templates", stats['total'])

    with col2:
        st.metric("Usos Totales", stats['total_usage'])

    with col3:
        avg_usage = stats['total_usage'] / stats['total'] if stats['total'] > 0 else 0
        st.metric("Promedio de Uso", f"{avg_usage:.1f}")

    st.markdown("---")

    # Por categoría
    if stats['by_category']:
        st.markdown("#### 📁 Por Categoría")
        for category, count in stats['by_category'].items():
            st.markdown(f"- **{category}:** {count} template(s)")

    st.markdown("---")

    # Por dificultad
    st.markdown("#### 📊 Por Dificultad")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 Básico", stats['by_difficulty']['basic'])
    with col2:
        st.metric("🟡 Intermedio", stats['by_difficulty']['intermediate'])
    with col3:
        st.metric("🔴 Avanzado", stats['by_difficulty']['advanced'])

    st.markdown("---")

    # Templates más usados
    st.markdown("#### 🏆 Templates Más Usados")
    templates = manager.list_templates()
    if templates:
        sorted_templates = sorted(
            templates,
            key=lambda t: t['metadata']['usage_count'],
            reverse=True
        )[:5]

        for i, template in enumerate(sorted_templates, 1):
            usage = template['metadata']['usage_count']
            st.markdown(f"{i}. **{template['name']}** - {usage} uso(s)")
    else:
        st.info("No hay datos de uso todavía")


def show_custom_template_quick_access():
    """
    Acceso rápido a templates custom para sidebar
    """
    if 'custom_template_manager' not in st.session_state:
        st.session_state.custom_template_manager = CustomTemplateManager()

    manager = st.session_state.custom_template_manager
    templates = manager.list_templates()

    if not templates:
        return

    st.markdown("#### 🎨 Mis Templates")

    # Mostrar últimos 5
    recent_templates = sorted(
        templates,
        key=lambda t: t['metadata']['updated_at'],
        reverse=True
    )[:5]

    for template in recent_templates:
        if st.button(
            f"📝 {template['name']}",
            key=f"quick_custom_{template['id']}",
            use_container_width=True
        ):
            st.session_state.selected_template_id = template['id']
            st.session_state.template_step = 'parameters'
            st.session_state.show_template_ui = True
            st.session_state.use_custom_template = True
            st.rerun()
