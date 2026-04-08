"""
Tutorial Interactivo
Guía paso a paso para nuevos usuarios del Power BI Bot
"""

import streamlit as st
from typing import Dict, List


class Tutorial:
    """Gestor del tutorial interactivo"""

    def __init__(self):
        self.steps = [
            {
                "title": "Bienvenido a Power BI Bot",
                "content": """
### 👋 ¡Bienvenido!

Power BI Bot te ayuda a consultar y crear medidas DAX para tus modelos de Power BI.

**¿Qué puedo hacer?**
- 📊 Consultar medidas, tablas y relaciones
- ✨ Crear medidas DAX automáticamente
- 📜 Ver historial de medidas creadas
- 💾 Exportar código generado

**Este tutorial te guiará en 5 pasos rápidos.**
                """,
                "icon": "👋"
            },
            {
                "title": "Paso 1: Cargar un Modelo",
                "content": """
### 📁 Cargar Modelo

Primero necesitas cargar un modelo de Power BI:

**Opción A: Desde Archivo**
1. Usa el panel izquierdo
2. Haz clic en "Selecciona archivo .pbix"
3. Elige tu archivo .pbix
4. Espera a que se cargue

**Opción B: Conectar a Power BI Desktop**
1. Abre tu .pbix en Power BI Desktop
2. Haz clic en "Detectar Power BI Desktop"
3. La conexión es automática

💡 **Tip:** El modo XMLA (Opción B) permite aplicar medidas directamente al modelo.
                """,
                "icon": "📁"
            },
            {
                "title": "Paso 2: Consultar el Modelo",
                "content": """
### 🔍 Hacer Consultas

Una vez cargado el modelo, puedes hacer preguntas en lenguaje natural:

**Ejemplos de consultas:**
- "¿Qué medidas tengo?"
- "Muéstrame las tablas del modelo"
- "¿Cuántas relaciones hay?"
- "Dame un resumen del modelo"

**Ejemplos de búsquedas:**
- "¿Qué medidas hay en la tabla Ventas?"
- "Muéstrame las columnas de Clientes"

💡 **Tip:** No necesitas sintaxis exacta, el bot entiende lenguaje natural.
                """,
                "icon": "🔍"
            },
            {
                "title": "Paso 3: Crear Medidas DAX",
                "content": """
### ✨ Crear Medidas Automáticamente

Para crear una medida DAX:

**1. Escribe tu petición:**
- "Crea una medida de ventas YTD"
- "Necesito una medida de margen %"
- "Quiero un Top 10 de productos"

**2. Selecciona el template:**
- El bot te sugerirá templates relevantes
- O puedes buscar manualmente por categoría

**3. Completa los parámetros:**
- Llena el formulario con los datos necesarios
- El bot te da sugerencias de valores válidos

**4. Preview y aplicar:**
- Revisa el código DAX generado
- Aplica al modelo o copia el código

💡 **Tip:** Tienes 46 templates disponibles en 4 categorías.
                """,
                "icon": "✨"
            },
            {
                "title": "Paso 4: Ver Historial",
                "content": """
### 📜 Historial de Medidas

Todas las medidas que crees se guardan automáticamente:

**Acceder al historial:**
- Panel lateral → "Ver Todo el Historial"
- O haz clic en cualquier medida reciente

**Qué puedes hacer:**
- 🔄 Reutilizar medidas anteriores
- 📋 Copiar código nuevamente
- 💾 Exportar a archivos .dax
- 🗑️ Eliminar entradas

**Filtros disponibles:**
- Buscar por nombre
- Filtrar por categoría
- Ver solo aplicadas/copiadas

💡 **Tip:** Usa "Reutilizar" para crear variaciones de medidas existentes.
                """,
                "icon": "📜"
            },
            {
                "title": "Paso 5: Exportar y Compartir",
                "content": """
### 💾 Exportar Medidas

Puedes exportar tus medidas en varios formatos:

**Exportar medida individual:**
1. En el preview de código → "Opciones de Exportación"
2. Elige formato (.dax o template config)
3. Descarga el archivo

**Exportar en lote:**
1. Ve al historial completo
2. "Exportar Todo" → genera archivo con todas las medidas
3. O filtra y exporta solo algunas

**Formatos disponibles:**
- 📄 .dax - Código DAX con comentarios
- ⚙️ .json - Configuración del template
- 📋 Power BI Template - JSON compatible

💡 **Tip:** Los archivos .dax incluyen todos los parámetros usados.
                """,
                "icon": "💾"
            },
            {
                "title": "¡Listo para Comenzar!",
                "content": """
### 🎉 Tutorial Completado

Ya conoces todas las funciones principales de Power BI Bot.

**Resumen rápido:**
1. ✅ Cargar modelo (.pbix o XMLA)
2. ✅ Hacer consultas en lenguaje natural
3. ✅ Crear medidas con 46 templates
4. ✅ Ver y reutilizar historial
5. ✅ Exportar en múltiples formatos

**Recursos adicionales:**
- 📖 Ver catálogo completo de templates
- 💬 Escribe "ayuda" en el chat
- 📚 Revisa la documentación

**¿Necesitas ayuda?**
Escribe "ayuda" en cualquier momento para ver la guía completa.

¡Ahora cierra este tutorial y comienza a crear medidas! 🚀
                """,
                "icon": "🎉"
            }
        ]

    def get_step(self, step_number: int) -> Dict:
        """Obtiene un paso del tutorial"""
        if 0 <= step_number < len(self.steps):
            return self.steps[step_number]
        return None

    def get_total_steps(self) -> int:
        """Retorna el número total de pasos"""
        return len(self.steps)


