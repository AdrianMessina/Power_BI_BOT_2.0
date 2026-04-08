"""
Sistema de Validación Mejorado con Feedback Visual
Validación en tiempo real con indicadores visuales y sugerencias
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional
from templates.parameter_validator import ParameterValidator
from templates.base_template import TemplateParameter


class EnhancedParameterValidator:
    """
    Validador mejorado con feedback visual en tiempo real
    """

    def __init__(self, model_data=None):
        self.validator = ParameterValidator(model_data)
        self.model_data = model_data

    def show_parameter_input_with_validation(
        self,
        param: TemplateParameter,
        key_prefix: str = ""
    ) -> Tuple[str, bool]:
        """
        Muestra input de parámetro con validación en tiempo real

        Args:
            param: TemplateParameter a mostrar
            key_prefix: Prefijo para las keys de Streamlit

        Returns:
            (valor_ingresado, es_valido)
        """
        param_key = f"{key_prefix}{param.name}"

        # Label con indicador de requerido
        label = param.description
        if param.required:
            label = f"{label} ⚠️"

        # Crear columnas para input + validación visual
        col_input, col_validation = st.columns([4, 1])

        with col_input:
            # Input según tipo con sugerencias
            if param.type in ['measure', 'column', 'date_column']:
                value = self._show_smart_input(param, param_key, label)
            else:
                value = st.text_input(
                    label,
                    key=param_key,
                    placeholder=self._get_placeholder(param.type)
                )

        # Validación en tiempo real
        is_valid = True
        validation_message = ""

        if value:
            is_valid, error = self.validator.validate_parameter(
                param.name,
                value,
                param.type
            )

            with col_validation:
                if is_valid:
                    st.markdown("### ✅")
                else:
                    st.markdown("### ❌")

            # Mostrar mensaje de error si hay
            if not is_valid:
                st.error(f"⚠️ {error}")
                validation_message = error
        elif param.required:
            with col_validation:
                st.markdown("### ⚪")
            st.caption("⚠️ Campo requerido")
            is_valid = False

        # Ayuda contextual
        if not value or not is_valid:
            with st.expander("💡 Ayuda", expanded=False):
                self._show_parameter_help(param)

        return value, is_valid

    def _show_smart_input(
        self,
        param: TemplateParameter,
        key: str,
        label: str
    ) -> str:
        """
        Input inteligente con autocompletado y sugerencias
        """
        # Obtener sugerencias
        suggestions = self.validator.suggest_values(param.type, query="")

        if suggestions:
            # Modo: selector o texto libre
            input_mode = st.radio(
                "Modo de entrada:",
                ["📝 Escribir", "📋 Seleccionar"],
                horizontal=True,
                key=f"{key}_mode",
                label_visibility="collapsed"
            )

            if input_mode == "📋 Seleccionar":
                # Selector con sugerencias
                value = st.selectbox(
                    label,
                    [""] + suggestions,
                    key=f"{key}_select",
                    format_func=lambda x: "-- Seleccione --" if x == "" else x
                )
                return value
            else:
                # Input con sugerencias como ayuda
                value = st.text_input(
                    label,
                    key=f"{key}_text",
                    placeholder=self._get_placeholder(param.type)
                )

                # Mostrar sugerencias si el input está activo
                if st.session_state.get(f"{key}_show_suggestions", False):
                    st.caption("💡 Sugerencias disponibles:")
                    # Filtrar sugerencias basadas en lo que el usuario escribió
                    filtered = [s for s in suggestions if not value or value.lower() in s.lower()]
                    for suggestion in filtered[:5]:
                        if st.button(
                            suggestion,
                            key=f"{key}_suggest_{suggestion}",
                            use_container_width=True
                        ):
                            st.session_state[f"{key}_text"] = suggestion
                            st.rerun()

                # Botón para mostrar/ocultar sugerencias
                if st.button(
                    "💡 Ver sugerencias" if not st.session_state.get(f"{key}_show_suggestions", False) else "❌ Ocultar",
                    key=f"{key}_toggle_suggestions"
                ):
                    st.session_state[f"{key}_show_suggestions"] = not st.session_state.get(f"{key}_show_suggestions", False)
                    st.rerun()

                return value
        else:
            # Input simple si no hay sugerencias
            return st.text_input(
                label,
                key=f"{key}_text",
                placeholder=self._get_placeholder(param.type)
            )

    def _get_placeholder(self, param_type: str) -> str:
        """
        Retorna placeholder apropiado según tipo de parámetro
        """
        placeholders = {
            'measure': 'Ej: [Total Ventas]',
            'table': 'Ej: Ventas',
            'column': 'Ej: Ventas[Fecha]',
            'date_column': 'Ej: Calendario[Fecha]',
            'text': 'Ingrese un valor'
        }
        return placeholders.get(param_type, 'Ingrese un valor')

    def _show_parameter_help(self, param: TemplateParameter):
        """
        Muestra ayuda contextual para un parámetro
        """
        st.markdown(f"**{param.name}** ({param.type})")
        st.markdown(param.description)

        # Formato esperado
        format_examples = {
            'measure': """
