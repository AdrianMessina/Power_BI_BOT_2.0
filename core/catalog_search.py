"""
Buscador inteligente del catálogo de Power BI
Permite buscar reportes, datasets, tablas, medidas, dueños, etc.
Funciona 100% offline sobre el catálogo SQLite local.
"""

import sqlite3
import re
import logging
from typing import Dict, List, Optional, Any
from .pbi_catalog import PBICatalog

logger = logging.getLogger(__name__)


class CatalogSearch:
    """
    Motor de búsqueda sobre el catálogo de Power BI.

    Soporta:
    - Búsqueda por texto libre (FTS5)
    - Búsqueda por dueño/usuario
    - Búsqueda por workspace
    - Búsqueda por tabla/columna
    - Búsqueda por data source
    - Detección automática de intención
    """

    def __init__(self, catalog: PBICatalog):
        self.catalog = catalog
        self._conn = catalog._get_conn()

    # ── Detección de intención ─────────────────────────────────

    def detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detecta la intención del usuario a partir de su pregunta.

        Returns:
            {
                "intent": str,       # tipo de búsqueda
                "search_term": str,  # término de búsqueda extraído
                "original": str      # query original
            }
        """
        q = query.lower().strip()

        # Patrones de intención
        patterns = {
            "owner": [
                r"(?:quién|quien|de quién|de quien|dueño|owner|responsable|creador).*?(?:es|del|de|reporte|tablero|dashboard|report)",
                r"(?:reporte|tablero|dashboard|report).*?(?:de quién|de quien|dueño|owner)",
                r"(?:quién|quien) (?:hizo|creó|creo|mantiene|administra)",
            ],
            "search_by_owner": [
                r"(?:reportes?|tableros?|dashboards?).*?(?:de|del|por)\s+(\w[\w\s]*?)(?:\?|$)",
                r"(?:qué|que|cuáles|cuales).*?(?:tiene|maneja|administra)\s+(\w[\w\s]*?)(?:\?|$)",
            ],
            "search_by_table": [
                r"(?:qué|que|cuáles|cuales|hay).*?(?:tableros?|reportes?|dashboards?).*?(?:usan?|tienen?|con).*?(?:tabla|datos de|data de)\s+(\w[\w\s]*)",
                r"(?:tabla|datos de|data de)\s+(\w[\w\s]*?).*?(?:en qué|en que|cuáles|cuales)",
                r"(?:quién|quien|qué|que).*?(?:usa|utiliza|tiene).*?(?:tabla)\s+(\w[\w\s]*)",
            ],
            "search_reports": [
                r"(?:hay|existe|busca|buscar|encontrar|listar?).*?(?:tablero|reporte|dashboard|report).*?(?:de|con|sobre|para)\s+([\w\s]+)",
                r"(?:tablero|reporte|dashboard|report).*?(?:de|con|sobre|para)\s+([\w\s]+)",
                r"(?:hay|existe).*?([\w\s]+?)(?:\?|$)",
            ],
            "count_reports": [
                r"(?:cuántos|cuantos|cantidad|total).*?(?:reportes?|tableros?|dashboards?)",
            ],
            "list_workspaces": [
                r"(?:listar?|mostrar?|ver|cuáles|cuales).*?(?:workspaces?|espacios?|áreas?)",
            ],
            "list_reports_in_workspace": [
                r"(?:reportes?|tableros?|dashboards?).*?(?:en|del|de).*?(?:workspace|espacio)\s+([\w\s]+)",
                r"(?:workspace|espacio)\s+([\w\s]+?).*?(?:reportes?|tableros?|dashboards?)",
            ],
            "search_measure": [
                r"(?:medida|measure|dax).*?([\w\s]+)",
                r"(?:quién|quien|qué|que).*?(?:medida|measure).*?([\w\s]+)",
            ],
            "search_datasource": [
                r"(?:qué|que|cuáles|cuales).*?(?:se conecta|conectan|usan?|fuente|source|origen).*?([\w\s.]+)",
                r"(?:servidor|server|base de datos|database)\s+([\w\s.]+)",
            ],
        }

        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, q)
                if match:
                    search_term = match.group(1).strip() if match.lastindex else ""
                    # Limpiar el término
                    search_term = re.sub(r'\?$', '', search_term).strip()
                    return {
                        "intent": intent,
                        "search_term": search_term,
                        "original": query,
                    }

        # Fallback: búsqueda general
        # Extraer el término más relevante (quitar palabras comunes)
        stopwords = {
            "hay", "existe", "tiene", "tengo", "algún", "algun", "alguna", "alguno",
            "qué", "que", "cuál", "cual", "cuáles", "cuales", "cómo", "como",
            "dónde", "donde", "quién", "quien", "para", "por", "con", "sin",
            "los", "las", "del", "de", "el", "la", "un", "una", "unos",
            "y", "o", "en", "es", "son", "me", "te", "se", "nos",
            "puedes", "puede", "puedo", "decir", "mostrar", "ver", "buscar",
            "reporte", "tablero", "dashboard", "report", "datos",
        }
        words = [w for w in re.findall(r'\w+', q) if w not in stopwords and len(w) > 2]
        search_term = " ".join(words) if words else q

        return {
            "intent": "general_search",
            "search_term": search_term,
            "original": query,
        }

    # ── Búsqueda principal ─────────────────────────────────────

    def search(self, query: str) -> Dict[str, Any]:
        """
        Búsqueda inteligente: detecta intención y ejecuta la consulta apropiada.

        Returns:
            {
                "intent": str,
                "query": str,
                "results": list,
                "summary": str,
                "count": int
            }
        """
        intent_info = self.detect_intent(query)
        intent = intent_info["intent"]
        term = intent_info["search_term"]

        handler = {
            "owner": self._search_owner,
            "search_by_owner": self._search_by_owner,
            "search_by_table": self._search_by_table,
            "search_reports": self._search_reports_by_keyword,
            "count_reports": self._count_reports,
            "list_workspaces": self._list_workspaces,
            "list_reports_in_workspace": self._search_reports_in_workspace,
            "search_measure": self._search_measures,
            "search_datasource": self._search_datasources,
            "general_search": self._general_search,
        }.get(intent, self._general_search)

        results = handler(term, query)
        return {
            "intent": intent,
            "query": query,
            "search_term": term,
            **results,
        }

    # ── Handlers de búsqueda ───────────────────────────────────

    def _search_reports_by_keyword(self, term: str, original: str = "") -> Dict:
        """Busca reportes por keyword en nombre, descripción, o tablas"""
        results = []

        # 1. Buscar en FTS de reportes
        fts_results = self._fts_search("fts_reports", term)
        report_ids_from_fts = {r["report_id"] for r in fts_results}

        # 2. Buscar también en tablas (por si el usuario busca por datos)
        table_matches = self._conn.execute("""
            SELECT DISTINCT t.dataset_id, t.name as table_name
            FROM tables_info t
            WHERE t.name LIKE ? COLLATE NOCASE
        """, (f"%{term}%",)).fetchall()

        # Obtener reportes que usan esos datasets
        dataset_ids_from_tables = {t["dataset_id"] for t in table_matches}
        if dataset_ids_from_tables:
            placeholders = ",".join("?" * len(dataset_ids_from_tables))
            extra_reports = self._conn.execute(f"""
                SELECT DISTINCT id FROM reports WHERE dataset_id IN ({placeholders})
            """, list(dataset_ids_from_tables)).fetchall()
            report_ids_from_fts.update(r["id"] for r in extra_reports)

        # 3. Buscar por nombre directo (LIKE) como fallback
        like_results = self._conn.execute("""
            SELECT DISTINCT id FROM reports WHERE name LIKE ? COLLATE NOCASE
        """, (f"%{term}%",)).fetchall()
        report_ids_from_fts.update(r["id"] for r in like_results)

        # Obtener detalles de cada reporte encontrado
        for rid in report_ids_from_fts:
            detail = self._get_report_summary(rid)
            if detail:
                results.append(detail)

        # Ordenar por relevancia (nombre exacto primero)
        term_lower = term.lower()
        results.sort(key=lambda r: (0 if term_lower in r["name"].lower() else 1, r["name"].lower()))

        summary = self._build_reports_summary(results, term)
        return {"results": results, "summary": summary, "count": len(results)}

    def _search_by_owner(self, owner_name: str, original: str = "") -> Dict:
        """Busca reportes de un dueño/usuario específico"""
        results = []

        # Buscar en datasets (configured_by)
        datasets = self._conn.execute("""
            SELECT DISTINCT d.id as dataset_id
            FROM datasets d
            WHERE d.configured_by LIKE ? COLLATE NOCASE
        """, (f"%{owner_name}%",)).fetchall()

        dataset_ids = {d["dataset_id"] for d in datasets}

        # Reportes de esos datasets
        if dataset_ids:
            placeholders = ",".join("?" * len(dataset_ids))
            reports = self._conn.execute(f"""
                SELECT DISTINCT id FROM reports WHERE dataset_id IN ({placeholders})
            """, list(dataset_ids)).fetchall()
            for r in reports:
                detail = self._get_report_summary(r["id"])
                if detail:
                    results.append(detail)

        # También buscar en report_users y dataset_users
        extra_reports = self._conn.execute("""
            SELECT DISTINCT ru.report_id as id
            FROM report_users ru
            WHERE ru.display_name LIKE ? COLLATE NOCASE
               OR ru.user_email LIKE ? COLLATE NOCASE
        """, (f"%{owner_name}%", f"%{owner_name}%")).fetchall()

        existing_ids = {r["id"] for r in results}
        for r in extra_reports:
            if r["id"] not in existing_ids:
                detail = self._get_report_summary(r["id"])
                if detail:
                    results.append(detail)

        summary = self._build_owner_summary(results, owner_name)
        return {"results": results, "summary": summary, "count": len(results)}

    def _search_owner(self, term: str, original: str = "") -> Dict:
        """Busca quién es el dueño de un reporte específico"""
        # Extraer nombre del reporte del query original
        q = original.lower()
        # Intentar extraer el nombre del reporte
        for pattern in [
            r"(?:reporte|tablero|dashboard|report)\s+[\"']?(.+?)[\"']?\s*\??\s*$",
            r"(?:del|de)\s+[\"']?(.+?)[\"']?\s*\??\s*$",
        ]:
            match = re.search(pattern, q)
            if match:
                term = match.group(1).strip()
                break

        reports = self._conn.execute("""
            SELECT r.id, r.name, r.modified_by, d.configured_by, w.name as workspace_name
            FROM reports r
            JOIN workspaces w ON w.id = r.workspace_id
            LEFT JOIN datasets d ON d.id = r.dataset_id
            WHERE r.name LIKE ? COLLATE NOCASE
        """, (f"%{term}%",)).fetchall()

        results = []
        for r in reports:
            users = self._conn.execute("""
                SELECT display_name, user_email, access_right
                FROM report_users WHERE report_id = ?
            """, (r["id"],)).fetchall()

            results.append({
                "id": r["id"],
                "name": r["name"],
                "workspace": r["workspace_name"],
                "configured_by": r["configured_by"] or "No disponible",
                "modified_by": r["modified_by"] or "No disponible",
                "users": [dict(u) for u in users],
            })

        if results:
            parts = []
            for r in results:
                owner = r["configured_by"] or r["modified_by"] or "No disponible"
                users_str = ""
                if r["users"]:
                    user_names = [u["display_name"] or u["user_email"] for u in r["users"] if u["display_name"] or u["user_email"]]
                    if user_names:
                        users_str = f"\n   Usuarios con acceso: {', '.join(user_names[:5])}"
                        if len(user_names) > 5:
                            users_str += f" (+{len(user_names)-5} más)"
                parts.append(
                    f"**{r['name']}** (Workspace: {r['workspace']})\n"
                    f"   Dueño/Creador: {owner}{users_str}"
                )
            summary = f"Encontré {len(results)} reporte(s) que coinciden con '{term}':\n\n" + "\n\n".join(parts)
        else:
            summary = f"No encontré reportes que coincidan con '{term}'."

        return {"results": results, "summary": summary, "count": len(results)}

    def _search_by_table(self, table_name: str, original: str = "") -> Dict:
        """Busca reportes que usen una tabla específica"""
        # Encontrar datasets que tienen esa tabla
        tables = self._conn.execute("""
            SELECT t.dataset_id, t.name as table_name, d.name as dataset_name
            FROM tables_info t
            JOIN datasets d ON d.id = t.dataset_id
            WHERE t.name LIKE ? COLLATE NOCASE
        """, (f"%{table_name}%",)).fetchall()

        dataset_ids = {t["dataset_id"] for t in tables}
        results = []

        if dataset_ids:
            placeholders = ",".join("?" * len(dataset_ids))
            reports = self._conn.execute(f"""
                SELECT DISTINCT r.id
                FROM reports r
                WHERE r.dataset_id IN ({placeholders})
            """, list(dataset_ids)).fetchall()

            for r in reports:
                detail = self._get_report_summary(r["id"])
                if detail:
                    # Agregar las tablas que matchearon
                    matching_tables = [t["table_name"] for t in tables if t["dataset_id"] == detail.get("dataset_id")]
                    detail["matching_tables"] = matching_tables
                    results.append(detail)

        if results:
            parts = []
            for r in results:
                tables_str = ", ".join(r.get("matching_tables", []))
                parts.append(
                    f"**{r['name']}** (Workspace: {r['workspace']})\n"
                    f"   Dueño: {r.get('owner', 'N/A')} | Tablas: {tables_str}"
                )
            summary = (
                f"Encontré {len(results)} reporte(s) que usan datos de '{table_name}':\n\n"
                + "\n\n".join(parts)
            )
        else:
            summary = f"No encontré reportes que usen una tabla llamada '{table_name}'."

        return {"results": results, "summary": summary, "count": len(results)}

    def _count_reports(self, term: str = "", original: str = "") -> Dict:
        """Cuenta reportes, opcionalmente filtrados"""
        if term:
            row = self._conn.execute(
                "SELECT COUNT(*) as cnt FROM reports WHERE name LIKE ? COLLATE NOCASE",
                (f"%{term}%",),
            ).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) as cnt FROM reports").fetchone()

        count = row["cnt"]
        stats = self.catalog.get_stats()

        summary = (
            f"El catálogo tiene **{stats['reports']} reportes** en "
            f"**{stats['workspaces']} workspaces**, con "
            f"**{stats['datasets']} datasets**, "
            f"**{stats['tables']} tablas** y "
            f"**{stats['measures']} medidas DAX**."
        )

        return {"results": [stats], "summary": summary, "count": count}

    def _list_workspaces(self, term: str = "", original: str = "") -> Dict:
        """Lista todos los workspaces"""
        workspaces = self.catalog.get_all_workspaces()
        parts = []
        for ws in workspaces:
            parts.append(
                f"- **{ws['name']}**: {ws['report_count']} reportes, {ws['dataset_count']} datasets"
            )

        summary = f"Hay **{len(workspaces)} workspaces** en el catálogo:\n\n" + "\n".join(parts)
        return {"results": workspaces, "summary": summary, "count": len(workspaces)}

    def _search_reports_in_workspace(self, ws_name: str, original: str = "") -> Dict:
        """Lista reportes de un workspace específico"""
        reports = self._conn.execute("""
            SELECT r.id, r.name, d.configured_by as owner, w.name as workspace_name
            FROM reports r
            JOIN workspaces w ON w.id = r.workspace_id
            LEFT JOIN datasets d ON d.id = r.dataset_id
            WHERE w.name LIKE ? COLLATE NOCASE
            ORDER BY r.name COLLATE NOCASE
        """, (f"%{ws_name}%",)).fetchall()

        results = [dict(r) for r in reports]

        if results:
            ws_actual = results[0]["workspace_name"]
            parts = [f"- **{r['name']}** (Dueño: {r['owner'] or 'N/A'})" for r in results]
            summary = (
                f"El workspace **{ws_actual}** tiene **{len(results)} reportes**:\n\n"
                + "\n".join(parts)
            )
        else:
            summary = f"No encontré workspaces que coincidan con '{ws_name}'."

        return {"results": results, "summary": summary, "count": len(results)}

    def _search_measures(self, term: str, original: str = "") -> Dict:
        """Busca medidas DAX por nombre o expresión"""
        measures = self._conn.execute("""
            SELECT m.name, m.expression, m.table_name, m.dataset_id,
                   d.name as dataset_name, w.name as workspace_name
            FROM measures m
            JOIN datasets d ON d.id = m.dataset_id
            JOIN workspaces w ON w.id = d.workspace_id
            WHERE m.name LIKE ? COLLATE NOCASE
               OR m.expression LIKE ? COLLATE NOCASE
            LIMIT 20
        """, (f"%{term}%", f"%{term}%")).fetchall()

        results = [dict(m) for m in measures]

        if results:
            parts = []
            for m in results:
                expr = (m["expression"] or "")[:100]
                if len(m["expression"] or "") > 100:
                    expr += "..."
                parts.append(
                    f"- **{m['name']}** ({m['dataset_name']} / {m['workspace_name']})\n"
                    f"  `{expr}`"
                )
            summary = f"Encontré {len(results)} medida(s) que coinciden con '{term}':\n\n" + "\n\n".join(parts)
        else:
            summary = f"No encontré medidas que coincidan con '{term}'."

        return {"results": results, "summary": summary, "count": len(results)}

    def _search_datasources(self, term: str, original: str = "") -> Dict:
        """Busca por data source (servidor, base de datos, etc.)"""
        sources = self._conn.execute("""
            SELECT ds.datasource_type, ds.connection_details, ds.dataset_id,
                   d.name as dataset_name, w.name as workspace_name
            FROM datasources ds
            JOIN datasets d ON d.id = ds.dataset_id
            JOIN workspaces w ON w.id = d.workspace_id
            WHERE ds.connection_details LIKE ? COLLATE NOCASE
               OR ds.datasource_type LIKE ? COLLATE NOCASE
        """, (f"%{term}%", f"%{term}%")).fetchall()

        results = [dict(s) for s in sources]

        if results:
            parts = []
            for s in results:
                parts.append(
                    f"- **{s['dataset_name']}** ({s['workspace_name']})\n"
                    f"  Tipo: {s['datasource_type']} | Conexión: {s['connection_details'][:100]}"
                )
            summary = f"Encontré {len(results)} data source(s) que coinciden con '{term}':\n\n" + "\n\n".join(parts)
        else:
            summary = f"No encontré data sources que coincidan con '{term}'."

        return {"results": results, "summary": summary, "count": len(results)}

    def _general_search(self, term: str, original: str = "") -> Dict:
        """Búsqueda general en todo el catálogo"""
        all_results = []

        # Buscar en reportes
        reports = self._search_reports_by_keyword(term)
        if reports["count"] > 0:
            all_results.extend(reports["results"])

        # Buscar en tablas
        tables_search = self._search_by_table(term)
        # Agregar resultados que no estén ya
        existing_ids = {r.get("id") for r in all_results}
        for r in tables_search["results"]:
            if r.get("id") not in existing_ids:
                all_results.append(r)

        # Buscar en medidas
        measures = self._search_measures(term)

        parts = []
        if all_results:
            parts.append(f"**Reportes encontrados ({len(all_results)}):**")
            for r in all_results[:10]:
                parts.append(f"- {r['name']} (Workspace: {r.get('workspace', 'N/A')}, Dueño: {r.get('owner', 'N/A')})")

        if measures["count"] > 0:
            parts.append(f"\n**Medidas DAX encontradas ({measures['count']}):**")
            for m in measures["results"][:5]:
                parts.append(f"- {m['name']} ({m.get('dataset_name', 'N/A')})")

        if not parts:
            summary = f"No encontré resultados para '{term}'. Intentá con otros términos."
        else:
            summary = f"Resultados para '{term}':\n\n" + "\n".join(parts)

        return {
            "results": all_results,
            "measures": measures["results"] if measures["count"] > 0 else [],
            "summary": summary,
            "count": len(all_results) + measures["count"],
        }

    # ── Helpers ────────────────────────────────────────────────

    def _fts_search(self, table: str, term: str) -> List[Dict]:
        """Ejecuta búsqueda FTS5"""
        try:
            # Escapar caracteres especiales de FTS5
            safe_term = re.sub(r'[^\w\s]', '', term)
            if not safe_term.strip():
                return []
            # Buscar con match (OR entre palabras)
            query_term = " OR ".join(safe_term.split())
            rows = self._conn.execute(
                f"SELECT * FROM {table} WHERE {table} MATCH ? LIMIT 50",
                (query_term,),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.debug(f"FTS search error en {table}: {e}")
            return []

    def _get_report_summary(self, report_id: str) -> Optional[Dict]:
        """Obtiene resumen de un reporte para mostrar en resultados"""
        row = self._conn.execute("""
            SELECT r.id, r.name, r.web_url, r.dataset_id, r.modified_by,
                   w.name as workspace, d.configured_by as owner, d.name as dataset_name
            FROM reports r
            JOIN workspaces w ON w.id = r.workspace_id
            LEFT JOIN datasets d ON d.id = r.dataset_id
            WHERE r.id = ?
        """, (report_id,)).fetchone()

        if not row:
            return None

        result = dict(row)
        result["owner"] = result.get("owner") or result.get("modified_by") or "No disponible"
        return result

    def _build_reports_summary(self, results: List[Dict], term: str) -> str:
        if not results:
            return f"No encontré reportes relacionados con '{term}'."

        parts = []
        for i, r in enumerate(results[:15], 1):
            parts.append(
                f"{i}. **{r['name']}** - Workspace: {r.get('workspace', 'N/A')}\n"
                f"   Dueño: {r.get('owner', 'N/A')} | Dataset: {r.get('dataset_name', 'N/A')}"
            )

        summary = f"Encontré **{len(results)} reporte(s)** relacionados con '{term}':\n\n" + "\n\n".join(parts)
        if len(results) > 15:
            summary += f"\n\n... y {len(results) - 15} más."
        return summary

    def _build_owner_summary(self, results: List[Dict], owner: str) -> str:
        if not results:
            return f"No encontré reportes de '{owner}'."

        parts = []
        for i, r in enumerate(results[:15], 1):
            parts.append(f"{i}. **{r['name']}** - Workspace: {r.get('workspace', 'N/A')}")

        summary = f"**{owner}** tiene **{len(results)} reporte(s)**:\n\n" + "\n\n".join(parts)
        if len(results) > 15:
            summary += f"\n\n... y {len(results) - 15} más."
        return summary
