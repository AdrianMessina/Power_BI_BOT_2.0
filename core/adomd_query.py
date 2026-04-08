"""
ADOMD Query Engine - Ejecuta consultas DAX y DMV contra Power BI Desktop
Usa Microsoft.PowerBI.AdomdClient.dll (incluido con Power BI Desktop)
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

ADOMD_AVAILABLE = False

try:
    import clr
    import sys
    from .pbi_detector import get_detector

    detector = get_detector()
    if detector.dll_path:
        if str(detector.dll_path) not in sys.path:
            sys.path.append(str(detector.dll_path))

        # PowerBI Desktop incluye su propio AdomdClient
        adomd_dll = detector.dll_path / "Microsoft.PowerBI.AdomdClient.dll"
        if adomd_dll.exists():
            clr.AddReference(str(adomd_dll))
            from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand
            ADOMD_AVAILABLE = True
            logger.info(f"ADOMD cargado desde: {adomd_dll}")
        else:
            logger.warning(f"AdomdClient DLL no encontrada en {detector.dll_path}")

except ImportError:
    logger.warning("pythonnet no disponible - ADOMD deshabilitado")
except Exception as e:
    logger.error(f"Error cargando ADOMD: {e}")


def find_port() -> Optional[int]:
    """Encuentra el puerto XMLA de Power BI Desktop (UTF-16-LE)"""
    ws_path = Path.home() / "AppData" / "Local" / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    if not ws_path.exists():
        return None
    for d in ws_path.iterdir():
        pf = d / "Data" / "msmdsrv.port.txt"
        if pf.exists():
            try:
                port = int(pf.read_bytes().decode('utf-16-le').strip())
                return port
            except (ValueError, UnicodeDecodeError):
                continue
    return None


class AdomdQueryEngine:
    """Motor de consultas DAX y DMV via ADOMD.NET"""

    def __init__(self, port: Optional[int] = None):
        self._conn = None
        self._port = port
        self._connected = False

    def connect(self, port: Optional[int] = None) -> bool:
        if not ADOMD_AVAILABLE:
            logger.error("ADOMD no disponible")
            return False

        p = port or self._port or find_port()
        if not p:
            logger.error("No se encontro puerto XMLA")
            return False

        try:
            self._port = p
            self._conn = AdomdConnection()
            self._conn.ConnectionString = f"Data Source=localhost:{p}"
            self._conn.Open()
            self._connected = True
            logger.info(f"ADOMD conectado al puerto {p}")
            return True
        except Exception as e:
            logger.error(f"Error conectando ADOMD: {e}")
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _execute(self, query: str) -> List[Dict[str, Any]]:
        """Ejecuta query y retorna lista de dicts con nombres de columna"""
        if not self._connected:
            return []
        try:
            cmd = self._conn.CreateCommand()
            cmd.CommandText = query
            reader = cmd.ExecuteReader()

            cols = [reader.GetName(i) for i in range(reader.FieldCount)]
            rows = []
            while reader.Read():
                row = {}
                for i, col in enumerate(cols):
                    val = reader.GetValue(i)
                    row[col] = val if val is not None else None
                rows.append(row)
            reader.Close()
            return rows
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            return []

    # ── DMV Queries (metadata rica) ──

    def dmv_tables(self) -> List[Dict]:
        """Todas las tablas con metadata completa"""
        return self._execute(
            "SELECT [ID], [Name], [IsHidden], [Description], [DataCategory] "
            "FROM $SYSTEM.TMSCHEMA_TABLES ORDER BY [Name]"
        )

    def dmv_measures(self) -> List[Dict]:
        """Todas las medidas con expresion, formato, display folder"""
        return self._execute(
            "SELECT [Name], [TableID], [Expression], [FormatString], "
            "[DisplayFolder], [Description], [IsHidden], [DataType] "
            "FROM $SYSTEM.TMSCHEMA_MEASURES ORDER BY [Name]"
        )

    def dmv_columns(self, table_id: Optional[int] = None) -> List[Dict]:
        """Columnas con tipo, formato, display folder"""
        q = ("SELECT [Name], [TableID], [ExplicitDataType], [IsHidden], "
             "[Type], [FormatString], [DisplayFolder], [Description], "
             "[SummarizeBy], [SortByColumnID], [Expression] "
             "FROM $SYSTEM.TMSCHEMA_COLUMNS")
        if table_id is not None:
            q += f" WHERE [TableID] = {table_id}"
        q += " ORDER BY [Name]"
        return self._execute(q)

    def dmv_relationships(self) -> List[Dict]:
        """Relaciones con cardinalidad y filtro cruzado"""
        return self._execute(
            "SELECT [ID], [Name], [FromTableID], [FromColumnID], "
            "[ToTableID], [ToColumnID], [IsActive], [CrossFilteringBehavior], "
            "[FromCardinality], [ToCardinality] "
            "FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS"
        )

    def dmv_partitions(self) -> List[Dict]:
        """Particiones (fuentes de datos)"""
        return self._execute(
            "SELECT [Name], [TableID], [SourceType], [Mode], [RefreshedTime] "
            "FROM $SYSTEM.TMSCHEMA_PARTITIONS"
        )

    def dmv_hierarchies(self) -> List[Dict]:
        """Jerarquias"""
        return self._execute(
            "SELECT [Name], [TableID], [IsHidden], [Description] "
            "FROM $SYSTEM.TMSCHEMA_HIERARCHIES"
        )

    def dmv_roles(self) -> List[Dict]:
        """Roles de seguridad"""
        return self._execute(
            "SELECT [Name], [ModelPermission], [Description] "
            "FROM $SYSTEM.TMSCHEMA_ROLES"
        )

    def dmv_expressions(self) -> List[Dict]:
        """Expresiones Power Query / M compartidas"""
        return self._execute(
            "SELECT [Name], [Kind], [Expression], [Description] "
            "FROM $SYSTEM.TMSCHEMA_EXPRESSIONS"
        )

    # ── Funciones de alto nivel ──

    def get_full_model_metadata(self) -> Dict[str, Any]:
        """Retorna metadata completa del modelo via DMVs"""
        tables = self.dmv_tables()
        measures = self.dmv_measures()
        columns_raw = self.dmv_columns()
        rels = self.dmv_relationships()

        # Crear lookup de tabla ID -> nombre
        table_map = {t.get('ID'): t.get('Name', '') for t in tables}

        # Enriquecer medidas con nombre de tabla
        for m in measures:
            tid = m.get('TableID')
            m['TableName'] = table_map.get(tid, f'Table_{tid}')

        # Enriquecer columnas
        for c in columns_raw:
            tid = c.get('TableID')
            c['TableName'] = table_map.get(tid, f'Table_{tid}')

        # Agrupar columnas por tabla
        columns_by_table = {}
        for c in columns_raw:
            tname = c['TableName']
            if tname not in columns_by_table:
                columns_by_table[tname] = []
            columns_by_table[tname].append(c)

        # Enriquecer relaciones
        col_map = {}
        for c in columns_raw:
            col_map[c.get('ID', c.get('Name', ''))] = c

        return {
            'tables': tables,
            'measures': measures,
            'columns': columns_raw,
            'columns_by_table': columns_by_table,
            'relationships': rels,
            'table_map': table_map,
            'stats': {
                'tables_count': len(tables),
                'measures_count': len(measures),
                'columns_count': len(columns_raw),
                'relationships_count': len(rels),
                'hidden_tables': sum(1 for t in tables if t.get('IsHidden')),
            }
        }

    # ── DAX Query Execution ──

    def execute_dax(self, dax: str) -> List[Dict[str, Any]]:
        """Ejecuta una consulta DAX (EVALUATE ...) y retorna resultados"""
        if not dax.strip().upper().startswith('EVALUATE'):
            # Intentar envolver en EVALUATE si no lo tiene
            if not dax.strip().upper().startswith('DEFINE'):
                dax = f"EVALUATE {dax}"
        return self._execute(dax)

    def evaluate_measure(self, expression: str) -> Any:
        """Evalua una expresion DAX escalar via ROW"""
        rows = self._execute(f'EVALUATE ROW("Result", {expression})')
        if rows:
            return rows[0].get('[Result]', rows[0].get('Result', None))
        return None

    def get_table_preview(self, table_name: str, top_n: int = 5) -> List[Dict]:
        """Preview de datos de una tabla"""
        return self._execute(f"EVALUATE TOPN({top_n}, '{table_name}')")

    def disconnect(self):
        if self._conn and self._connected:
            try:
                self._conn.Close()
                self._connected = False
            except Exception:
                pass
