"""
Gestión de Templates Personalizados
Permite crear, editar, guardar y cargar templates custom del usuario
"""

import json
import os
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from templates.base_template import DAXTemplate, TemplateParameter


@dataclass
class CustomTemplateMetadata:
    """Metadata de un template custom"""
    created_at: str
    updated_at: str
    author: str
    version: str
    usage_count: int = 0


class CustomTemplateManager:
    """
    Gestor de templates personalizados del usuario
    """

    def __init__(self, storage_path: str = "output/custom_templates.json"):
        """
        Args:
            storage_path: Ruta al archivo de almacenamiento
        """
        self.storage_path = storage_path
        self.templates: Dict[str, dict] = {}
        self._ensure_storage_dir()
        self.load_templates()

    def _ensure_storage_dir(self):
        """Asegura que el directorio de almacenamiento existe"""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)

    def load_templates(self) -> bool:
        """
        Carga templates desde archivo

        Returns:
            True si se cargó exitosamente
        """
        if not os.path.exists(self.storage_path):
            self.templates = {}
            return True

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
            return True
        except Exception as e:
            print(f"Error cargando templates: {e}")
            self.templates = {}
            return False

    def save_templates(self) -> bool:
        """
        Guarda templates a archivo

        Returns:
            True si se guardó exitosamente
        """
        try:
            data = {
                'templates': self.templates,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error guardando templates: {e}")
            return False

    def create_template(
        self,
        template_id: str,
        name: str,
        description: str,
        category: str,
        template_code: str,
        parameters: List[Dict],
        difficulty: str = 'intermediate',
        tags: List[str] = None,
        example: str = "",
        requires_date_table: bool = False,
        author: str = "User"
    ) -> bool:
        """
        Crea un nuevo template personalizado

        Args:
            template_id: ID único del template
            name: Nombre del template
            description: Descripción
            category: Categoría (Custom Templates por default)
            template_code: Código DAX con placeholders
            parameters: Lista de dicts con info de parámetros
            difficulty: basic, intermediate, advanced
            tags: Lista de tags para búsqueda
            example: Ejemplo de uso
            requires_date_table: Si requiere tabla de fechas
            author: Nombre del autor

        Returns:
            True si se creó exitosamente
        """
        # Validar que no existe
        if template_id in self.templates:
            return False

        # Crear metadata
        now = datetime.now().isoformat()
        metadata = {
            'created_at': now,
            'updated_at': now,
            'author': author,
            'version': '1.0',
            'usage_count': 0
        }

        # Crear template
        template_data = {
            'id': template_id,
            'name': name,
            'description': description,
            'category': category if category else 'Custom Templates',
            'template_code': template_code,
            'parameters': parameters,
            'difficulty': difficulty,
            'tags': tags if tags else [],
            'example': example,
            'requires_date_table': requires_date_table,
            'metadata': metadata
        }

        # Guardar
        self.templates[template_id] = template_data
        return self.save_templates()

    def update_template(
        self,
        template_id: str,
        **kwargs
    ) -> bool:
        """
        Actualiza un template existente

        Args:
            template_id: ID del template a actualizar
            **kwargs: Campos a actualizar

        Returns:
            True si se actualizó exitosamente
        """
        if template_id not in self.templates:
            return False

        # Actualizar campos permitidos
        allowed_fields = [
            'name', 'description', 'category', 'template_code',
            'parameters', 'difficulty', 'tags', 'example',
            'requires_date_table'
        ]

        for key, value in kwargs.items():
            if key in allowed_fields:
                self.templates[template_id][key] = value

        # Actualizar metadata
        self.templates[template_id]['metadata']['updated_at'] = datetime.now().isoformat()

        # Incrementar versión
        current_version = self.templates[template_id]['metadata'].get('version', '1.0')
        version_parts = current_version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        self.templates[template_id]['metadata']['version'] = '.'.join(version_parts)

        return self.save_templates()

    def delete_template(self, template_id: str) -> bool:
        """
        Elimina un template personalizado

        Args:
            template_id: ID del template

        Returns:
            True si se eliminó exitosamente
        """
        if template_id not in self.templates:
            return False

        del self.templates[template_id]
        return self.save_templates()

    def get_template(self, template_id: str) -> Optional[dict]:
        """
        Obtiene un template por ID

        Args:
            template_id: ID del template

        Returns:
            Dict con datos del template o None
        """
        return self.templates.get(template_id)

    def list_templates(self) -> List[dict]:
        """
        Lista todos los templates personalizados

        Returns:
            Lista de dicts con templates
        """
        return list(self.templates.values())

    def get_template_count(self) -> int:
        """Retorna cantidad de templates personalizados"""
        return len(self.templates)

    def search_templates(self, query: str) -> List[dict]:
        """
        Busca templates por nombre, descripción o tags

        Args:
            query: Término de búsqueda

        Returns:
            Lista de templates que coinciden
        """
        query_lower = query.lower()
        results = []

        for template in self.templates.values():
            if (query_lower in template['name'].lower() or
                query_lower in template['description'].lower() or
                any(query_lower in tag.lower() for tag in template.get('tags', []))):
                results.append(template)

        return results

    def increment_usage(self, template_id: str):
        """
        Incrementa contador de uso de un template

        Args:
            template_id: ID del template
        """
        if template_id in self.templates:
            self.templates[template_id]['metadata']['usage_count'] += 1
            self.save_templates()

    def convert_to_dax_template(self, template_data: dict) -> Optional[DAXTemplate]:
        """
        Convierte un template custom a DAXTemplate para usar con TemplateManager

        Args:
            template_data: Dict con datos del template

        Returns:
            DAXTemplate o None si error
        """
        try:
            # Convertir parámetros
            parameters = []
            for param_data in template_data.get('parameters', []):
                param = TemplateParameter(
                    name=param_data['name'],
                    type=param_data['type'],
                    description=param_data['description'],
                    required=param_data.get('required', True)
                )
                parameters.append(param)

            # Crear DAXTemplate
            template = DAXTemplate(
                id=template_data['id'],
                name=template_data['name'],
                category=template_data.get('category', 'Custom Templates'),
                description=template_data['description'],
                difficulty=template_data.get('difficulty', 'intermediate'),
                parameters=parameters,
                template_code=template_data['template_code'],
                example=template_data.get('example', ''),
                tags=template_data.get('tags', []),
                requires_date_table=template_data.get('requires_date_table', False)
            )

            return template

        except Exception as e:
            print(f"Error convirtiendo template: {e}")
            return None

    def export_template(self, template_id: str, output_path: str) -> bool:
        """
        Exporta un template a archivo JSON

        Args:
            template_id: ID del template
            output_path: Ruta del archivo de salida

        Returns:
            True si se exportó exitosamente
        """
        template = self.get_template(template_id)
        if not template:
            return False

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exportando template: {e}")
            return False

    def import_template(self, file_path: str) -> Optional[str]:
        """
        Importa un template desde archivo JSON

        Args:
            file_path: Ruta del archivo a importar

        Returns:
            ID del template importado o None si error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            # Validar campos requeridos
            required_fields = ['id', 'name', 'description', 'template_code', 'parameters']
            if not all(field in template_data for field in required_fields):
                return None

            # Verificar si ya existe
            template_id = template_data['id']
            if template_id in self.templates:
                # Generar nuevo ID
                base_id = template_id
                counter = 1
                while f"{base_id}_{counter}" in self.templates:
                    counter += 1
                template_id = f"{base_id}_{counter}"
                template_data['id'] = template_id
                template_data['name'] = f"{template_data['name']} (imported)"

            # Actualizar metadata
            now = datetime.now().isoformat()
            template_data['metadata'] = {
                'created_at': now,
                'updated_at': now,
                'author': template_data.get('metadata', {}).get('author', 'Unknown'),
                'version': template_data.get('metadata', {}).get('version', '1.0'),
                'usage_count': 0
            }

            # Guardar
            self.templates[template_id] = template_data
            self.save_templates()

            return template_id

        except Exception as e:
            print(f"Error importando template: {e}")
            return None

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de templates personalizados

        Returns:
            Dict con estadísticas
        """
        total = len(self.templates)
        total_usage = sum(
            t['metadata'].get('usage_count', 0)
            for t in self.templates.values()
        )

        categories = {}
        difficulties = {'basic': 0, 'intermediate': 0, 'advanced': 0}

        for template in self.templates.values():
            category = template.get('category', 'Custom Templates')
            categories[category] = categories.get(category, 0) + 1

            difficulty = template.get('difficulty', 'intermediate')
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1

        return {
            'total': total,
            'total_usage': total_usage,
            'by_category': categories,
            'by_difficulty': difficulties
        }
