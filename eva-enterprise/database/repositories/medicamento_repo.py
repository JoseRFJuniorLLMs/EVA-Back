"""
Medicamento Repository - Gerencia acesso a dados de medicamentos
Versão: Produção (com Fuzzy Matching)
"""
from typing import Optional, List, Dict, Any
import unicodedata
from sqlalchemy import func
from sqlalchemy.orm import Session
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
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_by_name(self, nome: str, idoso_id: int = None) -> Optional[dict]:
        """
        Busca EXATA por nome do medicamento.
        
        Args:
            nome: Nome exato do medicamento
            idoso_id: ID do idoso (opcional, filtra por idoso)
            
        Returns:
            Dict com dados do medicamento ou None
        """
        from ..models import Medicamento
        
        query = self.db.query(Medicamento).filter(
            func.lower(Medicamento.nome) == func.lower(nome),
            Medicamento.ativo == True
        )
        
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        result = query.first()
        
        if result:
            return {
                'id': result.id,
                'nome': result.nome,
                'dosagem': result.dosagem,
                'idoso_id': result.idoso_id,
                'horarios': result.horarios,
                'principio_ativo': getattr(result, 'principio_ativo', None),
                'observacoes': getattr(result, 'observacoes', None)
            }
        return None
    
    async def search_by_name(
        self, 
        nome: str, 
        idoso_id: int = None,
        min_similarity: int = 80
    ) -> Optional[dict]:
        """
        Busca FUZZY - tolera erros de pronúncia/transcrição.
        
        Casos comuns que essa busca resolve:
        - "Losartana" vs "Lozartana" (erro de transcrição Gemini)
        - "Captopril" vs "Captopri" (idoso pronuncia errado)
        - "Omeprazol" vs "Omeprazó" (sotaque)
        - "Metformina" vs "Merformina" (confusão fonética)
        
        Args:
            nome: Nome do medicamento (pode conter erros)
            idoso_id: ID do idoso (filtra medicamentos desse idoso)
            min_similarity: Similaridade mínima para match (0-100)
            
        Returns:
            Dict com medicamento mais similar ou None
        """
        if not FUZZYWUZZY_AVAILABLE:
            # Fallback para busca por substring
            return await self._search_substring(nome, idoso_id)
        
        from ..models import Medicamento
        
        query = self.db.query(Medicamento).filter(Medicamento.ativo == True)
        
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        medicamentos = query.all()
        
        if not medicamentos:
            return None
        
        best_match = None
        best_score = 0
        nome_limpo = self._normalize_name(nome)
        
        for med in medicamentos:
            med_limpo = self._normalize_name(med.nome)
            
            # Calcula 3 tipos de scores
            score_ratio = fuzz.ratio(nome_limpo, med_limpo)
            score_partial = fuzz.partial_ratio(nome_limpo, med_limpo)
            score_token = fuzz.token_sort_ratio(nome_limpo, med_limpo)
            
            # Score ponderado (exatidão > parcial > tokens)
            score = (score_ratio * 0.5) + (score_partial * 0.3) + (score_token * 0.2)
            
            if score > best_score:
                best_score = score
                best_match = med
        
        if best_score >= min_similarity:
            print(f"✓ [MEDICAMENTO] Fuzzy match: '{nome}' → '{best_match.nome}' ({best_score:.0f}%)")
            return {
                'id': best_match.id,
                'nome': best_match.nome,
                'dosagem': best_match.dosagem,
                'idoso_id': best_match.idoso_id,
                'horarios': best_match.horarios,
                'principio_ativo': getattr(best_match, 'principio_ativo', None),
                'confidence': best_score
            }
        
        print(f"✗ [MEDICAMENTO] Nenhum match: '{nome}' (best: {best_score:.0f}%)")
        return None
    
    async def _search_substring(self, nome: str, idoso_id: int = None) -> Optional[dict]:
        """
        Fallback: busca por substring quando fuzzywuzzy não está disponível.
        """
        from ..models import Medicamento
        
        nome_limpo = self._normalize_name(nome)
        
        query = self.db.query(Medicamento).filter(
            func.lower(Medicamento.nome).like(f'%{nome_limpo}%'),
            Medicamento.ativo == True
        )
        
        if idoso_id:
            query = query.filter(Medicamento.idoso_id == idoso_id)
        
        result = query.first()
        
        if result:
            return {
                'id': result.id,
                'nome': result.nome,
                'dosagem': result.dosagem,
                'idoso_id': result.idoso_id,
                'horarios': result.horarios
            }
        return None
    
    async def get_by_idoso(self, idoso_id: int) -> List[dict]:
        """
        Lista todos medicamentos ativos de um idoso.
        
        Args:
            idoso_id: ID do idoso
            
        Returns:
            Lista de medicamentos
        """
        from ..models import Medicamento
        
        results = self.db.query(Medicamento).filter(
            Medicamento.idoso_id == idoso_id,
            Medicamento.ativo == True
        ).order_by(Medicamento.nome).all()
        
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
        """
        Lista medicamentos agendados para hoje.
        
        Args:
            idoso_id: ID do idoso
            
        Returns:
            Lista de medicamentos com horários de hoje
        """
        # TODO: Implementar lógica de horários do dia
        return await self.get_by_idoso(idoso_id)
    
    async def validate_exists(self, nome: str, idoso_id: int) -> bool:
        """
        Valida se um medicamento existe para o idoso (exato ou fuzzy).
        
        Args:
            nome: Nome do medicamento
            idoso_id: ID do idoso
            
        Returns:
            True se existe, False caso contrário
        """
        exact = await self.get_by_name(nome, idoso_id)
        if exact:
            return True
        
        fuzzy = await self.search_by_name(nome, idoso_id)
        return fuzzy is not None
    
    @staticmethod
    def _normalize_name(nome: str) -> str:
        """
        Normaliza nome para comparação:
        - Remove acentos
        - Converte para lowercase
        - Remove espaços extras
        """
        # Remove acentos
        nome = unicodedata.normalize('NFKD', nome)
        nome = ''.join([c for c in nome if not unicodedata.combining(c)])
        
        # Lowercase e trim
        nome = nome.lower().strip()
        
        # Remove espaços duplicados
        nome = ' '.join(nome.split())
        
        return nome

    # CRUD Operations
    def create(self, dados: dict) -> Medicamento:
        med = Medicamento(**dados)
        self.db.add(med)
        self.db.commit()
        self.db.refresh(med)
        return med

    def get_by_id(self, id: int) -> Optional[Medicamento]:
        return self.db.query(Medicamento).filter(Medicamento.id == id).first()

    def update(self, id: int, dados: dict) -> Optional[Medicamento]:
        med = self.get_by_id(id)
        if med:
            for k, v in dados.items():
                if v is not None:
                    setattr(med, k, v)
            self.db.commit()
            self.db.refresh(med)
        return med

    def delete(self, id: int) -> bool:
        med = self.get_by_id(id)
        if med:
            # Soft delete? Or hard? Plan says "desativa" which implies soft delete or update active=False
            # But the requirement said "DELETE /medicamentos/{id} (desativa)".
            # So I will set active=False or actually delete?
            # User said "DELETE ... (desativa)". I will set active=False.
            med.ativo = False
            self.db.commit()
            return True
        return False
        
    def confirm_intake(self, medicamento_id: int, agendamento_id: int = None):
        # Implementation for confirming intake could go here or in agendamento logic
        pass

class SinaisVitaisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, dados: dict) -> SinaisVitais:
        sinal = SinaisVitais(**dados)
        self.db.add(sinal)
        self.db.commit()
        self.db.refresh(sinal)
        return sinal

    def get_by_idoso(self, idoso_id: int, limit: int = 20) -> List[SinaisVitais]:
        return self.db.query(SinaisVitais)\
            .filter(SinaisVitais.idoso_id == idoso_id)\
            .order_by(SinaisVitais.data_medicao.desc())\
            .limit(limit).all()

    def get_weekly_report(self, idoso_id: int) -> List[SinaisVitais]:
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        return self.db.query(SinaisVitais)\
            .filter(SinaisVitais.idoso_id == idoso_id, SinaisVitais.data_medicao >= week_ago)\
            .all()

