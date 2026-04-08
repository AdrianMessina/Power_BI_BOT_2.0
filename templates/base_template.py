"""
Clase base para templates DAX
Define la estructura común de todos los templates
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class TemplateParameter:
    """Define un parámetro de template"""
    name: str
    description: str
    type: str  # 'measure', 'table', 'column', 'text', 'date_column'
    required: bool = True
    default: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None


@dataclass
class DAXTemplate:
    """Representa un template DAX completo"""
    id: str
    name: str
    description: str
    category: str
    difficulty: str  # 'basic', 'intermediate', 'advanced'
    parameters: List[TemplateParameter]
    dax_template: str
    example: str
    tags: List[str]
    requires_date_table: bool = False

    def validate_parameters(self, params: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """
        Valida que todos los parámetros requeridos estén presentes
        Returns: (is_valid, error_message)
        """
        for param in self.parameters:
            if param.required and param.name not in params:
                return False, f"Parámetro requerido faltante: {param.name} ({param.description})"

        return True, None

    def generate(self, params: Dict[str, str]) -> tuple[str, str]:
        """
        Genera el código DAX a partir de los parámetros
        Returns: (measure_name, dax_expression)
        """
        # Validar parámetros
        is_valid, error = self.validate_parameters(params)
        if not is_valid:
            raise ValueError(error)

        # Generar nombre de medida (si no se proporciona)
        measure_name = params.get('measure_name', self._generate_default_name(params))

        # Reemplazar placeholders en el template
        dax_code = self.dax_template
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            dax_code = dax_code.replace(placeholder, value)

        # Limpiar corchetes dobles que puedan resultar del reemplazo
        dax_code = dax_code.replace('[[', '[').replace(']]', ']')

        return measure_name, dax_code

    def _generate_default_name(self, params: Dict[str, str]) -> str:
        """Genera nombre por defecto basado en parámetros"""
        return f"{self.name}_{params.get('base_measure', 'Measure')}"

    def get_help(self) -> str:
        """Retorna ayuda formateada sobre el template"""
        help_text = f"""
**{self.name}**
{self.description}

**Categoría:** {self.category}
**Dificultad:** {self.difficulty}

**Parámetros:**
"""
        for param in self.parameters:
            required = "✅ Requerido" if param.required else "⚪ Opcional"
            help_text += f"- **{param.name}** ({param.type}): {param.description} [{required}]\n"

        help_text += f"\n**Ejemplo:**\n```dax\n{self.example}\n```"

        if self.requires_date_table:
            help_text += "\n\n⚠️ **Requiere tabla de calendario/fechas**"

        return help_text


class BaseTemplateCollection(ABC):
    """Clase base para colecciones de templates"""

    def __init__(self):
        self.templates: List[DAXTemplate] = []
        self._load_templates()

    @abstractmethod
    def _load_templates(self):
        """Carga los templates de la colección"""
        pass

    def get_template(self, template_id: str) -> Optional[DAXTemplate]:
        """Obtiene un template por ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None

    def list_templates(self) -> List[DAXTemplate]:
        """Lista todos los templates de la colección"""
        return self.templates

    def search_templates(self, query: str) -> List[DAXTemplate]:
        """Busca templates por nombre, descripción o tags"""
        query_lower = query.lower()
        results = []

        for template in self.templates:
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results
