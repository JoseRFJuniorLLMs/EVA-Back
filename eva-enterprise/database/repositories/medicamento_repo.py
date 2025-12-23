from typing import Optional, List, Dict, Any
import unicodedata
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Medicamento, SinaisVitais
import datetime

# Tenta importar fuzzywuzzy para busca fuzzy
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("⚠️ fuzzywuzzy não disponível. Execute: pip install python-Levenshtein fuzzywuzzy")


class MedicamentoRepository:
    """
    Repositório para operações com medicamentos dos idosos.
    Suporta busca exata e fuzzy matching para tolerar erros de transcrição.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_name(self, nome: str, idoso_id: int = None) -> Optional[dict]:
        query = select(Medicamento).filter(
            func.lower(Medicamento.nome) == func.lower(nome),
            Medicamento.ativo == True
        )
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        result = await self.db.execute(query)
        res = result.scalar_one_or_none()
        
        if res:
            return {
                'id': res.id,
                'nome': res.nome,
                'dosagem': res.dosagem,
                'idoso_id': res.idoso_id,
                'horarios': res.horarios,
                'principio_ativo': getattr(res, 'principio_ativo', None),
                'observacoes': getattr(res, 'observacoes', None)
            }
        return None
    
    async def search_by_name(
        self, 
        nome: str, 
        idoso_id: int = None,
        min_similarity: int = 80
    ) -> Optional[dict]:
        if not FUZZYWUZZY_AVAILABLE:
            return await self._search_substring(nome, idoso_id)
        
        query = select(Medicamento).filter(Medicamento.ativo == True)
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        result = await self.db.execute(query)
        medicamentos = result.scalars().all()
        
        if not medicamentos:
            return None
        
        best_match = None
        best_score = 0
        nome_limpo = self._normalize_name(nome)
        
        for med in medicamentos:
            med_limpo = self._normalize_name(med.nome)
            score_ratio = fuzz.ratio(nome_limpo, med_limpo)
            score_partial = fuzz.partial_ratio(nome_limpo, med_limpo)
            score_token = fuzz.token_sort_ratio(nome_limpo, med_limpo)
            score = (score_ratio * 0.5) + (score_partial * 0.3) + (score_token * 0.2)
            
            if score > best_score:
                best_score = score
                best_match = med
        
        if best_score >= min_similarity:
            return {
                'id': best_match.id,
                'nome': best_match.nome,
                'dosagem': best_match.dosagem,
                'idoso_id': best_match.idoso_id,
                'horarios': best_match.horarios,
                'principio_ativo': getattr(best_match, 'principio_ativo', None),
                'confidence': best_score
            }
        return None
    
    async def _search_substring(self, nome: str, idoso_id: int = None) -> Optional[dict]:
        nome_limpo = self._normalize_name(nome)
        query = select(Medicamento).filter(
            func.lower(Medicamento.nome).like(f'%{nome_limpo}%'),
            Medicamento.ativo == True
        )
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        result = await self.db.execute(query)
        res = result.scalar_one_or_none()
        if res:
            return {
                'id': res.id,
                'nome': res.nome,
                'dosagem': res.dosagem,
                'idoso_id': res.idoso_id,
                'horarios': res.horarios
            }
        return None
    
    async def get_by_idoso(self, idoso_id: int) -> List[dict]:
        query = select(Medicamento).filter(
            Medicamento.idoso_id == idoso_id,
            Medicamento.ativo == True
        ).order_by(Medicamento.nome)
        
        result = await self.db.execute(query)
        results = result.scalars().all()
        return [{
            'id': r.id,
            'nome': r.nome,
            'dosagem': r.dosagem,
            'idoso_id': r.idoso_id,
            'horarios': r.horarios,
            'principio_ativo': getattr(r, 'principio_ativo', None),
            'forma': getattr(r, 'forma', None),
            'observacoes': getattr(r, 'observacoes', None)
        } for r in results]
    
    async def get_scheduled_for_today(self, idoso_id: int) -> List[dict]:
        return await self.get_by_idoso(idoso_id)
    
    async def validate_exists(self, nome: str, idoso_id: int) -> bool:
        exact = await self.get_by_name(nome, idoso_id)
        if exact:
            return True
        fuzzy = await self.search_by_name(nome, idoso_id)
        return fuzzy is not None
    
    @staticmethod
    def _normalize_name(nome: str) -> str:
        nome = unicodedata.normalize('NFKD', nome)
        nome = ''.join([c for c in nome if not unicodedata.combining(c)])
        nome = nome.lower().strip()
        nome = ' '.join(nome.split())
        return nome

    async def create(self, dados: dict) -> Medicamento:
        med = Medicamento(**dados)
        self.db.add(med)
        await self.db.commit()
        await self.db.refresh(med)
        return med

    async def get_by_id(self, id: int) -> Optional[Medicamento]:
        query = select(Medicamento).filter(Medicamento.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, id: int, dados: dict) -> Optional[Medicamento]:
        med = await self.get_by_id(id)
        if med:
            for k, v in dados.items():
                if v is not None:
                    setattr(med, k, v)
            await self.db.commit()
            await self.db.refresh(med)
        return med

    async def delete(self, id: int) -> bool:
        med = await self.get_by_id(id)
        if med:
            med.ativo = False
            await self.db.commit()
            return True
        return False
        
    async def confirm_intake(self, medicamento_id: int, agendamento_id: int = None):
        pass

class SinaisVitaisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dados: dict) -> SinaisVitais:
        sinal = SinaisVitais(**dados)
        self.db.add(sinal)
        await self.db.commit()
        await self.db.refresh(sinal)
        return sinal

    async def get_by_idoso(self, idoso_id: int, limit: int = 20) -> List[SinaisVitais]:
        query = select(SinaisVitais)\
            .filter(SinaisVitais.idoso_id == idoso_id)\
            .order_by(SinaisVitais.data_medicao.desc())\
            .limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_weekly_report(self, idoso_id: int) -> List[SinaisVitais]:
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        query = select(SinaisVitais)\
            .filter(SinaisVitais.idoso_id == idoso_id, SinaisVitais.data_medicao >= week_ago)
        result = await self.db.execute(query)
        return result.scalars().all()

