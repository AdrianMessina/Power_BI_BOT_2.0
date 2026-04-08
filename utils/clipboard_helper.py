"""
Helper de Clipboard Mejorado
Sistema para copiar código al portapapeles con notificaciones visuales
"""

import streamlit as st
from typing import Optional
import streamlit.components.v1 as components


def copy_to_clipboard_js(text: str, button_id: str) -> str:
    """
    Genera código JavaScript para copiar al portapapeles

    Args:
        text: Texto a copiar
        button_id: ID único del botón

    Returns:
        HTML con JavaScript embebido
    """
    # Escapar comillas y saltos de línea
    escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')

    html = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        const text = '{escaped_text}';

        // Intentar usar API moderna
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text).then(function() {{
                console.log('Copied to clipboard successfully!');
            }}).catch(function(err) {{
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(text);
            }});
        }} else {{
            // Fallback para navegadores antiguos
            fallbackCopyTextToClipboard(text);
        }}
    }}

    function fallbackCopyTextToClipboard(text) {{
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.top = 0;
        textArea.style.left = 0;
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = 0;
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';

        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {{
            const successful = document.execCommand('copy');
            console.log('Fallback: Copying text command was ' + (successful ? 'successful' : 'unsuccessful'));
        }} catch (err) {{
            console.error('Fallback: Oops, unable to copy', err);
        }}

        document.body.removeChild(textArea);
    }}
    </script>
    """

    return html


def clipboard_button(
    text: str,
    label: str = "📋 Copiar",
    button_id: Optional[str] = None,
    success_message: str = "✅ Código copiado al portapapeles!",
    use_container_width: bool = False
) -> bool:
    """
    Crea un botón para copiar texto al portapapeles con feedback visual

    Args:
        text: Texto a copiar
        label: Label del botón
        button_id: ID único del botón (se genera automático si no se proporciona)
        success_message: Mensaje de éxito
        use_container_width: Si usar ancho completo

    Returns:
        True si se hizo clic en el botón
    """
    if button_id is None:
        button_id = f"clipboard_{hash(text) % 10000}"

    # Crear estado para el feedback
    if f'clipboard_clicked_{button_id}' not in st.session_state:
        st.session_state[f'clipboard_clicked_{button_id}'] = False

    # Botón de Streamlit
    clicked = st.button(
        label,
        key=f"btn_{button_id}",
        use_container_width=use_container_width
    )

    if clicked:
        # Guardar en session_state
        st.session_state[f'clipboard_text_{button_id}'] = text
        st.session_state[f'clipboard_clicked_{button_id}'] = True

        # Mostrar mensaje de éxito
        st.success(success_message)

        # Renderizar JavaScript para copiar
        js_code = copy_to_clipboard_js(text, button_id)
        components.html(
            js_code + f"<script>copyToClipboard_{button_id}();</script>",
            height=0
        )

        return True

    # Reset del estado después de un frame
    if st.session_state.get(f'clipboard_clicked_{button_id}', False):
        st.session_state[f'clipboard_clicked_{button_id}'] = False

    return False


def clipboard_code_block(
    code: str,
    language: str = "dax",
    show_copy_button: bool = True,
    button_label: str = "📋 Copiar Código",
    button_id: Optional[str] = None
):
    """
    Muestra un bloque de código con botón de copiar integrado

    Args:
        code: Código a mostrar
        language: Lenguaje para syntax highlighting
        show_copy_button: Si mostrar botón de copiar
        button_label: Label del botón
        button_id: ID único del botón
    """
    # Mostrar código
    st.code(code, language=language)

    # Botón de copiar
    if show_copy_button:
        clipboard_button(
            text=code,
            label=button_label,
            button_id=button_id or f"code_{hash(code) % 10000}",
            use_container_width=True
        )


def clipboard_text_area(
    text: str,
    label: str = "Código DAX",
    height: int = 200,
    show_copy_button: bool = True
):
    """
    Muestra un text area con botón de copiar

    Args:
        text: Texto a mostrar
        label: Label del text area
        height: Altura del text area
        show_copy_button: Si mostrar botón de copiar
    """
    st.text_area(
        label,
        value=text,
        height=height,
        disabled=True,
        key=f"textarea_{hash(text) % 10000}"
    )

    if show_copy_button:
        clipboard_button(
            text=text,
            label="📋 Copiar Todo",
            button_id=f"textarea_copy_{hash(text) % 10000}",
            use_container_width=True
        )


def multi_clipboard_options(
    dax_code: str,
    measure_name: str,
    parameters: dict,
    template_name: str
):
    """
    Muestra múltiples opciones de copia (código, parámetros, todo)

    Args:
        dax_code: Código DAX
        measure_name: Nombre de la medida
        parameters: Parámetros usados
        template_name: Nombre del template
    """
    st.markdown("### 📋 Opciones de Copia")

    col1, col2, col3 = st.columns(3)

    with col1:
        if clipboard_button(
            text=dax_code,
            label="📄 Copiar Código DAX",
            button_id="copy_dax_only",
            use_container_width=True
        ):
            pass

    with col2:
        # Copiar parámetros como texto
        params_text = f"// Template: {template_name}\n"
        params_text += f"// Medida: {measure_name}\n\n"
        params_text += "// Parámetros:\n"
        for key, value in parameters.items():
            params_text += f"// {key}: {value}\n"

        if clipboard_button(
            text=params_text,
            label="⚙️ Copiar Parámetros",
            button_id="copy_params",
            use_container_width=True
        ):
            pass

    with col3:
        # Copiar todo (código + parámetros)
        full_text = f"""// ============================================
// Medida: {measure_name}
// Template: {template_name}
// ============================================

// Parámetros usados:
"""
        for key, value in parameters.items():
            full_text += f"// {key}: {value}\n"

        full_text += f"\n// Código DAX:\n{dax_code}"

        if clipboard_button(
            text=full_text,
            label="📦 Copiar Todo",
            button_id="copy_all",
            use_container_width=True
        ):
            pass


def show_clipboard_history():
    """
    Muestra historial de elementos copiados en la sesión actual
    """
    if 'clipboard_history' not in st.session_state:
        st.session_state.clipboard_history = []

    with st.expander("📋 Historial de Copiado (Esta Sesión)"):
        if not st.session_state.clipboard_history:
            st.caption("No hay elementos copiados en esta sesión")
            return

        for i, item in enumerate(reversed(st.session_state.clipboard_history[-5:])):
            st.text(f"{i+1}. {item['label']} - {item['timestamp']}")

            if st.button(f"🔄 Recopiar", key=f"recopy_{i}"):
                clipboard_button(
                    text=item['text'],
                    label="📋 Copiar Nuevamente",
                    button_id=f"recopy_btn_{i}"
                )


def add_to_clipboard_history(text: str, label: str):
    """
    Agrega un elemento al historial de clipboard

    Args:
        text: Texto copiado
        label: Descripción del elemento
    """
    from datetime import datetime

    if 'clipboard_history' not in st.session_state:
        st.session_state.clipboard_history = []

    st.session_state.clipboard_history.append({
        'text': text,
        'label': label,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })

    # Mantener solo los últimos 20
    if len(st.session_state.clipboard_history) > 20:
        st.session_state.clipboard_history = st.session_state.clipboard_history[-20:]
