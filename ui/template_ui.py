"""
UI Components para Templates DAX
Componentes de Streamlit reutilizables para el sistema de templates
"""

import streamlit as st
from typing import Optional, Dict, List
from templates import TemplateManager
from templates.parameter_validator import ParameterValidator, format_parameter_help
from utils.clipboard_helper import clipboard_button, multi_clipboard_options
from utils.export_helper import show_export_options


def show_template_selector(suggestions: List = None) -> Optional[str]:
    """
    Muestra selector de templates

    Args:
        suggestions: Lista de templates sugeridos (opcional)

    Returns:
        ID del template seleccionado o None
    """
    tm = st.session_state.template_manager

    st.markdown("### Seleccionar Tipo de Medida")

    # Si hay sugerencias, mostrarlas primero
    if suggestions:
        st.info(f"Sugerencias basadas en tu consulta:")

        # Botones para sugerencias
        cols = st.columns(min(len(suggestions), 3))
        for idx, template in enumerate(suggestions[:3]):
            with cols[idx]:
                if st.button(
                    f"{template.name}",
                    key=f"suggest_{template.id}",
                    use_container_width=True
                ):
                    return template.id

        st.markdown("---")

    # Selector manual por categoría
    category = st.selectbox(
        "O selecciona por categoría:",
        tm.get_categories(),
        key="template_category"
    )

    # Templates de la categoría
    templates = tm.list_by_category(category)

    # Crear diccionario para el selector
    template_options = {}
    for t in templates:
        difficulty_icon = {'basic': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}
        icon = difficulty_icon.get(t.difficulty, '⚪')
        date_req = ' 📅' if t.requires_date_table else ''
        label = f"{icon} {t.name}{date_req}"
        template_options[label] = t.id

    if template_options:
        selected_label = st.selectbox(
            "Tipo de medida:",
            list(template_options.keys()),
            key="template_selection"
        )

        template_id = template_options[selected_label]
        template = tm.get_template(template_id)

        # Mostrar descripción
        st.info(f"**{template.name}**\n\n{template.description}")

        # Botón continuar
        if st.button("➡️ Continuar", use_container_width=True):
            return template_id

    return None


def show_parameter_form(template_id: str) -> Optional[Dict[str, str]]:
    """
    Muestra formulario de parámetros para un template

    Args:
        template_id: ID del template

    Returns:
        Diccionario con parámetros o None
    """
    tm = st.session_state.template_manager
    template = tm.get_template(template_id)

    if not template:
        st.error(f"Template '{template_id}' no encontrado")
        return None

    st.markdown(f"### {template.name}")
    st.caption(template.description)

    # Crear validador
    model_data = st.session_state.get('model_data', None)
    validator = ParameterValidator(model_data)

    # Formulario
    with st.form(key="parameter_form"):
        params = {}

        for param in template.parameters:
            # Label con indicador de requerido
            label = param.description
            if param.required:
                label += " *"

            # Help text
            help_text = format_parameter_help(param.type)

            # Input según tipo
            if param.type in ['measure', 'column', 'date_column']:
                # Sugerir valores si tenemos datos del modelo
                suggestions = validator.suggest_values(param.type, query="")

                if suggestions:
                    # Selector + input manual
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        value = st.text_input(
                            label,
                            key=f"param_{param.name}",
                            help=help_text,
                            placeholder=f"Ej: {param.type}"
                        )
                    with col2:
                        if st.button("📋", key=f"suggest_{param.name}"):
                            st.session_state[f'show_suggestions_{param.name}'] = True

                    # Mostrar sugerencias si se solicitó
                    if st.session_state.get(f'show_suggestions_{param.name}', False):
                        selected = st.selectbox(
                            f"Seleccionar {param.name}:",
                            suggestions,
                            key=f"select_{param.name}"
                        )
                        if selected:
                            value = selected
                            st.session_state[f'show_suggestions_{param.name}'] = False
                else:
                    value = st.text_input(
                        label,
                        key=f"param_{param.name}",
                        help=help_text
                    )
            else:
                # Text input para otros tipos
                value = st.text_input(
                    label,
                    key=f"param_{param.name}",
                    help=help_text
                )

            params[param.name] = value

        # Botones
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔍 Preview", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

        if cancel:
            return "CANCEL"

        if submitted:
            # Validar parámetros
            all_valid = True
            errors = []

            for param in template.parameters:
                value = params.get(param.name, "")
                if param.required and not value:
                    errors.append(f"❌ {param.description} es requerido")
                    all_valid = False
                elif value:
                    # Validar formato
                    is_valid, error = validator.validate_parameter(
                        param.name,
                        value,
                        param.type
                    )
                    if not is_valid:
                        errors.append(f"❌ {error}")
                        all_valid = False

            if not all_valid:
                for error in errors:
                    st.error(error)
                return None

            return params

    return None


