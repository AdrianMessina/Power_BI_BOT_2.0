"""
Template Manager - Gestor central de todos los templates DAX
Proporciona interfaz unificada para acceder y usar templates
"""

from typing import List, Dict, Optional, Tuple
from .base_template import DAXTemplate
from .time_intelligence import TimeIntelligenceTemplates
from .aggregations import AggregationTemplates
from .calculations import CalculationTemplates
from .advanced import AdvancedTemplates
from .ypf_business import YPFBusinessTemplates


class TemplateManager:
    """
    Gestor central de templates DAX
    Proporciona búsqueda, filtrado y generación de código DAX
    """

    def __init__(self):
        """Inicializa el manager cargando todas las colecciones"""
        self.collections = {
            'time_intelligence': TimeIntelligenceTemplates(),
            'aggregations': AggregationTemplates(),
            'calculations': CalculationTemplates(),
            'advanced': AdvancedTemplates(),
            'ypf_business': YPFBusinessTemplates()
        }

        # Índice de todos los templates
        self.all_templates: List[DAXTemplate] = []
        self._build_index()

    def _build_index(self):
        """Construye índice de todos los templates disponibles"""
        self.all_templates = []
        for collection in self.collections.values():
            self.all_templates.extend(collection.list_templates())

    def get_template(self, template_id: str) -> Optional[DAXTemplate]:
        """
        Obtiene un template por su ID

        Args:
            template_id: ID del template

        Returns:
            DAXTemplate si existe, None si no
        """
        for template in self.all_templates:
            if template.id == template_id:
                return template
        return None

    def list_all_templates(self) -> List[DAXTemplate]:
        """Retorna todos los templates disponibles"""
        return self.all_templates

    def list_by_category(self, category: str) -> List[DAXTemplate]:
        """
        Lista templates de una categoría específica

        Args:
            category: 'Time Intelligence', 'Aggregations', 'Calculations', 'Advanced'
        """
        return [t for t in self.all_templates if t.category == category]

    def list_by_difficulty(self, difficulty: str) -> List[DAXTemplate]:
        """
        Lista templates por nivel de dificultad

        Args:
            difficulty: 'basic', 'intermediate', 'advanced'
        """
        return [t for t in self.all_templates if t.difficulty == difficulty]

    def search(self, query: str) -> List[DAXTemplate]:
        """
        Busca templates por nombre, descripción o tags

        Args:
            query: Término de búsqueda

        Returns:
            Lista de templates que coinciden
        """
        query_lower = query.lower()
        results = []

        for template in self.all_templates:
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    def generate_dax(
        self,
        template_id: str,
        parameters: Dict[str, str]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Genera código DAX a partir de un template y parámetros

        Args:
            template_id: ID del template a usar
            parameters: Diccionario con parámetros del template

        Returns:
            Tupla (success, message, dax_code)
            - success: True si se generó correctamente
            - message: Mensaje de éxito o error
            - dax_code: Código DAX generado (None si error)
        """
        template = self.get_template(template_id)

        if not template:
            return False, f"Template '{template_id}' no encontrado", None

        try:
            # Validar parámetros
            is_valid, error = template.validate_parameters(parameters)
            if not is_valid:
                return False, error, None

            # Generar código
            measure_name, dax_expression = template.generate(parameters)

            # El template ya incluye el formato completo
            # Solo retornamos la expresión tal cual
            dax_code = dax_expression

            return True, f"Medida '{measure_name}' generada correctamente", dax_code

        except Exception as e:
            return False, f"Error al generar DAX: {str(e)}", None

    def get_template_info(self, template_id: str) -> Optional[str]:
        """
        Obtiene información detallada de un template

        Args:
            template_id: ID del template

        Returns:
            String con información formateada, None si no existe
        """
        template = self.get_template(template_id)
        if not template:
            return None

        return template.get_help()

    def get_categories(self) -> List[str]:
        """Retorna lista de categorías disponibles"""
        categories = set(t.category for t in self.all_templates)
        return sorted(list(categories))

    def get_stats(self) -> Dict[str, any]:
        """Retorna estadísticas del catálogo"""
        stats = {
            'total_templates': len(self.all_templates),
            'by_category': {},
            'by_difficulty': {
                'basic': 0,
                'intermediate': 0,
                'advanced': 0
            },
            'requires_date_table': 0
        }

        # Contar por categoría
        for template in self.all_templates:
            category = template.category
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1

            # Contar por dificultad
            stats['by_difficulty'][template.difficulty] += 1

            # Contar los que requieren tabla de fechas
            if template.requires_date_table:
                stats['requires_date_table'] += 1

        return stats

    def suggest_templates(
        self,
        user_input: str,
        limit: int = 5
    ) -> List[DAXTemplate]:
        """
        Sugiere templates relevantes basados en input del usuario

        Args:
            user_input: Texto del usuario
            limit: Máximo número de sugerencias

        Returns:
            Lista de templates sugeridos
        """
        user_input_lower = user_input.lower()

        # Palabras clave para diferentes categorías
        keywords = {
            'time': ['año', 'mes', 'día', 'fecha', 'ytd', 'mtd', 'year', 'month',
                     'anterior', 'last', 'previous', 'acumulado', 'running'],
            'aggregation': ['suma', 'total', 'promedio', 'count', 'contar',
                           'sum', 'average', 'max', 'min', 'máximo', 'mínimo'],
            'calculation': ['porcentaje', 'ratio', 'margen', 'margin', 'growth',
                           'crecimiento', 'varianza', 'variance', '%'],
            'advanced': ['ranking', 'top', 'abc', 'pareto', 'clasificación',
                        'rank', 'classification']
        }

        # Detectar categoría más relevante
        category_scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in user_input_lower)
            if score > 0:
                category_scores[category] = score

        # Si detectamos una categoría, filtrar por ella
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)

            # Mapeo de categoría a categoría real
            category_map = {
                'time': 'Time Intelligence',
                'aggregation': 'Aggregations',
                'calculation': 'Calculations',
                'advanced': 'Advanced'
            }

            templates = self.list_by_category(category_map[best_category])
        else:
            templates = self.all_templates

        # Buscar coincidencias de texto
        results = self.search(user_input)

        # Si no hay resultados, retornar templates básicos de la categoría
        if not results and templates:
            results = [t for t in templates if t.difficulty == 'basic'][:limit]

        return results[:limit]

    def get_template_by_name(self, name: str) -> Optional[DAXTemplate]:
        """
        Busca template por nombre exacto (case-insensitive)

        Args:
            name: Nombre del template

        Returns:
            Template si existe, None si no
        """
        name_lower = name.lower()
        for template in self.all_templates:
            if template.name.lower() == name_lower:
                return template
        return None

    def validate_parameters_for_template(
        self,
        template_id: str,
        parameters: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida parámetros sin generar código

        Args:
            template_id: ID del template
            parameters: Parámetros a validar

        Returns:
            Tupla (is_valid, error_message)
        """
        template = self.get_template(template_id)
        if not template:
            return False, f"Template '{template_id}' no encontrado"

        return template.validate_parameters(parameters)

    def get_template_parameters(self, template_id: str) -> Optional[List]:
        """
        Obtiene lista de parámetros requeridos por un template

        Args:
            template_id: ID del template

        Returns:
            Lista de TemplateParameter o None
        """
        template = self.get_template(template_id)
        if not template:
            return None

        return template.parameters

    def list_templates_summary(self) -> str:
        """
        Genera resumen legible de todos los templates disponibles

        Returns:
            String formateado con resumen
        """
        summary = "📚 **Catálogo de Templates DAX**\n\n"

        stats = self.get_stats()
        summary += f"**Total de templates:** {stats['total_templates']}\n\n"

        for category in sorted(stats['by_category'].keys()):
            count = stats['by_category'][category]
            summary += f"### {category} ({count} templates)\n"

            templates = self.list_by_category(category)
            for t in templates:
                difficulty_icon = {
                    'basic': '🟢',
                    'intermediate': '🟡',
                    'advanced': '🔴'
                }
                icon = difficulty_icon.get(t.difficulty, '⚪')
                date_req = ' 📅' if t.requires_date_table else ''
                summary += f"- {icon} **{t.name}**{date_req}: {t.description}\n"

            summary += "\n"

        summary += "\n**Leyenda:**\n"
        summary += "🟢 Básico | 🟡 Intermedio | 🔴 Avanzado | 📅 Requiere tabla de fechas\n"

        return summary
