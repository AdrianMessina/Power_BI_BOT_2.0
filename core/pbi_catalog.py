"""
Catálogo de Power BI - Base de datos SQLite local
Almacena toda la metadata del tenant para consulta offline.
Una vez escaneado, no necesita conexión ni usuario activo.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).parent.parent / "catalog"
DB_PATH = DB_DIR / "powerbi_catalog.db"


class PBICatalog:
    """
    Catálogo local de Power BI almacenado en SQLite.
    Persiste toda la metadata del tenant para consulta offline.
    """

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            # check_same_thread=False permite usar la conexión en múltiples threads (necesario para Streamlit)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _init_db(self):
        """Crea las tablas si no existen"""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scan_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                workspace_count INTEGER DEFAULT 0,
                report_count INTEGER DEFAULT 0,
                dataset_count INTEGER DEFAULT 0,
                duration_seconds REAL DEFAULT 0,
                raw_file TEXT
            );

            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                state TEXT,
                is_on_dedicated_capacity INTEGER DEFAULT 0,
                capacity_id TEXT,
                scan_id INTEGER,
                FOREIGN KEY (scan_id) REFERENCES scan_metadata(id)
            );

            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                report_type TEXT,
                web_url TEXT,
                embed_url TEXT,
                dataset_id TEXT,
                created_date TEXT,
                modified_date TEXT,
                modified_by TEXT,
                endorsement TEXT,
                sensitivity_label TEXT,
                scan_id INTEGER,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                FOREIGN KEY (scan_id) REFERENCES scan_metadata(id)
            );

            CREATE TABLE IF NOT EXISTS report_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                user_email TEXT,
                display_name TEXT,
                principal_type TEXT,
                access_right TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            );

            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                configured_by TEXT,
                content_provider_type TEXT,
                created_date TEXT,
                is_refreshable INTEGER DEFAULT 0,
                endorsement TEXT,
                sensitivity_label TEXT,
                scan_id INTEGER,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                FOREIGN KEY (scan_id) REFERENCES scan_metadata(id)
            );

            CREATE TABLE IF NOT EXISTS dataset_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                user_email TEXT,
                display_name TEXT,
                principal_type TEXT,
                access_right TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            CREATE TABLE IF NOT EXISTS tables_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                is_hidden INTEGER DEFAULT 0,
                source_expression TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            CREATE TABLE IF NOT EXISTS columns_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                dataset_id TEXT NOT NULL,
                name TEXT NOT NULL,
                data_type TEXT,
                description TEXT,
                is_hidden INTEGER DEFAULT 0,
                expression TEXT,
                column_type TEXT,
                FOREIGN KEY (table_id) REFERENCES tables_info(id),
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            CREATE TABLE IF NOT EXISTS measures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                table_name TEXT,
                name TEXT NOT NULL,
                expression TEXT,
                description TEXT,
                data_type TEXT,
                is_hidden INTEGER DEFAULT 0,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            CREATE TABLE IF NOT EXISTS datasources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                datasource_type TEXT,
                connection_details TEXT,
                gateway_id TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            -- Índices para búsqueda rápida
            CREATE INDEX IF NOT EXISTS idx_reports_workspace ON reports(workspace_id);
            CREATE INDEX IF NOT EXISTS idx_reports_name ON reports(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_reports_dataset ON reports(dataset_id);
            CREATE INDEX IF NOT EXISTS idx_datasets_workspace ON datasets(workspace_id);
            CREATE INDEX IF NOT EXISTS idx_datasets_name ON datasets(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_tables_dataset ON tables_info(dataset_id);
            CREATE INDEX IF NOT EXISTS idx_tables_name ON tables_info(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_columns_table ON columns_info(table_id);
            CREATE INDEX IF NOT EXISTS idx_columns_name ON columns_info(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_measures_dataset ON measures(dataset_id);
            CREATE INDEX IF NOT EXISTS idx_measures_name ON measures(name COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_report_users_email ON report_users(user_email COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_dataset_users_email ON dataset_users(user_email COLLATE NOCASE);

            -- FTS (Full Text Search) para búsqueda por texto
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_reports USING fts5(
                report_id, name, description, workspace_name,
                content='', contentless_delete=1
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS fts_datasets USING fts5(
                dataset_id, name, description, configured_by, workspace_name,
                content='', contentless_delete=1
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS fts_tables USING fts5(
                table_id, dataset_id, name, description,
                content='', contentless_delete=1
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS fts_measures USING fts5(
                measure_id, dataset_id, name, expression, description,
                content='', contentless_delete=1
            );
        """)
        conn.commit()

    # ── Importar resultados del scan ───────────────────────────

    def import_scan_results(self, workspaces: List[Dict], scan_type: str = "admin",
                            raw_file: str = None, progress_callback=None) -> int:
        """
        Importa los resultados de un scan al catálogo SQLite.

        Args:
            workspaces: lista de workspaces del scan
            scan_type: "admin" o "standard"
            raw_file: path al archivo JSON raw (backup)
            progress_callback: función(message, progress) para reportar progreso

        Returns:
            ID del scan
        """
        conn = self._get_conn()
        start_time = datetime.now()
        total = len(workspaces)
        report_count = 0
        dataset_count = 0

        def _progress(msg, pct):
            if progress_callback:
                progress_callback(msg, pct)

        _progress(f"Importando {total} workspaces al catálogo...", 0.0)

        # Crear registro de scan
        cursor = conn.execute(
            "INSERT INTO scan_metadata (scan_date, scan_type, workspace_count, raw_file) VALUES (?, ?, ?, ?)",
            (start_time.isoformat(), scan_type, total, raw_file),
        )
        scan_id = cursor.lastrowid

        for idx, ws in enumerate(workspaces):
            ws_id = ws.get("id", "")
            ws_name = ws.get("name", "Sin nombre")
            _progress(f"Importando: {ws_name} ({idx+1}/{total})", (idx + 1) / total)

            # Workspace
            conn.execute(
                """INSERT OR REPLACE INTO workspaces
                   (id, name, description, type, state, is_on_dedicated_capacity, capacity_id, scan_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ws_id,
                    ws_name,
                    ws.get("description", ""),
                    ws.get("type", ""),
                    ws.get("state", ""),
                    1 if ws.get("isOnDedicatedCapacity") else 0,
                    ws.get("capacityId", ""),
                    scan_id,
                ),
            )

            # Reportes
            for report in ws.get("reports", []):
                report_id = report.get("id", "")
                r_name = report.get("name", "")
                conn.execute(
                    """INSERT OR REPLACE INTO reports
                       (id, workspace_id, name, description, report_type, web_url, embed_url,
                        dataset_id, created_date, modified_date, modified_by,
                        endorsement, sensitivity_label, scan_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        report_id, ws_id, r_name,
                        report.get("description", ""),
                        report.get("reportType", ""),
                        report.get("webUrl", ""),
                        report.get("embedUrl", ""),
                        report.get("datasetId", ""),
                        report.get("createdDateTime", ""),
                        report.get("modifiedDateTime", ""),
                        report.get("modifiedBy", ""),
                        report.get("endorsementDetails", {}).get("endorsement", "") if report.get("endorsementDetails") else "",
                        report.get("sensitivityLabel", {}).get("labelId", "") if report.get("sensitivityLabel") else "",
                        scan_id,
                    ),
                )

                # Usuarios del reporte
                for user in report.get("users", []):
                    conn.execute(
                        """INSERT INTO report_users
                           (report_id, user_email, display_name, principal_type, access_right)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            report_id,
                            user.get("emailAddress", user.get("identifier", "")),
                            user.get("displayName", ""),
                            user.get("principalType", ""),
                            user.get("reportUserAccessRight", user.get("datasetUserAccessRight", "")),
                        ),
                    )

                # FTS del reporte
                conn.execute(
                    "INSERT INTO fts_reports (report_id, name, description, workspace_name) VALUES (?, ?, ?, ?)",
                    (report_id, r_name, report.get("description", ""), ws_name),
                )
                report_count += 1

            # Datasets
            for ds in ws.get("datasets", []):
                ds_id = ds.get("id", "")
                ds_name = ds.get("name", "")
                conn.execute(
                    """INSERT OR REPLACE INTO datasets
                       (id, workspace_id, name, description, configured_by,
                        content_provider_type, created_date, is_refreshable,
                        endorsement, sensitivity_label, scan_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ds_id, ws_id, ds_name,
                        ds.get("description", ""),
                        ds.get("configuredBy", ""),
                        ds.get("ContentProviderType", ""),
                        ds.get("createdDate", ""),
                        1 if ds.get("isRefreshable") else 0,
                        ds.get("endorsementDetails", {}).get("endorsement", "") if ds.get("endorsementDetails") else "",
                        ds.get("sensitivityLabel", {}).get("labelId", "") if ds.get("sensitivityLabel") else "",
                        scan_id,
                    ),
                )

                # Usuarios del dataset
                for user in ds.get("users", []):
                    conn.execute(
                        """INSERT INTO dataset_users
                           (dataset_id, user_email, display_name, principal_type, access_right)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            ds_id,
                            user.get("emailAddress", user.get("identifier", "")),
                            user.get("displayName", ""),
                            user.get("principalType", ""),
                            user.get("datasetUserAccessRight", ""),
                        ),
                    )

                # FTS del dataset
                conn.execute(
                    "INSERT INTO fts_datasets (dataset_id, name, description, configured_by, workspace_name) VALUES (?, ?, ?, ?, ?)",
                    (ds_id, ds_name, ds.get("description", ""), ds.get("configuredBy", ""), ws_name),
                )

                # Tablas del dataset
                for table in ds.get("tables", []):
                    t_name = table.get("name", "")
                    cursor = conn.execute(
                        """INSERT INTO tables_info
                           (dataset_id, name, description, is_hidden, source_expression)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            ds_id, t_name,
                            table.get("description", ""),
                            1 if table.get("isHidden") else 0,
                            table.get("source", [{}])[0].get("expression", "") if table.get("source") else "",
                        ),
                    )
                    table_id = cursor.lastrowid

                    # FTS de tabla
                    conn.execute(
                        "INSERT INTO fts_tables (table_id, dataset_id, name, description) VALUES (?, ?, ?, ?)",
                        (str(table_id), ds_id, t_name, table.get("description", "")),
                    )

                    # Columnas
                    for col in table.get("columns", []):
                        conn.execute(
                            """INSERT INTO columns_info
                               (table_id, dataset_id, name, data_type, description,
                                is_hidden, expression, column_type)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                table_id, ds_id,
                                col.get("name", ""),
                                col.get("dataType", ""),
                                col.get("description", ""),
                                1 if col.get("isHidden") else 0,
                                col.get("expression", ""),
                                col.get("columnType", ""),
                            ),
                        )

                    # Medidas de la tabla
                    for measure in table.get("measures", []):
                        m_name = measure.get("name", "")
                        cursor2 = conn.execute(
                            """INSERT INTO measures
                               (dataset_id, table_name, name, expression, description, is_hidden)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (
                                ds_id, t_name, m_name,
                                measure.get("expression", ""),
                                measure.get("description", ""),
                                1 if measure.get("isHidden") else 0,
                            ),
                        )
                        # FTS de medida
                        conn.execute(
                            "INSERT INTO fts_measures (measure_id, dataset_id, name, expression, description) VALUES (?, ?, ?, ?, ?)",
                            (str(cursor2.lastrowid), ds_id, m_name, measure.get("expression", ""), measure.get("description", "")),
                        )

                # Datasources
                for dsrc in ds.get("datasourceUsages", ds.get("datasources", [])):
                    conn.execute(
                        """INSERT INTO datasources
                           (dataset_id, datasource_type, connection_details, gateway_id)
                           VALUES (?, ?, ?, ?)""",
                        (
                            ds_id,
                            dsrc.get("datasourceType", ""),
                            json.dumps(dsrc.get("connectionDetails", dsrc), ensure_ascii=False),
                            dsrc.get("gatewayId", ""),
                        ),
                    )

                dataset_count += 1

        # Actualizar metadata del scan
        duration = (datetime.now() - start_time).total_seconds()
        conn.execute(
            "UPDATE scan_metadata SET report_count=?, dataset_count=?, duration_seconds=? WHERE id=?",
            (report_count, dataset_count, duration, scan_id),
        )
        conn.commit()

        _progress(f"Importación completa: {report_count} reportes, {dataset_count} datasets", 1.0)
        logger.info(f"Catálogo actualizado: {report_count} reportes, {dataset_count} datasets en {duration:.1f}s")
        return scan_id

    # ── Estadísticas del catálogo ──────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas generales del catálogo"""
        conn = self._get_conn()
        stats = {}
        for table, key in [
            ("workspaces", "workspaces"),
            ("reports", "reports"),
            ("datasets", "datasets"),
            ("tables_info", "tables"),
            ("columns_info", "columns"),
            ("measures", "measures"),
            ("datasources", "datasources"),
        ]:
            row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
            stats[key] = row["cnt"]

        # Último scan
        row = conn.execute(
            "SELECT scan_date, scan_type, duration_seconds FROM scan_metadata ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            stats["last_scan_date"] = row["scan_date"]
            stats["last_scan_type"] = row["scan_type"]
            stats["last_scan_duration"] = row["duration_seconds"]

        return stats

    def get_last_scan_date(self) -> Optional[str]:
        """Retorna la fecha del último scan o None"""
        conn = self._get_conn()
        row = conn.execute("SELECT scan_date FROM scan_metadata ORDER BY id DESC LIMIT 1").fetchone()
        return row["scan_date"] if row else None

    def is_empty(self) -> bool:
        """Retorna True si el catálogo no tiene datos"""
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM workspaces").fetchone()
        return row["cnt"] == 0

    # ── Queries básicas ────────────────────────────────────────

    def get_all_workspaces(self) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT w.*,
                   COUNT(DISTINCT r.id) as report_count,
                   COUNT(DISTINCT d.id) as dataset_count
            FROM workspaces w
            LEFT JOIN reports r ON r.workspace_id = w.id
            LEFT JOIN datasets d ON d.workspace_id = w.id
            GROUP BY w.id
            ORDER BY w.name COLLATE NOCASE
        """).fetchall()
        return [dict(r) for r in rows]

    def get_all_reports(self) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT r.*, w.name as workspace_name
            FROM reports r
            JOIN workspaces w ON w.id = r.workspace_id
            ORDER BY r.name COLLATE NOCASE
        """).fetchall()
        return [dict(r) for r in rows]

    def get_report_details(self, report_id: str) -> Optional[Dict]:
        conn = self._get_conn()
        row = conn.execute("""
            SELECT r.*, w.name as workspace_name
            FROM reports r
            JOIN workspaces w ON w.id = r.workspace_id
            WHERE r.id = ?
        """, (report_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["users"] = [
            dict(u) for u in conn.execute(
                "SELECT * FROM report_users WHERE report_id = ?", (report_id,)
            ).fetchall()
        ]
        return result

    def get_dataset_details(self, dataset_id: str) -> Optional[Dict]:
        conn = self._get_conn()
        row = conn.execute("""
            SELECT d.*, w.name as workspace_name
            FROM datasets d
            JOIN workspaces w ON w.id = d.workspace_id
            WHERE d.id = ?
        """, (dataset_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["tables"] = [
            dict(t) for t in conn.execute(
                "SELECT * FROM tables_info WHERE dataset_id = ?", (dataset_id,)
            ).fetchall()
        ]
        result["measures"] = [
            dict(m) for m in conn.execute(
                "SELECT * FROM measures WHERE dataset_id = ?", (dataset_id,)
            ).fetchall()
        ]
        result["users"] = [
            dict(u) for u in conn.execute(
                "SELECT * FROM dataset_users WHERE dataset_id = ?", (dataset_id,)
            ).fetchall()
        ]
        return result

    # ── Limpiar catálogo ───────────────────────────────────────

    def clear_catalog(self):
        """Limpia todos los datos del catálogo (para re-escaneo)"""
        conn = self._get_conn()
        for table in [
            "fts_measures", "fts_tables", "fts_datasets", "fts_reports",
            "datasources", "measures", "columns_info", "tables_info",
            "dataset_users", "report_users", "datasets", "reports",
            "workspaces", "scan_metadata",
        ]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        logger.info("Catálogo limpiado completamente")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
