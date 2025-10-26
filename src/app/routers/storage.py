from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

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
    stored_path = storage.upload_file(
        destination_path,
        payload,
        content_type=file.content_type,
        upsert=True,
    )
    public_url: str | None = None
    try:
        public_url = storage.get_public_url(stored_path)
    except HTTPException:
        public_url = storage.build_public_url(stored_path)
    return {"path": stored_path, "public_url": public_url}


@router.post(
    "/sign",
    summary="Gera uma URL assinada temporária para um arquivo privado no Supabase.",
)
def generate_signed_url(
    payload: GenerateSignedUrlPayload,
    storage: SupabaseStorageService = Depends(get_supabase_storage_service),
):
    signed_url = storage.create_signed_url(
        payload.path,
        expires_in_seconds=payload.expires_in_seconds,
    )
    return {"signed_url": signed_url}


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um arquivo do bucket configurado no Supabase.",
)
def delete_file(
    destination_path: str,
    storage: SupabaseStorageService = Depends(get_supabase_storage_service),
):
    storage.delete_file(destination_path)
    return None
