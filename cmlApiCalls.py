"""Small, Python 3 client for the CML2 REST API.

Credentials are deliberately supplied by the caller (or environment), never
read from a file by this module.  The ``CML`` class is retained for callers of
the original script.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class CMLApiError(RuntimeError):
    """Raised when CML2 returns an error or an invalid response."""


@dataclass
class CMLClient:
    server: str
    token: str
    verify_tls: bool = True
    timeout: float = 20.0

    def __post_init__(self) -> None:
        self.base_url = self.server.rstrip("/")
        if not self.base_url.startswith(("https://", "http://")):
            self.base_url = f"https://{self.base_url}"

    @classmethod
    def authenticate(
        cls,
        server: str,
        username: str,
        password: str,
        *,
        verify_tls: bool = True,
        timeout: float = 20.0,
    ) -> "CMLClient":
        base_url = server.rstrip("/")
        if not base_url.startswith(("https://", "http://")):
            base_url = f"https://{base_url}"
        try:
            response = requests.post(
                f"{base_url}/api/v0/authenticate",
                json={"username": username, "password": password},
                headers={"Accept": "application/json"},
                verify=verify_tls,
                timeout=timeout,
            )
            response.raise_for_status()
            token = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise CMLApiError(f"CML2 authentication failed: {exc}") from exc
        if not isinstance(token, str) or not token:
            raise CMLApiError("CML2 authentication returned no access token")
        return cls(base_url, f"Bearer {token}", verify_tls, timeout)

    def get(self, path: str) -> Any:
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers={"Accept": "application/json", "Authorization": self.token},
                verify=self.verify_tls,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise CMLApiError(f"CML2 request {path} failed: {exc}") from exc

    def get_lab_info(self, lab: str) -> dict[str, Any]:
        result = self.get(f"/api/v0/labs/{lab}/?simplified=true")
        if not isinstance(result, dict):
            raise CMLApiError("CML2 returned an invalid lab response")
        return result

    def get_node(self, lab: str, node_id: str) -> dict[str, Any]:
        result = self.get(f"/api/v0/labs/{lab}/nodes/{node_id}?simplified=true")
        if not isinstance(result, dict):
            raise CMLApiError("CML2 returned an invalid node response")
        return result

    def get_nodes(self, lab: str) -> list[str]:
        result = self.get(f"/api/v0/labs/{lab}/nodes/?simplified=true")
        if not isinstance(result, list):
            raise CMLApiError("CML2 returned an invalid node list")
        return result


class CML:
    """Backward-compatible facade used by older automation."""

    @staticmethod
    def auth(server: str, username: str, password: str) -> str:
        return CMLClient.authenticate(server, username, password, verify_tls=False).token

    @staticmethod
    def _client(auth: str, server: str) -> CMLClient:
        return CMLClient(server, auth, verify_tls=False)

    @staticmethod
    def getLabInfo(auth: str, server: str, lab: str) -> dict[str, Any]:
        return CML._client(auth, server).get_lab_info(lab)

    @staticmethod
    def getNodesByID(auth: str, server: str, lab: str, node_id: str) -> dict[str, Any]:
        return CML._client(auth, server).get_node(lab, node_id)

    @staticmethod
    def getAllNodes(auth: str, server: str, lab: str) -> list[str]:
        return CML._client(auth, server).get_nodes(lab)
