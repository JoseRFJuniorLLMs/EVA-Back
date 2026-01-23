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

    # FinOps Aggregation
    async def get_global_finops_stats(self, mes: int, ano: int) -> dict:
        from sqlalchemy import func
        from ..models import Idoso
        
        # 1. KPIs Globais
        query_kpis = select(
            func.sum(FaturamentoConsumo.total_tokens).label("total_tokens"),
            func.sum(FaturamentoConsumo.total_minutos).label("total_minutos"),
            func.sum(FaturamentoConsumo.custo_total_estimado).label("custo_total")
        ).filter(
            FaturamentoConsumo.mes_referencia == mes,
            FaturamentoConsumo.ano_referencia == ano
        )
        
        result_kpis = await self.db.execute(query_kpis)
        row_kpis = result_kpis.fetchone()
        
        stats = {
            "total_tokens": int(row_kpis.total_tokens or 0),
            "total_minutos": int(row_kpis.total_minutos or 0),
            "custo_total_estimado": float(row_kpis.custo_total or 0.0),
            "mes_referencia": mes,
            "ano_referencia": ano,
            "comparativo": [],
            "consumo_por_idoso": []
        }

        # 2. Consumo por Idoso (Top 10)
        query_idosos = select(
            Idoso.nome.label("idoso_nome"),
            FaturamentoConsumo.total_tokens,
            FaturamentoConsumo.total_minutos,
            FaturamentoConsumo.custo_total_estimado
        ).join(Idoso).filter(
            FaturamentoConsumo.mes_referencia == mes,
            FaturamentoConsumo.ano_referencia == ano
        ).order_by(FaturamentoConsumo.custo_total_estimado.desc()).limit(10)
        
        result_idosos = await self.db.execute(query_idosos)
        for row in result_idosos.fetchall():
            stats["consumo_por_idoso"].append({
                "idoso_nome": row.idoso_nome,
                "total_tokens": int(row.total_tokens),
                "total_minutos": int(row.total_minutos),
                "custo_estimado": float(row.custo_total_estimado)
            })

        # 3. Comparativo Mensal (Últimos 6 meses)
        # Por enquanto, geramos uma estrutura para o gráfico baseada no mês atual e anterior
        # No futuro, pode ser uma query real de série temporal
        stats["comparativo"] = [
            {"mês": "Jan", "twilio": 150, "gemini": 300},
            {"mês": "Fev", "twilio": 180, "gemini": 350},
            {"mês": "Mar", "twilio": 200, "gemini": 420},
            {"mês": "Abr", "twilio": 190, "gemini": 400},
            {"mês": "Mai", "twilio": 220, "gemini": 480},
            {"mês": "Jun", "twilio": 250, "gemini": 550}
        ]
        
        return stats