def show_dax_preview(template_id: str, params: Dict[str, str]) -> bool:
    """
    Muestra preview del código DAX y opciones de aplicar

    Args:
        template_id: ID del template
        params: Parámetros del template

    Returns:
        True si usuario confirma aplicar, False si cancela
    """
    # Imports dentro de la función para evitar imports circulares
    from ui.enriched_preview import show_enriched_preview_ui, show_quick_analysis
    from ui.favorites_ui import show_favorite_button

    tm = st.session_state.template_manager

    # Generar DAX
    success, message, dax_code = tm.generate_dax(template_id, params)

    if not success:
        st.error(f"Error al generar DAX: {message}")
        return False

    st.success(message)

    # Obtener template
    template = tm.get_template(template_id)
    measure_name = params.get('measure_name', 'New Measure')

    # Opciones de vista
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        preview_mode = st.radio(
            "Vista:",
            ["📄 Simple", "🔬 Enriquecida"],
            horizontal=True,
            key="preview_mode"
        )

    with col2:
        # Botón de favorito
        show_favorite_button(template_id, template.name)

    with col3:
        st.write("")  # Spacer

    st.markdown("---")

    # Mostrar preview según modo
    if preview_mode == "🔬 Enriquecida":
        # Preview enriquecido con análisis
        show_enriched_preview_ui(
            dax_code=dax_code,
            measure_name=measure_name,
            template_name=template.name,
            parameters=params
        )
    else:
        # Preview simple
        st.markdown("### 📄 Código DAX")
        st.code(dax_code, language="dax")

        # Análisis rápido
        show_quick_analysis(dax_code, measure_name)

        # Información adicional
        with st.expander("ℹ️ Información del Template"):
            st.markdown(f"**Categoría:** {template.category}")
            st.markdown(f"**Dificultad:** {template.difficulty}")
            if template.requires_date_table:
                st.warning("⚠️ Esta medida requiere una tabla de calendario/fechas en el modelo")

            st.markdown("**Ejemplo de uso:**")
            st.code(template.example, language="dax")

    # Opciones de copia mejoradas
    st.markdown("---")
    multi_clipboard_options(
        dax_code=dax_code,
        measure_name=measure_name,
        parameters=params,
        template_name=template.name
    )

    # Opciones de exportación
    show_export_options(
        measure_name=measure_name,
        dax_code=dax_code,
        template_name=template.name,
        template_id=template_id,
        parameters=params,
        category=template.category
    )

    # Opciones principales
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Aplicar al Modelo", use_container_width=True, type="primary"):
            return True

    with col2:
        if st.button("🔄 Modificar Parámetros", use_container_width=True):
            st.session_state['template_step'] = 'parameters'
            st.rerun()
            return False

    return False


def apply_measure_to_model(
    measure_name: str,
    dax_code: str,
    target_table: Optional[str] = None
) -> bool:
    """
    Aplica la medida generada al modelo

    Args:
        measure_name: Nombre de la medida
        dax_code: Código DAX completo
        target_table: Tabla destino (opcional)

    Returns:
        True si se aplicó correctamente
    """
    # Extraer expresión (sin el nombre)
    if "=" in dax_code:
        parts = dax_code.split("=", 1)
        measure_name = parts[0].strip()
        expression = parts[1].strip()
    else:
        expression = dax_code

    # Verificar modo
    mode = st.session_state.get('mode', None)

    if mode == 'xmla' and st.session_state.get('is_connected', False):
        # Modo XMLA: aplicar con TOM
        try:
            connector = st.session_state.connector
            tom = connector.get_tom_wrapper()

            if not tom or not tom.is_connected:
                st.error("❌ TOM no está conectado. Requiere pythonnet instalado.")
                st.info("📋 Código copiado al portapapeles. Puedes pegarlo manualmente en Power BI Desktop.")
                st.session_state['clipboard'] = dax_code
                return False

            # Pedir tabla destino si no se especificó
            if not target_table:
                model_data = st.session_state.get('model_data', None)
                if model_data and hasattr(model_data, 'tables'):
                    tables = [t.get('name', t.get('Name', '')) for t in model_data.tables]
                    target_table = st.selectbox(
                        "Selecciona tabla destino:",
                        tables,
                        key="target_table_select"
                    )
                else:
                    target_table = st.text_input(
                        "Nombre de la tabla destino:",
                        key="target_table_input"
                    )

            if not target_table:
                st.warning("⚠️ Debes especificar una tabla destino")
                return False

            # Aplicar medida
            success = tom.create_measure(
                table_name=target_table,
                measure_name=measure_name,
                expression=expression
            )

            if success:
                st.success(f"✅ Medida '{measure_name}' creada en tabla '{target_table}'!")
                st.info("💡 La medida está visible en Power BI Desktop. Usa Ctrl+Z si necesitas deshacer.")
                return True
            else:
                st.error("❌ Error al crear la medida")
                return False

        except Exception as e:
            st.error(f"❌ Error al aplicar medida: {e}")
            st.info("📋 Código copiado al portapapeles para aplicación manual.")
            st.session_state['clipboard'] = dax_code
            return False

    else:
        # Modo archivo: solo mostrar código
        st.warning("⚠️ Modo archivo - La medida no puede aplicarse directamente")
        st.info("**Opciones:**")
        st.markdown("1. 📋 Copiar código y pegar en Power BI Desktop")
        st.markdown("2. 🔌 Conectar a Power BI Desktop vía XMLA para aplicar automáticamente")

        st.code(dax_code, language="dax")

        if st.button("📋 Copiar Código", key="copy_code_file_mode"):
            st.session_state['clipboard'] = dax_code
            st.success("✅ Código copiado!")

        return False


