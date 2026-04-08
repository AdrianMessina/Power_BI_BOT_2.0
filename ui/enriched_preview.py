"""
Preview Enriquecido de Medidas DAX
Muestra código con análisis, insights y recomendaciones
"""

import streamlit as st
from typing import Optional, Dict
from core.dax_analyzer import DAXAnalyzer, DAXAnalysis


class EnrichedPreview:
    """
    Preview mejorado con análisis de código DAX
    """

    def __init__(self):
        self.analyzer = DAXAnalyzer()

    def show_enriched_preview(
        self,
        dax_code: str,
        measure_name: str,
        template_name: str,
        parameters: Optional[Dict] = None
    ):
        """
        Muestra preview enriquecido con análisis completo

        Args:
            dax_code: Código DAX generado
            measure_name: Nombre de la medida
            template_name: Nombre del template usado
            parameters: Parámetros usados
        """
        # Analizar código
        analysis = self.analyzer.analyze(dax_code)

        # Header con badges
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"### 📄 {measure_name}")
            st.caption(f"Template: {template_name}")

        with col2:
            # Badge de complejidad
            complexity_colors = {
                'Low': '🟢',
                'Medium': '🟡',
                'High': '🟠',
                'Very High': '🔴'
            }
            icon = complexity_colors.get(analysis.complexity_level, '⚪')
            st.metric(
                "Complejidad",
                f"{icon} {analysis.complexity_level}",
                f"{analysis.complexity_score}/100"
            )

        with col3:
            # Badge de performance
            perf_icons = {
                'Good': '✅',
                'Fair': '⚠️',
                'Poor': '❌'
            }
            icon = perf_icons.get(analysis.estimated_performance, '⚪')
            st.metric(
                "Performance",
                f"{icon} {analysis.estimated_performance}"
            )

        st.markdown("---")

        # Código DAX
        st.markdown("#### 💻 Código DAX")
        st.code(dax_code, language="dax")

        # Tabs con información
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Análisis",
            "⚙️ Funciones",
            "🔗 Referencias",
            "💡 Insights"
        ])

        with tab1:
            self._show_analysis_tab(analysis, measure_name)

        with tab2:
            self._show_functions_tab(analysis)

        with tab3:
            self._show_references_tab(analysis)

        with tab4:
            self._show_insights_tab(analysis, parameters)

    def _show_analysis_tab(self, analysis: DAXAnalysis, measure_name: str):
        """Tab de análisis general"""
        st.markdown("### 📈 Análisis General")

        # Explicación
        explanation = self.analyzer.explain_measure(analysis, measure_name)
        st.info(explanation)

        # Métricas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Líneas", analysis.line_count)

        with col2:
            st.metric("Caracteres", analysis.char_count)

        with col3:
            st.metric("Funciones", len(analysis.functions_used))

        with col4:
            st.metric("Referencias", len(analysis.tables_referenced))

        st.markdown("---")

        # Características
        st.markdown("### ✨ Características")

        features = []
        if analysis.has_variables:
            features.append("✅ Usa variables (VAR)")
        else:
            features.append("❌ No usa variables")

        if analysis.has_iterators:
            features.append("✅ Usa iteradores (row context)")
        else:
            features.append("❌ No usa iteradores")

        if analysis.has_time_intelligence:
            features.append("✅ Time Intelligence")
        else:
            features.append("❌ No es Time Intelligence")

        for feature in features:
            st.markdown(f"- {feature}")

    def _show_functions_tab(self, analysis: DAXAnalysis):
        """Tab de funciones usadas"""
        st.markdown("### ⚙️ Funciones DAX Utilizadas")

        if not analysis.functions_used:
            st.info("No se detectaron funciones DAX específicas")
            return

        # Categorizar funciones
        categories = self.analyzer.get_function_categories(analysis.functions_used)

        for category, functions in categories.items():
            with st.expander(f"**{category}** ({len(functions)})", expanded=True):
                # Mostrar en columnas
                cols = st.columns(3)
                for idx, func in enumerate(functions):
                    with cols[idx % 3]:
                        st.markdown(f"• `{func}`")

        # Resumen
        st.markdown("---")
        st.markdown("### 📊 Distribución")

        # Crear diccionario para mostrar
        category_counts = {cat: len(funcs) for cat, funcs in categories.items()}

        # Mostrar como métricas
        cols = st.columns(len(category_counts))
        for idx, (category, count) in enumerate(category_counts.items()):
            with cols[idx]:
                st.metric(category, count)

    def _show_references_tab(self, analysis: DAXAnalysis):
        """Tab de referencias a tablas, columnas y medidas"""
        st.markdown("### 🔗 Referencias del Modelo")

        col1, col2 = st.columns(2)

        with col1:
            # Tablas
            st.markdown("#### 📁 Tablas Referenciadas")
            if analysis.tables_referenced:
                for table in analysis.tables_referenced:
                    st.markdown(f"• `{table}`")
            else:
                st.caption("No se detectaron referencias a tablas")

            st.markdown("---")

            # Columnas
            st.markdown("#### 📊 Columnas Referenciadas")
            if analysis.columns_referenced:
                for column in analysis.columns_referenced:
                    st.markdown(f"• `{column}`")
            else:
                st.caption("No se detectaron referencias a columnas")

        with col2:
            # Medidas
            st.markdown("#### 📐 Medidas Referenciadas")
            if analysis.measures_referenced:
                for measure in analysis.measures_referenced:
                    st.markdown(f"• `[{measure}]`")
            else:
                st.caption("No se detectaron referencias a otras medidas")

        # Resumen
        st.markdown("---")
        st.markdown("### 📈 Resumen de Referencias")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tablas", len(analysis.tables_referenced))
        with col2:
            st.metric("Columnas", len(analysis.columns_referenced))
        with col3:
            st.metric("Medidas", len(analysis.measures_referenced))

    def _show_insights_tab(self, analysis: DAXAnalysis, parameters: Optional[Dict]):
        """Tab de insights, warnings y tips"""
        st.markdown("### 💡 Insights y Recomendaciones")

        # Performance warnings
        if analysis.performance_warnings:
            st.markdown("#### ⚠️ Advertencias de Performance")
            for warning in analysis.performance_warnings:
                st.warning(warning)
        else:
            st.success("✅ No se detectaron problemas de performance")

        st.markdown("---")

        # Tips de optimización
        st.markdown("#### 💡 Tips de Optimización")
        if analysis.performance_tips:
            for tip in analysis.performance_tips:
                st.info(tip)
        else:
            st.info("No hay recomendaciones adicionales")

        st.markdown("---")

        # Parámetros usados
        if parameters:
            st.markdown("#### ⚙️ Parámetros Utilizados")
            param_df_data = []
            for key, value in parameters.items():
                param_df_data.append({
                    "Parámetro": key,
                    "Valor": value
                })

            if param_df_data:
                import pandas as pd
                df = pd.DataFrame(param_df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

        # Score general
        st.markdown("---")
        st.markdown("#### 🎯 Score General")

        # Barra de progreso para complejidad
        st.markdown("**Complejidad:**")
        complexity_color = "normal"
        if analysis.complexity_score > 75:
            complexity_color = "red"
        elif analysis.complexity_score > 50:
            complexity_color = "orange"

        # No podemos cambiar color del progress bar fácilmente, usar métrica
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(analysis.complexity_score / 100)
        with col2:
            st.metric("", f"{analysis.complexity_score}/100")

        # Recomendación final
        st.markdown("---")
        if analysis.estimated_performance == 'Good' and analysis.complexity_level in ['Low', 'Medium']:
            st.success("✅ **Esta medida está bien optimizada y lista para usar**")
        elif analysis.estimated_performance == 'Fair':
            st.info("ℹ️ **Esta medida es aceptable, pero podría optimizarse**")
        else:
            st.warning("⚠️ **Considera revisar y optimizar esta medida antes de usar en producción**")


def show_enriched_preview_ui(
    dax_code: str,
    measure_name: str,
    template_name: str,
    parameters: Optional[Dict] = None
):
    """
    Función helper para mostrar preview enriquecido

    Args:
        dax_code: Código DAX generado
        measure_name: Nombre de la medida
        template_name: Nombre del template
        parameters: Parámetros usados
    """
    preview = EnrichedPreview()
    preview.show_enriched_preview(dax_code, measure_name, template_name, parameters)


def show_quick_analysis(dax_code: str, measure_name: str):
    """
    Análisis rápido para mostrar en preview simple

    Args:
        dax_code: Código DAX
        measure_name: Nombre de la medida

    Returns:
        None (muestra en streamlit)
    """
    analyzer = DAXAnalyzer()
    analysis = analyzer.analyze(dax_code)

    # Mostrar solo métricas clave
    col1, col2, col3 = st.columns(3)

    with col1:
        complexity_icons = {
            'Low': '🟢',
            'Medium': '🟡',
            'High': '🟠',
            'Very High': '🔴'
        }
        icon = complexity_icons.get(analysis.complexity_level, '⚪')
        st.metric("Complejidad", f"{icon} {analysis.complexity_level}")

    with col2:
        perf_icons = {
            'Good': '✅',
            'Fair': '⚠️',
            'Poor': '❌'
        }
        icon = perf_icons.get(analysis.estimated_performance, '⚪')
        st.metric("Performance", f"{icon} {analysis.estimated_performance}")

    with col3:
        st.metric("Funciones", len(analysis.functions_used))

    # Warnings si hay
    if analysis.performance_warnings:
        with st.expander("⚠️ Advertencias", expanded=False):
            for warning in analysis.performance_warnings:
                st.warning(warning)
