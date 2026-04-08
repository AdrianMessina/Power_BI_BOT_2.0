"""
Validador de parámetros para templates DAX
Valida tipos, formatos y existencia de elementos en el modelo
"""

import re
from typing import Dict, Tuple, Optional, List


class ParameterValidator:
    """
    Valida parámetros de templates DAX contra el modelo actual
    """

    def __init__(self, model_data=None):
        """
        Args:
            model_data: Objeto con datos del modelo (tablas, medidas, columnas)
        """
        self.model_data = model_data

    def validate_parameter(
        self,
        param_name: str,
        param_value: str,
        param_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida un parámetro individual

        Args:
            param_name: Nombre del parámetro
            param_value: Valor del parámetro
            param_type: Tipo esperado ('measure', 'table', 'column', etc.)

        Returns:
            (is_valid, error_message)
        """
        # Validar que no esté vacío
        if not param_value or not param_value.strip():
            return False, f"El parámetro '{param_name}' no puede estar vacío"

        # Validar según tipo
        validator_map = {
            'measure': self._validate_measure,
            'table': self._validate_table,
            'column': self._validate_column,
            'date_column': self._validate_date_column,
            'text': self._validate_text
        }

        validator = validator_map.get(param_type, self._validate_text)
        return validator(param_value, param_name)

    def _validate_measure(
        self,
        value: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Valida nombre de medida [MeasureName]"""
        # Formato: [MeasureName]
        if not (value.startswith('[') and value.endswith(']')):
            return False, f"{param_name}: Formato incorrecto. Use [NombreMedida]"

        measure_name = value[1:-1]

        # Si tenemos datos del modelo, verificar que existe
        if self.model_data and hasattr(self.model_data, 'measures'):
            measure_exists = any(
                m.get('name') == measure_name or m.get('Name') == measure_name
                for m in self.model_data.measures
            )
            if not measure_exists:
                return False, f"Medida '{measure_name}' no existe en el modelo"

        return True, None

    def _validate_table(
        self,
        value: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Valida nombre de tabla (sin corchetes)"""
        # Verificar caracteres inválidos
        if any(char in value for char in ['[', ']', '.']):
            return False, f"{param_name}: Nombre de tabla no debe contener [], o ."

        # Si tenemos datos del modelo, verificar que existe
        if self.model_data and hasattr(self.model_data, 'tables'):
            table_exists = any(
                t.get('name') == value or t.get('Name') == value
                for t in self.model_data.tables
            )
            if not table_exists:
                return False, f"Tabla '{value}' no existe en el modelo"

        return True, None

    def _validate_column(
        self,
        value: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Valida referencia a columna Table[Column]"""
        # Formato: Table[Column]
        pattern = r"^([^\[\]]+)\[([^\[\]]+)\]$"
        match = re.match(pattern, value)

        if not match:
            return False, f"{param_name}: Formato incorrecto. Use Tabla[Columna]"

        table_name, column_name = match.groups()

        # Si tenemos datos del modelo, verificar
        if self.model_data and hasattr(self.model_data, 'tables'):
            # Verificar tabla
            table = next(
                (t for t in self.model_data.tables
                 if t.get('name') == table_name or t.get('Name') == table_name),
                None
            )

            if not table:
                return False, f"Tabla '{table_name}' no existe en el modelo"

            # Verificar columna (si la tabla tiene info de columnas)
            if 'columns' in table and table['columns']:
                column_exists = any(
                    c.get('name') == column_name or c.get('Name') == column_name
                    for c in table['columns']
                )
                if not column_exists:
                    return False, f"Columna '{column_name}' no existe en tabla '{table_name}'"

        return True, None

    def _validate_date_column(
        self,
        value: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Valida columna de fecha (mismo formato que columna)"""
        is_valid, error = self._validate_column(value, param_name)

        if not is_valid:
            return is_valid, error

        # Advertencia adicional (no error) si no podemos verificar tipo
        if not self.model_data:
            return True, None

        # TODO: Verificar que sea tipo fecha si tenemos esa info
        return True, None

    def _validate_text(
        self,
        value: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Valida texto libre"""
        # Texto libre, solo verificar que no esté vacío
        if not value.strip():
            return False, f"{param_name} no puede estar vacío"

        return True, None

    def suggest_values(
        self,
        param_type: str,
        query: str = ""
    ) -> List[str]:
        """
        Sugiere valores posibles para un parámetro

        Args:
            param_type: Tipo de parámetro
            query: Filtro de búsqueda (opcional)

        Returns:
            Lista de sugerencias
        """
        if not self.model_data:
            return []

        query_lower = query.lower()

        if param_type == 'measure':
            if hasattr(self.model_data, 'measures'):
                measures = [
                    f"[{m.get('name', m.get('Name', ''))}]"
                    for m in self.model_data.measures
                ]
                if query:
                    measures = [m for m in measures if query_lower in m.lower()]
                return sorted(measures)[:20]

        elif param_type == 'table':
            if hasattr(self.model_data, 'tables'):
                tables = [
                    t.get('name', t.get('Name', ''))
                    for t in self.model_data.tables
                ]
                if query:
                    tables = [t for t in tables if query_lower in t.lower()]
                return sorted(tables)[:20]

        elif param_type in ['column', 'date_column']:
            if hasattr(self.model_data, 'tables'):
                columns = []
                for table in self.model_data.tables:
                    table_name = table.get('name', table.get('Name', ''))
                    if 'columns' in table and table['columns']:
                        for col in table['columns']:
                            col_name = col.get('name', col.get('Name', ''))
                            full_ref = f"{table_name}[{col_name}]"
                            columns.append(full_ref)

                if query:
                    columns = [c for c in columns if query_lower in c.lower()]
                return sorted(columns)[:20]

        return []

    def get_validation_summary(
        self,
        parameters: Dict[str, Tuple[str, str]]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Valida múltiples parámetros y retorna resumen

        Args:
            parameters: Dict con {param_name: (param_value, param_type)}

        Returns:
            (all_valid, errors, warnings)
        """
        errors = []
        warnings = []

        for param_name, (param_value, param_type) in parameters.items():
            is_valid, error = self.validate_parameter(
                param_name,
                param_value,
                param_type
            )

            if not is_valid:
                errors.append(f"❌ {error}")

        all_valid = len(errors) == 0
        return all_valid, errors, warnings


def format_parameter_help(param_type: str) -> str:
    """
    Retorna ayuda sobre formato esperado de un parámetro

    Args:
        param_type: Tipo de parámetro

    Returns:
        String con ayuda formateada
    """
    help_text = {
        'measure': """
**Formato de Medida:**
- Usar corchetes: `[NombreMedida]`
- Ejemplo: `[Total Ventas]`
        """,
        'table': """
**Formato de Tabla:**
- Nombre sin corchetes: `NombreTabla`
- Ejemplo: `Ventas`
        """,
        'column': """
**Formato de Columna:**
- Tabla y columna: `Tabla[Columna]`
- Ejemplo: `Ventas[Fecha]`
        """,
        'date_column': """
**Formato de Columna de Fecha:**
- Tabla y columna: `Tabla[Columna]`
- Debe ser tipo fecha
- Ejemplo: `Calendario[Fecha]`
        """,
        'text': """
**Texto Libre:**
- Cualquier texto
- Evitar caracteres especiales si es nombre
        """
    }

    return help_text.get(param_type, "Formato no especificado")
