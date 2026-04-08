"""
Helper de Exportación
Sistema para exportar medidas, templates y configuraciones
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st


class ExportHelper:
    """Helper para exportar contenido a diferentes formatos"""

    @staticmethod
    def export_measure_to_dax(
        measure_name: str,
        dax_code: str,
        template_name: str,
        parameters: Dict[str, str],
        notes: str = "",
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta una medida a formato .dax

        Args:
            measure_name: Nombre de la medida
            dax_code: Código DAX
            template_name: Nombre del template usado
            parameters: Parámetros usados
            notes: Notas adicionales
            output_path: Ruta de salida (opcional)

        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            # Nombre seguro para archivo
            safe_name = "".join(c for c in measure_name if c.isalnum() or c in (' ', '-', '_'))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/medida_{safe_name}_{timestamp}.dax"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""// ============================================
// MEDIDA DAX - {measure_name}
// ============================================
// Generado por: Power BI Bot - YPF RTIC
// Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Template: {template_name}
// ============================================

// PARÁMETROS USADOS:
"""
        for key, value in parameters.items():
            content += f"// - {key}: {value}\n"

        if notes:
            content += f"\n// NOTAS:\n// {notes}\n"

        content += f"""
// ============================================
// CÓDIGO DAX:
// ============================================

{dax_code}

// ============================================
// FIN DE MEDIDA
// ============================================
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)

    @staticmethod
    def export_template_config(
        template_id: str,
        template_data: dict,
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta configuración de un template a JSON

        Args:
            template_id: ID del template
            template_data: Datos del template
            output_path: Ruta de salida

        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/template_{template_id}_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "template_id": template_id,
            "exported_at": datetime.now().isoformat(),
            "template_data": template_data
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return str(output_file)

    @staticmethod
    def export_multiple_measures(
        measures: List[Dict],
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta múltiples medidas a un archivo

        Args:
            measures: Lista de medidas con sus datos
            output_path: Ruta de salida

        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/medidas_exportadas_{timestamp}.dax"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""// ============================================
// COLECCIÓN DE MEDIDAS DAX
// ============================================
// Power BI Bot - YPF RTIC
// Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Total de medidas: {len(measures)}
// ============================================

"""

        for i, measure in enumerate(measures, 1):
            content += f"""
// ============================================
// MEDIDA #{i}: {measure['measure_name']}
// ============================================
// Template: {measure['template_name']}
// Parámetros:
"""
            for key, value in measure['parameters'].items():
                content += f"//   - {key}: {value}\n"

            content += f"""
{measure['dax_code']}

"""

        content += """// ============================================
// FIN DE COLECCIÓN
// ============================================
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)

    @staticmethod
    def export_to_powerbi_template(
        measures: List[Dict],
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta medidas en formato template de Power BI (JSON)

        Args:
            measures: Lista de medidas
            output_path: Ruta de salida

        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/powerbi_template_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Formato compatible con Power BI
        template = {
            "name": "Power BI Bot - Medidas Exportadas",
            "description": f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "version": "1.0",
            "measures": []
        }

        for measure in measures:
            template["measures"].append({
                "name": measure['measure_name'],
                "expression": measure['dax_code'],
                "displayFolder": measure.get('category', 'General'),
                "formatString": "",
                "description": f"Template: {measure['template_name']}"
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        return str(output_file)

    @staticmethod
    def create_download_link(file_path: str, link_text: str = "⬇️ Descargar Archivo"):
        """
        Crea un botón de descarga para un archivo

        Args:
            file_path: Ruta del archivo
            link_text: Texto del link
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_name = Path(file_path).name

            st.download_button(
                label=link_text,
                data=content,
                file_name=file_name,
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error al crear link de descarga: {e}")


def show_export_options(
    measure_name: str,
    dax_code: str,
    template_name: str,
    template_id: str,
    parameters: Dict[str, str],
    category: str
):
    """
    Muestra opciones de exportación en UI

    Args:
        measure_name: Nombre de la medida
        dax_code: Código DAX
        template_name: Nombre del template
        template_id: ID del template
        parameters: Parámetros usados
        category: Categoría
    """
    with st.expander("💾 Opciones de Exportación"):
        st.markdown("Guarda la medida generada en diferentes formatos")

        col1, col2 = st.columns(2)

        with col1:
            # Exportar medida individual
            if st.button("📄 Exportar como .dax", use_container_width=True):
                helper = ExportHelper()
                file_path = helper.export_measure_to_dax(
                    measure_name=measure_name,
                    dax_code=dax_code,
                    template_name=template_name,
                    parameters=parameters
                )

                st.success(f"Exportado a: {file_path}")

                # Botón de descarga
                helper.create_download_link(file_path, "⬇️ Descargar .dax")

        with col2:
            # Exportar configuración
            if st.button("⚙️ Exportar Template Config", use_container_width=True):
                helper = ExportHelper()

                template_data = {
                    "template_id": template_id,
                    "template_name": template_name,
                    "category": category,
                    "parameters": parameters,
                    "example_output": dax_code
                }

                file_path = helper.export_template_config(
                    template_id=template_id,
                    template_data=template_data
                )

                st.success(f"Exportado a: {file_path}")

                # Botón de descarga
                helper.create_download_link(file_path, "⬇️ Descargar .json")


def show_batch_export():
    """
    Muestra opciones de exportación en lote
    """
    st.markdown("### 📦 Exportación en Lote")

    if 'measure_history' not in st.session_state:
        st.warning("No hay medidas en el historial para exportar")
        return

    history = st.session_state.measure_history
    entries = history.get_all()

    if not entries:
        st.info("No hay medidas en el historial")
        return

    st.markdown(f"**Total de medidas:** {len(entries)}")

    # Opciones de filtro
    col1, col2 = st.columns(2)

    with col1:
        export_applied = st.checkbox("Incluir solo aplicadas", value=False)

    with col2:
        export_category = st.selectbox(
            "Filtrar por categoría",
            ["Todas"] + list(set(e.category for e in entries))
        )

    # Filtrar
    filtered_entries = entries

    if export_applied:
        filtered_entries = [e for e in filtered_entries if e.applied]

    if export_category != "Todas":
        filtered_entries = [e for e in filtered_entries if e.category == export_category]

    st.markdown(f"**A exportar:** {len(filtered_entries)} medidas")

    # Botones de exportación
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Exportar como .dax", use_container_width=True):
            measures = [
                {
                    'measure_name': e.measure_name,
                    'dax_code': e.dax_code,
                    'template_name': e.template_name,
                    'parameters': e.parameters,
                    'category': e.category
                }
                for e in filtered_entries
            ]

            helper = ExportHelper()
            file_path = helper.export_multiple_measures(measures)

            st.success(f"Exportadas {len(measures)} medidas a: {file_path}")
            helper.create_download_link(file_path)

    with col2:
        if st.button("📋 Exportar para Power BI", use_container_width=True):
            measures = [
                {
                    'measure_name': e.measure_name,
                    'dax_code': e.dax_code,
                    'template_name': e.template_name,
                    'parameters': e.parameters,
                    'category': e.category
                }
                for e in filtered_entries
            ]

            helper = ExportHelper()
            file_path = helper.export_to_powerbi_template(measures)

            st.success(f"Template Power BI generado: {file_path}")
            helper.create_download_link(file_path)
