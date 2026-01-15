"""
Voice Cloning Routes - Integração com EVA-Voice
Gerenciamento de vozes clonadas dos familiares
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
import httpx
import os
from database.connection import get_db
from utils.security import require_subscription

router = APIRouter()

# URL do microserviço EVA-Voice
EVA_VOICE_URL = os.getenv("EVA_VOICE_URL", "http://localhost:8001")

# ==========================================
# VOICE CLONING
# ==========================================

@router.post("/voices/clone", dependencies=[Depends(require_subscription("gold"))])
async def clone_voice(
    audio: UploadFile = File(...),
    idoso_id: int = Form(...),
    familiar_nome: str = Form(...),
    familiar_tipo: str = Form(...),  # "filha", "filho", "neta", etc
    emotion_type: str = Form("loving"),  # "serious", "loving", "happy"
    db: AsyncSession = Depends(get_db)
):
    """
    Clona a voz de um familiar
    
    Args:
        audio: Arquivo de áudio (.wav, .mp3)
        idoso_id: ID do idoso
        familiar_nome: Nome do familiar (ex: "Ana")
        familiar_tipo: Tipo de familiar (filha, filho, neta, etc)
        emotion_type: Tipo de emoção (serious, loving, happy)
    """
    try:
        # Ler áudio
        audio_bytes = await audio.read()
        
        # Enviar para EVA-Voice
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"audio": (audio.filename, audio_bytes, audio.content_type)}
            data = {
                "user_id": f"{familiar_tipo}_{familiar_nome}_{idoso_id}",
                "emotion_type": emotion_type
            }
            
            response = await client.post(
                f"{EVA_VOICE_URL}/clone-voice",
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                raise HTTPException(500, f"Erro no EVA-Voice: {response.text}")
            
            voice_data = response.json()
        
        # Salvar no banco de dados
        query = text("""
            INSERT INTO family_voices (
                idoso_id,
                familiar_nome,
                familiar_tipo,
                emotion_type,
                voice_id,
                file_size_kb,
                created_at
            ) VALUES (
                :idoso_id,
                :familiar_nome,
                :familiar_tipo,
                :emotion_type,
                :voice_id,
                :file_size_kb,
                NOW()
            )
            RETURNING id
        """)
        
        result = await db.execute(query, {
            "idoso_id": idoso_id,
            "familiar_nome": familiar_nome,
            "familiar_tipo": familiar_tipo,
            "emotion_type": emotion_type,
            "voice_id": voice_data["voice_id"],
            "file_size_kb": voice_data["file_size_kb"]
        })
        
        await db.commit()
        
        db_id = result.scalar()
        
        return {
            "id": db_id,
            "voice_id": voice_data["voice_id"],
            "familiar_nome": familiar_nome,
            "emotion_type": emotion_type,
            "message": "Voz clonada com sucesso!"
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(500, f"Erro ao conectar com EVA-Voice: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Erro ao clonar voz: {str(e)}")


@router.post("/voices/speak", dependencies=[Depends(require_subscription("gold"))])
async def generate_speech(
    text: str = Form(...),
    idoso_id: int = Form(...),
    familiar_tipo: str = Form("filha"),
    emotion_type: str = Form("loving"),
    speed: float = Form(1.0),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera áudio com voz clonada
    
    Args:
        text: Texto a ser falado
        idoso_id: ID do idoso
        familiar_tipo: Tipo de familiar (filha, filho, etc)
        emotion_type: Emoção (serious, loving, happy)
        speed: Velocidade da fala (0.5 a 2.0)
    """
    try:
        # Buscar voice_id no banco
        query = text("""
            SELECT voice_id
            FROM family_voices
            WHERE idoso_id = :idoso_id
              AND familiar_tipo = :familiar_tipo
              AND emotion_type = :emotion_type
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = await db.execute(query, {
            "idoso_id": idoso_id,
            "familiar_tipo": familiar_tipo,
            "emotion_type": emotion_type
        })
        
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                404, 
                f"Voz não encontrada para {familiar_tipo} com emoção {emotion_type}"
            )
        
        voice_id = row[0]
        
        # Gerar áudio no EVA-Voice
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EVA_VOICE_URL}/speak",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "language": "pt",
                    "emotion_type": emotion_type,
                    "speed": speed
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(500, f"Erro no EVA-Voice: {response.text}")
            
            audio_bytes = response.content
        
        # Retornar áudio
        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=eva_voice_{idoso_id}.wav"
            }
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(500, f"Erro ao conectar com EVA-Voice: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Erro ao gerar fala: {str(e)}")


@router.get("/voices/list/{idoso_id}")
async def list_voices(
    idoso_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as vozes clonadas de um idoso
    """
    query = text("""
        SELECT 
            id,
            familiar_nome,
            familiar_tipo,
            emotion_type,
            voice_id,
            file_size_kb,
            created_at
        FROM family_voices
        WHERE idoso_id = :idoso_id
        ORDER BY familiar_tipo, emotion_type
    """)
    
    result = await db.execute(query, {"idoso_id": idoso_id})
    rows = result.fetchall()
    
    return {
        "idoso_id": idoso_id,
        "voices": [
            {
                "id": row[0],
                "familiar_nome": row[1],
                "familiar_tipo": row[2],
                "emotion_type": row[3],
                "voice_id": row[4],
                "file_size_kb": float(row[5]) if row[5] else 0,
                "created_at": row[6].isoformat() if row[6] else None
            }
            for row in rows
        ],
        "total": len(rows)
    }


@router.delete("/voices/{voice_db_id}")
async def delete_voice(
    voice_db_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta uma voz clonada
    """
    try:
        # Buscar voice_id
        query = text("SELECT voice_id FROM family_voices WHERE id = :id")
        result = await db.execute(query, {"id": voice_db_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(404, "Voz não encontrada")
        
        voice_id = row[0]
        
        # Deletar do EVA-Voice
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.delete(f"{EVA_VOICE_URL}/voices/{voice_id}")
        
        # Deletar do banco
        delete_query = text("DELETE FROM family_voices WHERE id = :id")
        await db.execute(delete_query, {"id": voice_db_id})
        await db.commit()
        
        return {"message": "Voz deletada com sucesso"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Erro ao deletar voz: {str(e)}")


@router.get("/voices/health")
async def check_voice_service():
    """
    Verifica se o EVA-Voice está online
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{EVA_VOICE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "online",
                    "eva_voice_url": EVA_VOICE_URL,
                    "service_info": data
                }
            else:
                return {
                    "status": "error",
                    "eva_voice_url": EVA_VOICE_URL,
                    "error": response.text
                }
    except Exception as e:
        return {
            "status": "offline",
            "eva_voice_url": EVA_VOICE_URL,
            "error": str(e)
        }


@router.post("/voices/batch-cache", dependencies=[Depends(require_subscription("gold"))])
async def batch_cache_voices(
    idoso_id: int = Form(...),
    texts: List[str] = Form(...),
    familiar_tipo: str = Form("filha"),
    emotion_type: str = Form("loving"),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera múltiplos áudios de uma vez (cache noturno)
    Útil para pré-gerar lembretes fixos
    """
    try:
        # Buscar voice_id
        query = text("""
            SELECT voice_id
            FROM family_voices
            WHERE idoso_id = :idoso_id
              AND familiar_tipo = :familiar_tipo
              AND emotion_type = :emotion_type
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = await db.execute(query, {
            "idoso_id": idoso_id,
            "familiar_tipo": familiar_tipo,
            "emotion_type": emotion_type
        })
        
        row = result.fetchone()
        
        if not row:
            raise HTTPException(404, "Voz não encontrada")
        
        voice_id = row[0]
        
        # Gerar batch no EVA-Voice
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{EVA_VOICE_URL}/batch-generate",
                json={
                    "texts": texts,
                    "voice_id": voice_id,
                    "language": "pt"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(500, f"Erro no EVA-Voice: {response.text}")
            
            batch_result = response.json()
        
        return {
            "idoso_id": idoso_id,
            "voice_id": voice_id,
            "total_generated": batch_result["total"],
            "results": batch_result["results"]
        }
        
    except Exception as e:
        raise HTTPException(500, f"Erro no batch: {str(e)}")