def show_tutorial():
    """
    Muestra el tutorial interactivo
    """
    # Inicializar estado
    if 'tutorial_step' not in st.session_state:
        st.session_state.tutorial_step = 0
    if 'tutorial_completed' not in st.session_state:
        st.session_state.tutorial_completed = False

    tutorial = Tutorial()
    current_step = st.session_state.tutorial_step
    total_steps = tutorial.get_total_steps()

    # Header
    st.markdown("## 📚 Tutorial Interactivo")

    # Progress bar
    progress = (current_step + 1) / total_steps
    st.progress(progress)
    st.caption(f"Paso {current_step + 1} de {total_steps}")

    st.markdown("---")

    # Contenido del paso actual
    step = tutorial.get_step(current_step)

    if step:
        st.markdown(f"# {step['icon']} {step['title']}")
        st.markdown(step['content'])

    st.markdown("---")

    # Navegación
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_step > 0:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state.tutorial_step -= 1
                st.rerun()

    with col2:
        if st.button("❌ Cerrar Tutorial", use_container_width=True):
            st.session_state.show_tutorial = False
            st.session_state.tutorial_completed = True
            st.rerun()

    with col3:
        if current_step < total_steps - 1:
            if st.button("Siguiente ➡️", use_container_width=True):
                st.session_state.tutorial_step += 1
                st.rerun()
        else:
            if st.button("✅ Finalizar", use_container_width=True):
                st.session_state.show_tutorial = False
                st.session_state.tutorial_completed = True
                st.balloons()
                st.rerun()


def show_tutorial_button():
    """
    Muestra botón para abrir el tutorial
    """
    # Solo mostrar si no se ha completado nunca
    if not st.session_state.get('tutorial_completed', False):
        with st.sidebar:
            st.markdown("---")
            if st.button("📚 Ver Tutorial", use_container_width=True):
                st.session_state.show_tutorial = True
                st.session_state.tutorial_step = 0
                st.rerun()


def show_quick_tips():
    """
    Muestra tips rápidos contextuales
    """
    tips = {
        'select': """
💡 **Tip:** Los templates marcados con 📅 requieren una tabla de fechas en tu modelo.
        """,
        'parameters': """
💡 **Tip:** Si ves el botón 📋, puedes ver sugerencias de valores del modelo.
        """,
        'preview': """
💡 **Tip:** Puedes copiar el código DAX y pegarlo manualmente si no tienes XMLA habilitado.
        """
    }

    step = st.session_state.get('template_step', 'select')

    if step in tips:
        st.info(tips[step])


def show_first_time_welcome():
    """
    Muestra mensaje de bienvenida para usuarios nuevos
    """
    # Verificar si es primera vez
    if 'first_time_user' not in st.session_state:
        st.session_state.first_time_user = True

    if st.session_state.first_time_user:
        st.info("""
        👋 **¡Parece que es tu primera vez usando Power BI Bot!**

        Te recomendamos ver el tutorial interactivo para conocer todas las funciones.
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📚 Ver Tutorial", use_container_width=True):
                st.session_state.show_tutorial = True
                st.session_state.tutorial_step = 0
                st.session_state.first_time_user = False
                st.rerun()

        with col2:
            if st.button("⏭️ Saltar Tutorial", use_container_width=True):
                st.session_state.first_time_user = False
                st.rerun()


def show_contextual_help(context: str):
    """
    Muestra ayuda contextual según la situación

    Args:
        context: Contexto actual ('no_model', 'creating_measure', etc.)
    """
    help_messages = {
        'no_model': """
        ℹ️ **Necesitas cargar un modelo primero**

        1. Sube un archivo .pbix desde el panel izquierdo
        2. O conecta a Power BI Desktop si tienes un modelo abierto
        """,
        'creating_measure': """
        ℹ️ **Creando una medida DAX**

        - Completa todos los campos marcados con *
        - Usa el botón 📋 para ver sugerencias de valores
        - Haz clic en "Preview" para ver el código generado
        """,
        'history_empty': """
        ℹ️ **El historial está vacío**

        Las medidas que crees se guardarán aquí automáticamente.
        Escribe "crea una medida..." en el chat para comenzar.
        """,
        'export': """
        ℹ️ **Exportando medidas**

        - .dax: Archivo con código y comentarios
        - .json: Configuración del template
        - Power BI Template: Compatible para importar
        """
    }

    if context in help_messages:
        with st.expander("ℹ️ Ayuda", expanded=False):
            st.markdown(help_messages[context])
