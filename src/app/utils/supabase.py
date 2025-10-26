from __future__ import annotations

from functools import lru_cache
from typing import Any, BinaryIO

import httpx
from fastapi import HTTPException, status

from ..config import settings


class SupabaseStorageService:
    """Helper para interagir com o Supabase Storage via HTTP."""

    def __init__(
        self,
        base_url: str,
        service_role_key: str,
        bucket: str,
        public_bucket_url: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_role_key = service_role_key
        self._bucket = bucket
        self._storage_base_url = f"{self._base_url}/storage/v1"
        self._timeout = httpx.Timeout(30.0)
        if public_bucket_url:
            self._public_base_url = public_bucket_url.rstrip("/")
        else:
            self._public_base_url = (
                f"{self._storage_base_url}/object/public/{self._bucket}"
            )

    def upload_file(
        self,
        destination_path: str,
        file_data: bytes | BinaryIO,
        *,
        content_type: str | None = None,
        upsert: bool = False,
    ) -> str:
        """Envia um arquivo para o bucket e retorna o caminho armazenado."""
        path = destination_path.lstrip("/")
        payload = _ensure_bytes(file_data)
        headers = {
            **self._auth_headers(),
            "x-upsert": "true" if upsert else "false",
            "Content-Type": content_type or "application/octet-stream",
            "Accept": "application/json",
        }
        url = f"{self._storage_base_url}/object/{self._bucket}/{path}"
        response = _perform_request(
            method="POST",
            url=url,
            headers=headers,
            content=payload,
            timeout=self._timeout,
            error_message="Falha ao enviar arquivo para o Supabase.",
        )

        data = _safe_json(response)
        if isinstance(data, dict):
            stored_path = data.get("path") or data.get("Key") or data.get("key")
            if stored_path:
                return stored_path
        return path

    def delete_file(self, destination_path: str) -> None:
        path = destination_path.lstrip("/")
        url = f"{self._storage_base_url}/object/{self._bucket}"
        response = _perform_request(
            method="DELETE",
            url=url,
            headers={
                **self._auth_headers(),
                "Content-Type": "application/json",
            },
            json={"paths": [path]},
            timeout=self._timeout,
            error_message="Falha ao remover arquivo do Supabase.",
        )
        _safe_json(response)  # Consumir possível erro retornado como JSON.

    def create_signed_url(self, destination_path: str, *, expires_in_seconds: int = 3600) -> str:
        path = destination_path.lstrip("/")
        url = f"{self._storage_base_url}/object/sign/{self._bucket}/{path}"
        response = _perform_request(
            method="POST",
            url=url,
            headers={
                **self._auth_headers(),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={"expiresIn": expires_in_seconds},
            timeout=self._timeout,
            error_message="Falha ao gerar URL assinada no Supabase.",
        )
        data = _safe_json(response)
        if isinstance(data, dict):
            signed_url = data.get("signedURL") or data.get("signedUrl")
            if signed_url:
                return signed_url
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Resposta inesperada ao criar URL assinada no Supabase.",
        )

    def get_public_url(self, destination_path: str) -> str:
        """Gera a URL pública assumindo que o bucket é público."""
        return self.build_public_url(destination_path)

    def build_public_url(self, destination_path: str) -> str:
        return f"{self._public_base_url}/{destination_path.lstrip('/')}"

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._service_role_key}",
            "apikey": self._service_role_key,
        }


def _ensure_bytes(data: bytes | BinaryIO) -> bytes:
    if isinstance(data, bytes):
        return data
    if hasattr(data, "read"):
        return data.read()
    raise TypeError("O arquivo enviado deve ser bytes ou um objeto com método read().")


def _perform_request(
    *,
    method: str,
    url: str,
    timeout: httpx.Timeout,
    error_message: str,
    headers: dict[str, str] | None = None,
    content: bytes | None = None,
    json: Any = None,
) -> httpx.Response:
    try:
        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            json=json,
            timeout=timeout,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"{error_message} Detalhes: {exc}",
        ) from exc

    if not 200 <= response.status_code < 300:
        detail = _extract_error_detail(response)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"{error_message} Detalhes: {detail}",
        )
    return response


def _safe_json(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text or response.reason_phrase

    if isinstance(payload, dict):
        for key in ("message", "msg", "error", "description"):
            if key in payload and payload[key]:
                return str(payload[key])
        return str(payload)
    return str(payload)


@lru_cache
def get_supabase_storage_service() -> SupabaseStorageService:
    base_url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    bucket = settings.SUPABASE_BUCKET

    if not base_url or not key or not bucket:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e SUPABASE_BUCKET devem estar configurados.",
        )

    return SupabaseStorageService(base_url, key, bucket, settings.SUPABASE_PUBLIC_BUCKET_URL)
