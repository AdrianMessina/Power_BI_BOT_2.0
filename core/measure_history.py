"""
Historial de Medidas Creadas
Sistema para guardar y recuperar medidas generadas por el usuario
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class MeasureHistoryEntry:
    """Representa una entrada en el historial de medidas"""
    measure_name: str
    template_id: str
    template_name: str
    dax_code: str
    parameters: Dict[str, str]
    timestamp: str
    category: str
    applied: bool  # Si se aplicó al modelo o solo se copió
    notes: str = ""

    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'MeasureHistoryEntry':
        """Crea desde diccionario"""
        return MeasureHistoryEntry(**data)


class MeasureHistory:
    """Gestor del historial de medidas creadas"""

    def __init__(self, history_file: str = "output/measure_history.json"):
        """
        Args:
            history_file: Ruta al archivo de historial
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[MeasureHistoryEntry] = []
        self._load_history()

    def _load_history(self):
        """Carga el historial desde archivo"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [
                        MeasureHistoryEntry.from_dict(entry)
                        for entry in data
                    ]
            except Exception as e:
                print(f"Error cargando historial: {e}")
                self.entries = []
        else:
            self.entries = []

    def _save_history(self):
        """Guarda el historial a archivo"""
        try:
            data = [entry.to_dict() for entry in self.entries]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def add_entry(
        self,
        measure_name: str,
        template_id: str,
        template_name: str,
        dax_code: str,
        parameters: Dict[str, str],
        category: str,
        applied: bool = False,
        notes: str = ""
    ):
        """
        Agrega una nueva entrada al historial

        Args:
            measure_name: Nombre de la medida
            template_id: ID del template usado
            template_name: Nombre del template
            dax_code: Código DAX generado
            parameters: Parámetros usados
            category: Categoría del template
            applied: Si se aplicó al modelo
            notes: Notas adicionales
        """
        entry = MeasureHistoryEntry(
            measure_name=measure_name,
            template_id=template_id,
            template_name=template_name,
            dax_code=dax_code,
            parameters=parameters,
            timestamp=datetime.now().isoformat(),
            category=category,
            applied=applied,
            notes=notes
        )

        self.entries.insert(0, entry)  # Más reciente primero
        self._save_history()

    def get_all(self) -> List[MeasureHistoryEntry]:
        """Retorna todas las entradas del historial"""
        return self.entries

    def get_recent(self, limit: int = 10) -> List[MeasureHistoryEntry]:
        """Retorna las N entradas más recientes"""
        return self.entries[:limit]

    def get_by_template(self, template_id: str) -> List[MeasureHistoryEntry]:
        """Retorna entradas que usaron un template específico"""
        return [e for e in self.entries if e.template_id == template_id]

    def get_by_category(self, category: str) -> List[MeasureHistoryEntry]:
        """Retorna entradas de una categoría específica"""
        return [e for e in self.entries if e.category == category]

    def search(self, query: str) -> List[MeasureHistoryEntry]:
        """Busca en el historial por nombre de medida o código DAX"""
        query_lower = query.lower()
        results = []

        for entry in self.entries:
            if (query_lower in entry.measure_name.lower() or
                query_lower in entry.dax_code.lower() or
                query_lower in entry.template_name.lower()):
                results.append(entry)

        return results

    def get_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[MeasureHistoryEntry]:
        """
        Retorna entradas en un rango de fechas

        Args:
            start_date: Fecha inicio (ISO format)
            end_date: Fecha fin (ISO format)
        """
        results = []

        for entry in self.entries:
            entry_date = entry.timestamp

            if start_date and entry_date < start_date:
                continue
            if end_date and entry_date > end_date:
                continue

            results.append(entry)

        return results

    def delete_entry(self, index: int):
        """Elimina una entrada del historial por índice"""
        if 0 <= index < len(self.entries):
            self.entries.pop(index)
            self._save_history()

    def clear_history(self):
        """Limpia todo el historial"""
        self.entries = []
        self._save_history()

    def get_stats(self) -> Dict:
        """Retorna estadísticas del historial"""
        total = len(self.entries)
        applied = sum(1 for e in self.entries if e.applied)
        copied = total - applied

        # Contar por categoría
        by_category = {}
        for entry in self.entries:
            cat = entry.category
            by_category[cat] = by_category.get(cat, 0) + 1

        # Contar por template
        by_template = {}
        for entry in self.entries:
            tmpl = entry.template_name
            by_template[tmpl] = by_template.get(tmpl, 0) + 1

        # Top 5 templates más usados
        top_templates = sorted(
            by_template.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total': total,
            'applied': applied,
            'copied': copied,
            'by_category': by_category,
            'top_templates': dict(top_templates)
        }

    def export_entry_to_file(
        self,
        entry: MeasureHistoryEntry,
        output_path: str
    ):
        """
        Exporta una entrada a un archivo .dax

        Args:
            entry: Entrada a exportar
            output_path: Ruta del archivo de salida
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""// Medida: {entry.measure_name}
// Template: {entry.template_name} ({entry.template_id})
// Categoría: {entry.category}
// Creada: {entry.timestamp}
// Aplicada: {'Sí' if entry.applied else 'No'}

// Parámetros usados:
"""
        for key, value in entry.parameters.items():
            content += f"// - {key}: {value}\n"

        content += f"""
// Código DAX:
{entry.dax_code}
"""

        if entry.notes:
            content += f"\n// Notas: {entry.notes}\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def export_all_to_file(self, output_path: str):
        """
        Exporta todo el historial a un archivo

        Args:
            output_path: Ruta del archivo de salida
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""// ============================================
// HISTORIAL DE MEDIDAS DAX
// Power BI Bot - YPF RTIC
// Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Total de medidas: {len(self.entries)}
// ============================================

"""

        for i, entry in enumerate(self.entries, 1):
            content += f"""
// ============================================
// Medida #{i}: {entry.measure_name}
// ============================================
// Template: {entry.template_name}
// Categoría: {entry.category}
// Fecha: {entry.timestamp}
// Estado: {'Aplicada al modelo' if entry.applied else 'Solo generada/copiada'}

{entry.dax_code}

"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
