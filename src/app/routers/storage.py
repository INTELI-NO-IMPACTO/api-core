from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator

from ..utils.supabase import SupabaseStorageService, get_supabase_storage_service

router = APIRouter(prefix="/storage", tags=["storage"])


class GenerateSignedUrlPayload(BaseModel):
    path: str = Field(..., description="Caminho do arquivo dentro do bucket.")
    expires_in_seconds: int = Field(
        3600,
        ge=1,
        le=60 * 60 * 24 * 7,
        description="Tempo de expiração da URL assinada (segundos).",
    )


class DeleteFilesPayload(BaseModel):
    prefixes: list[str] = Field(
        ...,
        min_length=1,
        description="Lista de caminhos (incluindo pastas) dentro do bucket a serem removidos.",
    )

    @field_validator("prefixes")
    @classmethod
    def validate_prefixes(cls, prefixes: list[str]) -> list[str]:
        if any(not prefix or not prefix.strip() for prefix in prefixes):
            raise ValueError("Cada caminho deve ser uma string não vazia.")
        return prefixes


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Envia um arquivo para o bucket configurado no Supabase.",
)
async def upload_file(
    destination_path: str = Form(..., description="Caminho (incluindo pastas) dentro do bucket."),
    file: UploadFile = File(..., description="Arquivo a ser enviado para o Supabase."),
    storage: SupabaseStorageService = Depends(get_supabase_storage_service),
):
    payload = await file.read()
    stored_path = await run_in_threadpool(
        storage.upload_file,
        destination_path,
        payload,
        content_type=file.content_type,
        upsert=True,
    )
    public_url = storage.get_public_url(stored_path)
    return {"path": stored_path, "public_url": public_url}


@router.post(
    "/sign",
    summary="Gera uma URL assinada temporária para um arquivo privado no Supabase.",
)
async def generate_signed_url(
    payload: GenerateSignedUrlPayload,
    storage: SupabaseStorageService = Depends(get_supabase_storage_service),
):
    signed_url = await run_in_threadpool(
        storage.create_signed_url,
        payload.path,
        expires_in_seconds=payload.expires_in_seconds,
    )
    return {"signed_url": signed_url}


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um ou mais arquivos do bucket configurado no Supabase.",
)
async def delete_file(
    payload: DeleteFilesPayload,
    storage: SupabaseStorageService = Depends(get_supabase_storage_service),
):
    await run_in_threadpool(storage.delete_files, payload.prefixes)
    return None
