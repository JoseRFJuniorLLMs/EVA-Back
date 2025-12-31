"""
Repository para operações de banco de dados do sistema de saúde
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from database.models import (
    Usuario, Atividade, SinaisVitaisHealth, Sono,
    MedicaoCorporal, Nutricao, CicloMenstrual
)
from schemas import (
    UsuarioCreate, UsuarioUpdate,
    AtividadeCreate, SinaisVitaisHealthCreate,
    SonoCreate, MedicaoCorporalCreate,
    NutricaoCreate, CicloMenstrualCreate
)


# =====================================================
# USUÁRIOS
# =====================================================

async def create_usuario(db: AsyncSession, usuario: UsuarioCreate) -> Usuario:
    """Criar novo usuário"""
    db_usuario = Usuario(**usuario.dict())
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


async def get_usuario_by_id(db: AsyncSession, usuario_id: int) -> Optional[Usuario]:
    """Buscar usuário por ID"""
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    return result.scalar_one_or_none()


async def get_usuario_by_email(db: AsyncSession, email: str) -> Optional[Usuario]:
    """Buscar usuário por email"""
    result = await db.execute(
        select(Usuario).where(Usuario.email == email)
    )
    return result.scalar_one_or_none()


async def update_usuario(db: AsyncSession, usuario_id: int, usuario_update: UsuarioUpdate) -> Optional[Usuario]:
    """Atualizar dados do usuário"""
    db_usuario = await get_usuario_by_id(db, usuario_id)
    if not db_usuario:
        return None
    
    update_data = usuario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario


# =====================================================
# ATIVIDADE FÍSICA
# =====================================================

async def create_atividade(db: AsyncSession, atividade: AtividadeCreate) -> Atividade:
    """Criar registro de atividade"""
    db_atividade = Atividade(**atividade.dict())
    db.add(db_atividade)
    await db.commit()
    await db.refresh(db_atividade)
    return db_atividade


async def create_atividades_bulk(db: AsyncSession, atividades: List[AtividadeCreate]) -> List[Atividade]:
    """Criar múltiplos registros de atividade (sync offline)"""
    db_atividades = [Atividade(**ativ.dict()) for ativ in atividades]
    db.add_all(db_atividades)
    await db.commit()
    
    # Refresh all objects
    for ativ in db_atividades:
        await db.refresh(ativ)
    
    return db_atividades


async def get_atividades_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[Atividade]:
    """Buscar histórico de atividades com paginação e filtros"""
    query = select(Atividade).where(Atividade.cliente_id == cliente_id)
    
    if data_inicio:
        query = query.where(Atividade.timestamp_coleta >= data_inicio)
    if data_fim:
        query = query.where(Atividade.timestamp_coleta <= data_fim)
    
    query = query.order_by(Atividade.timestamp_coleta.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# =====================================================
# SINAIS VITAIS
# =====================================================

async def create_sinais_vitais(db: AsyncSession, sinais: SinaisVitaisHealthCreate) -> SinaisVitaisHealth:
    """Criar registro de sinais vitais"""
    db_sinais = SinaisVitaisHealth(**sinais.dict())
    db.add(db_sinais)
    await db.commit()
    await db.refresh(db_sinais)
    return db_sinais


async def create_sinais_vitais_bulk(db: AsyncSession, sinais_list: List[SinaisVitaisHealthCreate]) -> List[SinaisVitaisHealth]:
    """Criar múltiplos registros de sinais vitais"""
    db_sinais_list = [SinaisVitaisHealth(**sinais.dict()) for sinais in sinais_list]
    db.add_all(db_sinais_list)
    await db.commit()
    
    for sinais in db_sinais_list:
        await db.refresh(sinais)
    
    return db_sinais_list


async def get_sinais_vitais_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[SinaisVitaisHealth]:
    """Buscar histórico de sinais vitais"""
    query = select(SinaisVitaisHealth).where(SinaisVitaisHealth.cliente_id == cliente_id)
    
    if data_inicio:
        query = query.where(SinaisVitaisHealth.timestamp_coleta >= data_inicio)
    if data_fim:
        query = query.where(SinaisVitaisHealth.timestamp_coleta <= data_fim)
    
    query = query.order_by(SinaisVitaisHealth.timestamp_coleta.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# =====================================================
# SONO
# =====================================================

async def create_sono(db: AsyncSession, sono: SonoCreate) -> Sono:
    """Criar registro de sono"""
    db_sono = Sono(**sono.dict())
    db.add(db_sono)
    await db.commit()
    await db.refresh(db_sono)
    return db_sono


async def get_sono_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[Sono]:
    """Buscar histórico de sono"""
    result = await db.execute(
        select(Sono)
        .where(Sono.cliente_id == cliente_id)
        .order_by(Sono.timestamp_inicio.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =====================================================
# MEDIÇÃO CORPORAL
# =====================================================

async def create_medicao_corporal(db: AsyncSession, medicao: MedicaoCorporalCreate) -> MedicaoCorporal:
    """Criar medição corporal"""
    db_medicao = MedicaoCorporal(**medicao.dict())
    db.add(db_medicao)
    await db.commit()
    await db.refresh(db_medicao)
    return db_medicao


async def get_medicoes_corporais_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[MedicaoCorporal]:
    """Buscar histórico de medições corporais"""
    result = await db.execute(
        select(MedicaoCorporal)
        .where(MedicaoCorporal.cliente_id == cliente_id)
        .order_by(MedicaoCorporal.timestamp_coleta.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =====================================================
# NUTRIÇÃO
# =====================================================

async def create_nutricao(db: AsyncSession, nutricao: NutricaoCreate) -> Nutricao:
    """Criar registro de nutrição"""
    db_nutricao = Nutricao(**nutricao.dict())
    db.add(db_nutricao)
    await db.commit()
    await db.refresh(db_nutricao)
    return db_nutricao


async def get_nutricao_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[Nutricao]:
    """Buscar histórico de nutrição"""
    result = await db.execute(
        select(Nutricao)
        .where(Nutricao.cliente_id == cliente_id)
        .order_by(Nutricao.timestamp_coleta.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =====================================================
# CICLO MENSTRUAL
# =====================================================

async def create_ciclo_menstrual(db: AsyncSession, ciclo: CicloMenstrualCreate) -> CicloMenstrual:
    """Criar registro de ciclo menstrual"""
    db_ciclo = CicloMenstrual(**ciclo.dict())
    db.add(db_ciclo)
    await db.commit()
    await db.refresh(db_ciclo)
    return db_ciclo


async def get_ciclo_menstrual_by_usuario(
    db: AsyncSession, 
    cliente_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[CicloMenstrual]:
    """Buscar histórico de ciclo menstrual"""
    result = await db.execute(
        select(CicloMenstrual)
        .where(CicloMenstrual.cliente_id == cliente_id)
        .order_by(CicloMenstrual.data_menstruacao.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =====================================================
# DASHBOARD E RELATÓRIOS
# =====================================================

async def get_dashboard_resumo(db: AsyncSession, cliente_id: int, data: date) -> dict:
    """Resumo diário para dashboard"""
    hoje_inicio = datetime.combine(data, datetime.min.time())
    hoje_fim = datetime.combine(data, datetime.max.time())
    ontem_inicio = hoje_inicio - timedelta(days=1)
    ontem_fim = hoje_fim - timedelta(days=1)
    
    # Passos hoje
    result_passos = await db.execute(
        select(func.sum(Atividade.passos))
        .where(
            and_(
                Atividade.cliente_id == cliente_id,
                Atividade.timestamp_coleta >= hoje_inicio,
                Atividade.timestamp_coleta <= hoje_fim
            )
        )
    )
    passos_hoje = result_passos.scalar() or 0
    
    # Último BPM e pressão
    result_sinais = await db.execute(
        select(SinaisVitaisHealth)
        .where(SinaisVitaisHealth.cliente_id == cliente_id)
        .order_by(SinaisVitaisHealth.timestamp_coleta.desc())
        .limit(1)
    )
    ultimo_sinal = result_sinais.scalar_one_or_none()
    
    ultimo_bpm = ultimo_sinal.bpm if ultimo_sinal else None
    ultima_pressao = None
    if ultimo_sinal and ultimo_sinal.pressao_sistolica and ultimo_sinal.pressao_diastolica:
        ultima_pressao = f"{ultimo_sinal.pressao_sistolica}/{ultimo_sinal.pressao_diastolica}"
    
    # Sono de ontem
    result_sono = await db.execute(
        select(Sono)
        .where(
            and_(
                Sono.cliente_id == cliente_id,
                Sono.timestamp_inicio >= ontem_inicio,
                Sono.timestamp_inicio <= ontem_fim
            )
        )
        .order_by(Sono.timestamp_inicio.desc())
        .limit(1)
    )
    sono_ontem = result_sono.scalar_one_or_none()
    horas_sono = (sono_ontem.duracao_total_minutos / 60) if sono_ontem and sono_ontem.duracao_total_minutos else None
    
    # Nutrição hoje
    result_nutricao = await db.execute(
        select(
            func.sum(Nutricao.calorias_consumidas),
            func.sum(Nutricao.ingestao_agua_ml)
        )
        .where(
            and_(
                Nutricao.cliente_id == cliente_id,
                Nutricao.timestamp_coleta >= hoje_inicio,
                Nutricao.timestamp_coleta <= hoje_fim
            )
        )
    )
    nutricao_row = result_nutricao.one_or_none()
    calorias_hoje = nutricao_row[0] if nutricao_row and nutricao_row[0] else 0
    agua_hoje = nutricao_row[1] if nutricao_row and nutricao_row[1] else 0
    
    return {
        "cliente_id": cliente_id,
        "data": data,
        "passos_hoje": int(passos_hoje),
        "ultimo_bpm": ultimo_bpm,
        "ultima_pressao": ultima_pressao,
        "horas_sono_ontem": float(horas_sono) if horas_sono else None,
        "calorias_consumidas_hoje": int(calorias_hoje),
        "agua_ml_hoje": int(agua_hoje)
    }


async def get_relatorio_mensal(db: AsyncSession, cliente_id: int, mes: int, ano: int) -> dict:
    """Relatório mensal para análise de tendências"""
    # Total de passos
    result_passos = await db.execute(
        select(func.sum(Atividade.passos))
        .where(
            and_(
                Atividade.cliente_id == cliente_id,
                extract('month', Atividade.timestamp_coleta) == mes,
                extract('year', Atividade.timestamp_coleta) == ano
            )
        )
    )
    total_passos = result_passos.scalar() or 0
    
    # Média de BPM
    result_bpm = await db.execute(
        select(func.avg(SinaisVitaisHealth.bpm))
        .where(
            and_(
                SinaisVitaisHealth.cliente_id == cliente_id,
                SinaisVitaisHealth.bpm.isnot(None),
                extract('month', SinaisVitaisHealth.timestamp_coleta) == mes,
                extract('year', SinaisVitaisHealth.timestamp_coleta) == ano
            )
        )
    )
    media_bpm = result_bpm.scalar()
    
    # Média de horas de sono
    result_sono = await db.execute(
        select(func.avg(Sono.duracao_total_minutos))
        .where(
            and_(
                Sono.cliente_id == cliente_id,
                Sono.duracao_total_minutos.isnot(None),
                extract('month', Sono.timestamp_inicio) == mes,
                extract('year', Sono.timestamp_inicio) == ano
            )
        )
    )
    media_minutos_sono = result_sono.scalar()
    media_horas_sono = (media_minutos_sono / 60) if media_minutos_sono else None
    
    # Peso inicial e final
    result_peso = await db.execute(
        select(MedicaoCorporal.peso_kg)
        .where(
            and_(
                MedicaoCorporal.cliente_id == cliente_id,
                MedicaoCorporal.peso_kg.isnot(None),
                extract('month', MedicaoCorporal.timestamp_coleta) == mes,
                extract('year', MedicaoCorporal.timestamp_coleta) == ano
            )
        )
        .order_by(MedicaoCorporal.timestamp_coleta.asc())
    )
    pesos = result_peso.scalars().all()
    peso_inicial = pesos[0] if pesos else None
    peso_final = pesos[-1] if pesos else None
    
    # Total de atividades
    result_count = await db.execute(
        select(func.count(Atividade.id))
        .where(
            and_(
                Atividade.cliente_id == cliente_id,
                extract('month', Atividade.timestamp_coleta) == mes,
                extract('year', Atividade.timestamp_coleta) == ano
            )
        )
    )
    total_atividades = result_count.scalar() or 0
    
    return {
        "cliente_id": cliente_id,
        "mes": mes,
        "ano": ano,
        "total_passos": int(total_passos),
        "media_bpm": float(media_bpm) if media_bpm else None,
        "media_horas_sono": float(media_horas_sono) if media_horas_sono else None,
        "peso_inicial": peso_inicial,
        "peso_final": peso_final,
        "total_atividades": int(total_atividades)
    }
