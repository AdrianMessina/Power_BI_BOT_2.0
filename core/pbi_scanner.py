"""
Power BI Tenant Scanner
Escanea el tenant completo usando la Scanner API (Admin REST API)
Autenticación con MSAL usando client ID público (no requiere registro de app en Azure AD)
"""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Client IDs públicos de Microsoft (no requieren registro de app)
PUBLIC_CLIENT_IDS = {
    "power_bi_powershell": "ea0616ba-638b-4df5-95eb-564f8baf79d9",
    "azure_powershell": "1950a258-227b-4e31-a9cf-717495945fc2",
}

PBI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
PBI_SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
AUTHORITY_BASE = "https://login.microsoftonline.com"


class PBIAuthenticator:
    """Maneja la autenticación con Power BI Service via MSAL"""

    def __init__(self, tenant_id: str = "organizations", client_id: str = None):
        """
        Args:
            tenant_id: ID del tenant Azure AD. Usar "organizations" para multi-tenant.
            client_id: Client ID a usar. Por defecto usa el de Power BI PowerShell.
        """
        if not MSAL_AVAILABLE:
            raise ImportError("Instalar msal: pip install msal")

        self.tenant_id = tenant_id
        self.client_id = client_id or PUBLIC_CLIENT_IDS["power_bi_powershell"]
        self.authority = f"{AUTHORITY_BASE}/{self.tenant_id}"
        self._token_cache = msal.SerializableTokenCache()
        self._cache_file = Path(__file__).parent.parent / "config" / ".token_cache.json"
        self._load_cache()

        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self._token_cache,
        )
        self._access_token = None

    def _load_cache(self):
        """Carga el cache de tokens desde disco"""
        if self._cache_file.exists():
            try:
                self._token_cache.deserialize(self._cache_file.read_text())
            except Exception:
                pass

    def _save_cache(self):
        """Guarda el cache de tokens a disco"""
        if self._token_cache.has_state_changed:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            self._cache_file.write_text(self._token_cache.serialize())

    def authenticate_interactive(self) -> bool:
        """
        Autenticación interactiva via browser popup.
        Abre el navegador para que el usuario inicie sesión.
        """
        # Intentar token silencioso primero (desde cache)
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(PBI_SCOPE, account=accounts[0])
            if result and "access_token" in result:
                self._access_token = result["access_token"]
                self._save_cache()
                logger.info("Token obtenido desde cache (silent)")
                return True

        # Login interactivo
        try:
            result = self.app.acquire_token_interactive(scopes=PBI_SCOPE)
            if "access_token" in result:
                self._access_token = result["access_token"]
                self._save_cache()
                logger.info("Autenticación interactiva exitosa")
                return True
            else:
                error = result.get("error_description", result.get("error", "Error desconocido"))
                logger.error(f"Error de autenticación: {error}")
                return False
        except Exception as e:
            logger.error(f"Error en autenticación interactiva: {e}")
            return False

    def authenticate_device_code(self, callback=None) -> bool:
        """
        Autenticación via device code flow.
        Muestra un código que el usuario ingresa en https://microsoft.com/devicelogin

        Args:
            callback: función que recibe el mensaje con el código para mostrar al usuario
        """
        # Intentar token silencioso primero
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(PBI_SCOPE, account=accounts[0])
            if result and "access_token" in result:
                self._access_token = result["access_token"]
                self._save_cache()
                logger.info("Token obtenido desde cache (silent)")
                return True

        # Device code flow
        flow = self.app.initiate_device_flow(scopes=PBI_SCOPE)
        if "user_code" not in flow:
            logger.error(f"Error iniciando device flow: {flow}")
            return False

        message = flow["message"]
        logger.info(message)
        if callback:
            callback(message)

        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            self._access_token = result["access_token"]
            self._save_cache()
            logger.info("Autenticación por device code exitosa")
            return True
        else:
            error = result.get("error_description", result.get("error", "Error desconocido"))
            logger.error(f"Error de autenticación: {error}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers HTTP con el token de autenticación"""
        if not self._access_token:
            raise RuntimeError("No autenticado. Llamar authenticate_interactive() o authenticate_device_code() primero.")
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    @property
    def is_authenticated(self) -> bool:
        return self._access_token is not None


class PBITenantScanner:
    """
    Escanea el tenant completo de Power BI usando la Scanner API.

    Workflow de la Scanner API:
    1. GET  /admin/workspaces/modified  → lista de workspace IDs
    2. POST /admin/workspaces/getInfo   → inicia scan (max 100 workspaces por llamada)
    3. GET  /admin/workspaces/scanStatus/{scanId} → esperar a que termine
    4. GET  /admin/workspaces/scanResult/{scanId} → obtener resultados
    """

    def __init__(self, auth: PBIAuthenticator):
        if not REQUESTS_AVAILABLE:
            raise ImportError("Instalar requests: pip install requests")
        self.auth = auth
        self.base_url = PBI_API_BASE
        self._scan_results = []
        self._progress_callback = None

    def set_progress_callback(self, callback):
        """
        Establece callback para reportar progreso.
        callback(message: str, progress: float)  # progress 0.0 a 1.0
        """
        self._progress_callback = callback

    def _report_progress(self, message: str, progress: float = 0.0):
        """Reporta progreso via callback y logger"""
        logger.info(f"[{progress:.0%}] {message}")
        if self._progress_callback:
            self._progress_callback(message, progress)

    def _api_get(self, endpoint: str, params: dict = None) -> Optional[Dict]:
        """GET request a la API de Power BI"""
        url = f"{self.base_url}/{endpoint}"
        try:
            resp = requests.get(url, headers=self.auth.get_headers(), params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error {resp.status_code} en GET {endpoint}: {resp.text}")
            raise
        except Exception as e:
            logger.error(f"Error en GET {endpoint}: {e}")
            raise

    def _api_post(self, endpoint: str, json_data: dict = None, params: dict = None) -> Optional[Dict]:
        """POST request a la API de Power BI"""
        url = f"{self.base_url}/{endpoint}"
        try:
            resp = requests.post(url, headers=self.auth.get_headers(), json=json_data, params=params, timeout=60)
            resp.raise_for_status()
            if resp.content:
                return resp.json()
            return {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error {resp.status_code} en POST {endpoint}: {resp.text}")
            raise
        except Exception as e:
            logger.error(f"Error en POST {endpoint}: {e}")
            raise

    # ── Paso 1: Obtener workspaces ─────────────────────────────

    def get_modified_workspaces(self, modified_since: str = None) -> List[str]:
        """
        Obtiene IDs de todos los workspaces (o solo los modificados desde una fecha).

        Args:
            modified_since: fecha ISO 8601 (ej: "2024-01-01T00:00:00Z"). None = todos.
        """
        self._report_progress("Obteniendo lista de workspaces...", 0.05)
        params = {}
        if modified_since:
            params["modifiedSince"] = modified_since

        result = self._api_get("admin/workspaces/modified", params=params)
        workspace_ids = [w["id"] for w in result] if isinstance(result, list) else []
        self._report_progress(f"Encontrados {len(workspace_ids)} workspaces", 0.10)
        return workspace_ids

    # ── Paso 2-4: Escanear workspaces ──────────────────────────

    def _start_scan(self, workspace_ids: List[str]) -> str:
        """Inicia un scan para un lote de workspaces (max 100)"""
        body = {"workspaces": workspace_ids}
        params = {
            "lineage": True,
            "datasourceDetails": True,
            "getArtifactUsers": True,
            "datasetSchema": True,
            "datasetExpressions": True,
        }
        result = self._api_post("admin/workspaces/getInfo", json_data=body, params=params)
        scan_id = result.get("id")
        logger.info(f"Scan iniciado: {scan_id} para {len(workspace_ids)} workspaces")
        return scan_id

    def _wait_for_scan(self, scan_id: str, max_wait: int = 300) -> bool:
        """Espera a que un scan termine (polling)"""
        start = time.time()
        while time.time() - start < max_wait:
            result = self._api_get(f"admin/workspaces/scanStatus/{scan_id}")
            status = result.get("status", "Unknown")
            if status == "Succeeded":
                return True
            elif status in ("Failed", "NotFound"):
                logger.error(f"Scan {scan_id} falló con status: {status}")
                return False
            time.sleep(3)
        logger.error(f"Scan {scan_id} timeout después de {max_wait}s")
        return False

    def _get_scan_result(self, scan_id: str) -> Optional[Dict]:
        """Obtiene los resultados de un scan completado"""
        return self._api_get(f"admin/workspaces/scanResult/{scan_id}")

    def scan_tenant(self, modified_since: str = None, batch_size: int = 100) -> List[Dict]:
        """
        Escanea el tenant completo.

        Args:
            modified_since: solo escanear workspaces modificados desde esta fecha
            batch_size: tamaño del lote (max 100 por API)

        Returns:
            Lista de workspaces con toda su metadata
        """
        # Paso 1: Obtener workspace IDs
        workspace_ids = self.get_modified_workspaces(modified_since)

        if not workspace_ids:
            self._report_progress("No se encontraron workspaces", 1.0)
            return []

        # Dividir en lotes de 100 (límite de la API)
        batch_size = min(batch_size, 100)
        batches = [workspace_ids[i:i + batch_size] for i in range(0, len(workspace_ids), batch_size)]
        total_batches = len(batches)

        self._report_progress(f"Escaneando {len(workspace_ids)} workspaces en {total_batches} lotes...", 0.15)

        all_workspaces = []
        for idx, batch in enumerate(batches):
            batch_num = idx + 1
            progress = 0.15 + (0.80 * batch_num / total_batches)
            self._report_progress(f"Lote {batch_num}/{total_batches}: escaneando {len(batch)} workspaces...", progress)

            try:
                # Paso 2: Iniciar scan
                scan_id = self._start_scan(batch)

                # Paso 3: Esperar resultado
                if not self._wait_for_scan(scan_id):
                    logger.warning(f"Lote {batch_num} falló, continuando con el siguiente...")
                    continue

                # Paso 4: Obtener resultado
                result = self._get_scan_result(scan_id)
                if result and "workspaces" in result:
                    all_workspaces.extend(result["workspaces"])
                    self._report_progress(
                        f"Lote {batch_num}/{total_batches} completado: {len(result['workspaces'])} workspaces",
                        progress,
                    )

                # Rate limiting: esperar entre lotes
                if batch_num < total_batches:
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error en lote {batch_num}: {e}")
                continue

        self._scan_results = all_workspaces
        self._report_progress(f"Scan completo: {len(all_workspaces)} workspaces escaneados", 1.0)
        return all_workspaces

    # ── API estándar (fallback sin admin) ──────────────────────

    def get_workspaces_standard(self) -> List[Dict]:
        """
        Obtiene workspaces usando la API estándar (no admin).
        Solo devuelve los workspaces a los que el usuario tiene acceso.
        Fallback si el usuario no tiene rol admin.
        """
        self._report_progress("Obteniendo workspaces (API estándar)...", 0.05)
        result = self._api_get("groups")
        workspaces = result.get("value", [])
        self._report_progress(f"Encontrados {len(workspaces)} workspaces accesibles", 0.10)
        return workspaces

    def get_reports_in_workspace(self, workspace_id: str) -> List[Dict]:
        """Obtiene reportes de un workspace específico"""
        result = self._api_get(f"groups/{workspace_id}/reports")
        return result.get("value", [])

    def get_datasets_in_workspace(self, workspace_id: str) -> List[Dict]:
        """Obtiene datasets de un workspace específico"""
        result = self._api_get(f"groups/{workspace_id}/datasets")
        return result.get("value", [])

    def get_dataset_tables(self, workspace_id: str, dataset_id: str) -> List[Dict]:
        """Obtiene tablas de un dataset (requiere permisos de build)"""
        try:
            # Ejecutar query DMV para obtener tablas
            body = {"queries": [{"query": "EVALUATE INFO.TABLES()"}], "serializerSettings": {"includeNulls": True}}
            result = self._api_post(f"groups/{workspace_id}/datasets/{dataset_id}/executeQueries", json_data=body)
            if result and "results" in result:
                return result["results"][0].get("tables", [])
        except Exception as e:
            logger.debug(f"No se pudo obtener tablas del dataset {dataset_id}: {e}")
        return []

    def scan_standard(self) -> List[Dict]:
        """
        Escaneo usando API estándar (sin admin).
        Más limitado pero no requiere permisos de admin.
        """
        workspaces = self.get_workspaces_standard()
        total = len(workspaces)

        for idx, ws in enumerate(workspaces):
            progress = 0.10 + (0.85 * (idx + 1) / total)
            ws_name = ws.get("name", ws.get("id", "?"))
            self._report_progress(f"Escaneando workspace: {ws_name} ({idx+1}/{total})", progress)

            ws_id = ws["id"]
            try:
                ws["reports"] = self.get_reports_in_workspace(ws_id)
                ws["datasets"] = self.get_datasets_in_workspace(ws_id)
            except Exception as e:
                logger.warning(f"Error escaneando workspace {ws_name}: {e}")
                ws["reports"] = []
                ws["datasets"] = []

            # Rate limiting
            time.sleep(0.5)

        self._report_progress(f"Scan estándar completo: {total} workspaces", 1.0)
        return workspaces

    # ── Exportar resultados ────────────────────────────────────

    def save_raw_results(self, filepath: str = None) -> str:
        """
        Guarda los resultados raw del scan en JSON.
        Útil como backup antes de procesarlos.
        """
        if not self._scan_results:
            raise ValueError("No hay resultados de scan. Ejecutar scan_tenant() primero.")

        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            filepath = str(output_dir / f"scan_raw_{timestamp}.json")

        data = {
            "scan_date": datetime.now().isoformat(),
            "workspace_count": len(self._scan_results),
            "workspaces": self._scan_results,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Resultados guardados en: {filepath}")
        return filepath