**Formato:**
- Usar corchetes: `[NombreMedida]`
- Ejemplo: `[Total Ventas]`, `[Cantidad]`

**Común:**
- `[Total Sales]`
- `[Cantidad Vendida]`
- `[Margen]`
            """,
            'table': """
**Formato:**
- Nombre sin corchetes
- Ejemplo: `Ventas`, `Productos`

**Común:**
- `Ventas`
- `Productos`
- `Clientes`
            """,
            'column': """
**Formato:**
- Tabla[Columna]
- Ejemplo: `Ventas[Fecha]`, `Productos[Categoria]`

**Común:**
- `Ventas[Fecha]`
- `Ventas[Monto]`
- `Productos[Nombre]`
            """,
            'date_column': """
**Formato:**
- Tabla[Columna] donde Columna es tipo fecha
- Ejemplo: `Calendario[Fecha]`, `Ventas[FechaVenta]`

**Importante:**
- Debe ser una columna de tipo fecha (Date/DateTime)
- Preferiblemente de una tabla de calendario

**Común:**
- `Calendario[Fecha]`
- `Dim_Fecha[Fecha]`
- `Ventas[FechaVenta]`
            """
        }

        help_text = format_examples.get(param.type, "Formato no especificado")
        st.markdown(help_text)

    def validate_all_parameters(
        self,
        parameters: Dict[str, str],
        template_params: List[TemplateParameter]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Valida todos los parámetros y retorna resumen completo

        Args:
            parameters: Dict con valores de parámetros
            template_params: Lista de TemplateParameter del template

        Returns:
            (all_valid, errors, warnings)
        """
        errors = []
        warnings = []

        for param in template_params:
            value = parameters.get(param.name, "")

            # Verificar requeridos
            if param.required and not value:
                errors.append(f"❌ {param.description} es requerido")
                continue

            # Validar formato si tiene valor
            if value:
                is_valid, error = self.validator.validate_parameter(
                    param.name,
                    value,
                    param.type
                )

                if not is_valid:
                    errors.append(f"❌ {error}")

        all_valid = len(errors) == 0
        return all_valid, errors, warnings

    def show_validation_summary(
        self,
        parameters: Dict[str, str],
        template_params: List[TemplateParameter]
    ):
        """
        Muestra resumen visual de validación
        """
        all_valid, errors, warnings = self.validate_all_parameters(
            parameters,
            template_params
        )

        st.markdown("### 📋 Resumen de Validación")

        if all_valid:
            st.success("✅ Todos los parámetros son válidos")
        else:
            st.error(f"❌ {len(errors)} error(es) encontrado(s)")

            for error in errors:
                st.error(error)

        if warnings:
            st.warning(f"⚠️ {len(warnings)} advertencia(s)")
            for warning in warnings:
                st.warning(warning)

        # Estadísticas
        total_params = len(template_params)
        required_params = len([p for p in template_params if p.required])
        filled_params = len([v for v in parameters.values() if v])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Parámetros", total_params)
        with col2:
            st.metric("Requeridos", required_params)
        with col3:
            st.metric("Completados", filled_params)

        return all_valid


def show_parameter_form_enhanced(
    template_id: str,
    key_prefix: str = "enhanced_"
) -> Optional[Dict[str, str]]:
    """
    Muestra formulario de parámetros con validación mejorada

    Args:
        template_id: ID del template
        key_prefix: Prefijo para las keys

    Returns:
        Dict con parámetros si se completó, None si no
    """
    if 'template_manager' not in st.session_state:
        st.error("Template Manager no inicializado")
        return None

    tm = st.session_state.template_manager
    template = tm.get_template(template_id)

    if not template:
        st.error(f"Template '{template_id}' no encontrado")
        return None

    # Header
    st.markdown(f"### ⚙️ {template.name}")
    st.caption(template.description)

    # Crear validador
    model_data = st.session_state.get('model_data', None)
    validator = EnhancedParameterValidator(model_data)

    # Contenedor para parámetros
    parameters = {}
    all_valid = True

    st.markdown("---")
    st.markdown("**Parámetros:**")

    # Mostrar cada parámetro con validación
    for param in template.parameters:
        value, is_valid = validator.show_parameter_input_with_validation(
            param,
            key_prefix=key_prefix
        )
        parameters[param.name] = value

        if param.required and not is_valid:
            all_valid = False

    # Resumen de validación
    st.markdown("---")
    validator.show_validation_summary(parameters, template.parameters)

    # Botones de acción
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Volver", key=f"{key_prefix}back", use_container_width=True):
            return "BACK"

    with col2:
        preview_enabled = all_valid
        if st.button(
            "👁️ Preview",
            key=f"{key_prefix}preview",
            use_container_width=True,
            disabled=not preview_enabled,
            type="primary" if preview_enabled else "secondary"
        ):
            if all_valid:
                return parameters

    with col3:
        if st.button("❌ Cancelar", key=f"{key_prefix}cancel", use_container_width=True):
            return "CANCEL"

    if not all_valid:
        st.info("💡 Completa todos los campos requeridos para continuar")

    return None
