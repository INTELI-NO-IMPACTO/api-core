from __future__ import annotations

from functools import lru_cache
from typing import Any, BinaryIO

from fastapi import HTTPException, status
from supabase import Client, create_client

from ..config import settings


class SupabaseStorageService:
    """High-level helper to interact with a single Supabase Storage bucket."""

    def __init__(self, client: Client, bucket: str, public_bucket_url: str | None = None) -> None:
        self._client = client
        self._bucket = client.storage.from_(bucket)
        if public_bucket_url:
            self._public_base_url = public_bucket_url.rstrip("/")
        else:
            base_url = settings.SUPABASE_URL
            if not base_url:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "SUPABASE_URL deve estar configurada.",
                )
            self._public_base_url = (
                f"{base_url.rstrip('/')}/storage/v1/object/public/{bucket}"
            )

    def upload_file(
        self,
        destination_path: str,
        file_data: bytes | BinaryIO,
        *,
        content_type: str | None = None,
        upsert: bool = False,
    ) -> str:
        """Uploads file data to the configured bucket and returns the file path."""
        options: dict[str, Any] = {"upsert": upsert}
        if content_type:
            options["content-type"] = content_type

        response = self._bucket.upload(destination_path.lstrip("/"), file_data, file_options=options)
        _ensure_response_ok(response, "Falha ao enviar arquivo para o Supabase.")
        return destination_path.lstrip("/")

    def delete_file(self, destination_path: str) -> None:
        response = self._bucket.remove([destination_path.lstrip("/")])
        _ensure_response_ok(response, "Falha ao remover arquivo do Supabase.")

    def create_signed_url(self, destination_path: str, *, expires_in_seconds: int = 3600) -> str:
        response = self._bucket.create_signed_url(
            destination_path.lstrip("/"), expires_in_seconds
        )
        data = _ensure_response_ok(response, "Falha ao gerar URL assinada.")
        try:
            return data["signedURL"] if "signedURL" in data else data["signedUrl"]
        except (KeyError, TypeError) as exc:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Resposta inesperada ao criar URL assinada no Supabase.",
            ) from exc

    def get_public_url(self, destination_path: str) -> str:
        response = self._bucket.get_public_url(destination_path.lstrip("/"))
        data = _ensure_response_ok(response, "Falha ao recuperar URL pública.")
        try:
            return data["publicUrl"]
        except (KeyError, TypeError) as exc:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Resposta inesperada ao recuperar URL pública no Supabase.",
            ) from exc

    def build_public_url(self, destination_path: str) -> str:
        """Builds the public URL when the bucket is `public`."""
        return f"{self._public_base_url}/{destination_path.lstrip('/')}"


def _ensure_response_ok(response: Any, error_message: str) -> Any:
    """Normalizes Supabase responses and raises HTTP errors when needed."""
    if response is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, error_message)

    error = getattr(response, "error", None)
    if error:
        detail = getattr(error, "message", repr(error))
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"{error_message} Detalhes: {detail}")

    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")

    return data if data is not None else response


@lru_cache
def get_supabase_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar configuradas.",
        )

    # Create Supabase client with default options
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache
def get_supabase_storage_service() -> SupabaseStorageService:
    bucket = settings.SUPABASE_BUCKET
    if not bucket:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "SUPABASE_BUCKET deve estar configurado.",
        )
    return SupabaseStorageService(get_supabase_client(), bucket, settings.SUPABASE_PUBLIC_BUCKET_URL)
