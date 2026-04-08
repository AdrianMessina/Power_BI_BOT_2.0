"""
Sistema de Favoritos para Templates
Permite marcar templates favoritos para acceso rápido
"""

import json
import os
from typing import List, Set, Dict
from datetime import datetime


class FavoritesManager:
    """
    Gestor de templates favoritos
    """

    def __init__(self, storage_path: str = "output/favorites.json"):
        """
        Args:
            storage_path: Ruta al archivo de almacenamiento
        """
        self.storage_path = storage_path
        self.favorites: Set[str] = set()
        self.metadata: Dict[str, dict] = {}
        self._ensure_storage_dir()
        self.load()

    def _ensure_storage_dir(self):
        """Asegura que el directorio existe"""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)

    def load(self) -> bool:
        """
        Carga favoritos desde archivo

        Returns:
            True si se cargó exitosamente
        """
        if not os.path.exists(self.storage_path):
            self.favorites = set()
            self.metadata = {}
            return True

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.favorites = set(data.get('favorites', []))
                self.metadata = data.get('metadata', {})
            return True
        except Exception as e:
            print(f"Error cargando favoritos: {e}")
            self.favorites = set()
            self.metadata = {}
            return False

    def save(self) -> bool:
        """
        Guarda favoritos a archivo

        Returns:
            True si se guardó exitosamente
        """
        try:
            data = {
                'favorites': list(self.favorites),
                'metadata': self.metadata,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error guardando favoritos: {e}")
            return False

    def add_favorite(self, template_id: str, template_name: str = None) -> bool:
        """
        Agrega un template a favoritos

        Args:
            template_id: ID del template
            template_name: Nombre del template (opcional)

        Returns:
            True si se agregó exitosamente
        """
        self.favorites.add(template_id)

        # Guardar metadata
        self.metadata[template_id] = {
            'name': template_name if template_name else template_id,
            'added_at': datetime.now().isoformat(),
            'access_count': self.metadata.get(template_id, {}).get('access_count', 0)
        }

        return self.save()

    def remove_favorite(self, template_id: str) -> bool:
        """
        Remueve un template de favoritos

        Args:
            template_id: ID del template

        Returns:
            True si se removió exitosamente
        """
        if template_id in self.favorites:
            self.favorites.remove(template_id)

            if template_id in self.metadata:
                del self.metadata[template_id]

            return self.save()

        return False

    def is_favorite(self, template_id: str) -> bool:
        """
        Verifica si un template es favorito

        Args:
            template_id: ID del template

        Returns:
            True si es favorito
        """
        return template_id in self.favorites

    def toggle_favorite(self, template_id: str, template_name: str = None) -> bool:
        """
        Alterna estado de favorito

        Args:
            template_id: ID del template
            template_name: Nombre del template

        Returns:
            True si ahora es favorito, False si se removió
        """
        if self.is_favorite(template_id):
            self.remove_favorite(template_id)
            return False
        else:
            self.add_favorite(template_id, template_name)
            return True

    def get_favorites(self) -> List[str]:
        """
        Obtiene lista de templates favoritos

        Returns:
            Lista de IDs de templates favoritos
        """
        return list(self.favorites)

    def get_favorites_count(self) -> int:
        """Retorna cantidad de favoritos"""
        return len(self.favorites)

    def increment_access(self, template_id: str):
        """
        Incrementa contador de accesos a un favorito

        Args:
            template_id: ID del template
        """
        if template_id in self.favorites and template_id in self.metadata:
            self.metadata[template_id]['access_count'] = \
                self.metadata[template_id].get('access_count', 0) + 1
            self.metadata[template_id]['last_accessed'] = datetime.now().isoformat()
            self.save()

    def get_most_accessed(self, limit: int = 5) -> List[tuple]:
        """
        Obtiene favoritos más accedidos

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de tuplas (template_id, access_count)
        """
        favorites_with_count = [
            (template_id, self.metadata.get(template_id, {}).get('access_count', 0))
            for template_id in self.favorites
        ]

        sorted_favorites = sorted(favorites_with_count, key=lambda x: x[1], reverse=True)
        return sorted_favorites[:limit]

    def get_recently_added(self, limit: int = 5) -> List[str]:
        """
        Obtiene favoritos agregados recientemente

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de template IDs
        """
        favorites_with_date = [
            (template_id, self.metadata.get(template_id, {}).get('added_at', ''))
            for template_id in self.favorites
        ]

        sorted_favorites = sorted(favorites_with_date, key=lambda x: x[1], reverse=True)
        return [fav[0] for fav in sorted_favorites[:limit]]

    def export_favorites(self, output_path: str) -> bool:
        """
        Exporta favoritos a archivo

        Args:
            output_path: Ruta del archivo de salida

        Returns:
            True si se exportó exitosamente
        """
        try:
            data = {
                'favorites': list(self.favorites),
                'metadata': self.metadata,
                'exported_at': datetime.now().isoformat()
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error exportando favoritos: {e}")
            return False

    def import_favorites(self, file_path: str, merge: bool = True) -> bool:
        """
        Importa favoritos desde archivo

        Args:
            file_path: Ruta del archivo a importar
            merge: Si True, combina con favoritos existentes; si False, reemplaza

        Returns:
            True si se importó exitosamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_favorites = set(data.get('favorites', []))
            imported_metadata = data.get('metadata', {})

            if merge:
                # Combinar con existentes
                self.favorites.update(imported_favorites)
                self.metadata.update(imported_metadata)
            else:
                # Reemplazar
                self.favorites = imported_favorites
                self.metadata = imported_metadata

            return self.save()

        except Exception as e:
            print(f"Error importando favoritos: {e}")
            return False

    def clear_favorites(self) -> bool:
        """
        Elimina todos los favoritos

        Returns:
            True si se eliminaron exitosamente
        """
        self.favorites.clear()
        self.metadata.clear()
        return self.save()

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de favoritos

        Returns:
            Dict con estadísticas
        """
        total_access = sum(
            meta.get('access_count', 0)
            for meta in self.metadata.values()
        )

        return {
            'total': len(self.favorites),
            'total_access': total_access,
            'avg_access': total_access / len(self.favorites) if self.favorites else 0,
            'most_accessed': self.get_most_accessed(3),
            'recently_added': self.get_recently_added(3)
        }
