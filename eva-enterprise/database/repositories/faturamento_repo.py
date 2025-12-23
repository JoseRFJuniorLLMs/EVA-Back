from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import AssinaturaEntidade, FaturamentoConsumo
from typing import List, Optional
import datetime

class FaturamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Assinaturas
    async def get_assinatura(self, id: int) -> Optional[AssinaturaEntidade]:
        query = select(AssinaturaEntidade).filter(AssinaturaEntidade.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_assinaturas(self) -> List[AssinaturaEntidade]:
        query = select(AssinaturaEntidade)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_assinatura(self, dados: dict) -> AssinaturaEntidade:
        assinatura = AssinaturaEntidade(**dados)
        self.db.add(assinatura)
        await self.db.commit()
        await self.db.refresh(assinatura)
        return assinatura

    # Consumo
    async def get_consumo_mes(self, idoso_id: int, mes: int, ano: int) -> Optional[FaturamentoConsumo]:
        query = select(FaturamentoConsumo).filter(
            FaturamentoConsumo.idoso_id == idoso_id,
            FaturamentoConsumo.mes_referencia == mes,
            FaturamentoConsumo.ano_referencia == ano
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def registrar_consumo(self, idoso_id: int, tokens: int, minutos: int):
        now = datetime.datetime.now()
        mes, ano = now.month, now.year
        
        consumo = await self.get_consumo_mes(idoso_id, mes, ano)
        if not consumo:
            consumo = FaturamentoConsumo(
                idoso_id=idoso_id,
                mes_referencia=mes,
                ano_referencia=ano,
                total_tokens=tokens,
                total_minutos=minutos
            )
            self.db.add(consumo)
        else:
            consumo.total_tokens += tokens
            consumo.total_minutos += minutos
        
        await self.db.commit()
        await self.db.refresh(consumo)
        return consumo