def show_template_workflow():
    """
    Muestra el flujo completo de creación de medida con templates
    """
    # Inicializar estado del workflow
    if 'template_step' not in st.session_state:
        st.session_state.template_step = 'select'
    if 'selected_template_id' not in st.session_state:
        st.session_state.selected_template_id = None
    if 'template_params' not in st.session_state:
        st.session_state.template_params = None

    # Breadcrumb
    steps = {
        'select': '1️⃣ Seleccionar Template',
        'parameters': '2️⃣ Parámetros',
        'preview': '3️⃣ Preview & Aplicar'
    }

    current_step = st.session_state.template_step
    breadcrumb = " → ".join([
        f"**{text}**" if step == current_step else text
        for step, text in steps.items()
    ])
    st.markdown(breadcrumb)
    st.markdown("---")

    # Paso 1: Seleccionar Template
    if current_step == 'select':
        # Opción de modo avanzado
        col1, col2 = st.columns([3, 1])
        with col2:
            use_advanced = st.checkbox(
                "🔍 Búsqueda Avanzada",
                key="use_advanced_search",
                value=st.session_state.get('use_advanced_search', False)
            )

        if use_advanced:
            # Usar búsqueda avanzada
            from ui.advanced_search import show_advanced_search
            template_id = show_advanced_search()
        else:
            # Obtener sugerencias si hay contexto
            last_user_message = None
            if st.session_state.chat_history:
                for msg in reversed(st.session_state.chat_history):
                    if msg['role'] == 'user':
                        last_user_message = msg['content']
                        break

            suggestions = None
            if last_user_message:
                tm = st.session_state.template_manager
                suggestions = tm.suggest_templates(last_user_message, limit=3)

            template_id = show_template_selector(suggestions)

        if template_id:
            st.session_state.selected_template_id = template_id
            st.session_state.template_step = 'parameters'
            st.rerun()

    # Paso 2: Parámetros
    elif current_step == 'parameters':
        template_id = st.session_state.selected_template_id

        if not template_id:
            st.session_state.template_step = 'select'
            st.rerun()
            return

        # Botón volver
        if st.button("⬅️ Volver a selección", key="back_to_select"):
            st.session_state.template_step = 'select'
            st.rerun()
            return

        # Opción de validación mejorada
        col1, col2 = st.columns([3, 1])
        with col2:
            use_enhanced = st.checkbox(
                "✨ Validación Mejorada",
                key="use_enhanced_validation",
                value=st.session_state.get('use_enhanced_validation', True),
                help="Validación en tiempo real con sugerencias inteligentes"
            )

        if use_enhanced:
            from ui.enhanced_validation import show_parameter_form_enhanced
            params = show_parameter_form_enhanced(template_id)
        else:
            params = show_parameter_form(template_id)

        if params == "CANCEL":
            st.session_state.template_step = 'select'
            st.session_state.selected_template_id = None
            st.rerun()
        elif params == "BACK":
            st.session_state.template_step = 'select'
            st.rerun()
        elif params:
            st.session_state.template_params = params
            st.session_state.template_step = 'preview'
            st.rerun()

    # Paso 3: Preview y Aplicar
    elif current_step == 'preview':
        template_id = st.session_state.selected_template_id
        params = st.session_state.template_params

        if not template_id or not params:
            st.session_state.template_step = 'select'
            st.rerun()
            return

        should_apply = show_dax_preview(template_id, params)

        if should_apply:
            measure_name = params.get('measure_name', 'New Measure')
            tm = st.session_state.template_manager
            success, message, dax_code = tm.generate_dax(template_id, params)

            if success:
                applied = apply_measure_to_model(measure_name, dax_code)

                # Guardar en historial (aplicada o solo copiada)
                from ui.history_ui import add_to_history
                template = tm.get_template(template_id)

                add_to_history(
                    measure_name=measure_name,
                    template_id=template_id,
                    template_name=template.name,
                    dax_code=dax_code,
                    parameters=params,
                    category=template.category,
                    applied=applied
                )

                if applied:
                    # Reset workflow
                    st.session_state.template_step = 'select'
                    st.session_state.selected_template_id = None
                    st.session_state.template_params = None

                    # Agregar a historial de chat
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': f"✅ Medida '{measure_name}' creada y guardada en historial",
                        'timestamp': None
                    })

                    st.balloons()
                    st.rerun()
