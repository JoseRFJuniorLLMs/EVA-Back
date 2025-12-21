"""
Medication Handler - Gerencia confirmação de medicamentos
Com proteção contra race conditions
"""
from asyncio import Lock
from typing import Optional
from database.connection import SessionLocal
from database.repositories.historico_repo import HistoricoRepository
from database.repositories.agendamento_repo import AgendamentoRepository

# Lock global para prevenir race conditions
_execution_locks = {}  # {ligacao_id: Lock}


class MedicationHandler:
    def __init__(self):
        pass

    def confirm_intake(self, text: str, agendamento_id: int):
        # Logic to confirm if medication was taken based on text
        # Potentially update DB
        pass


async def confirm_medication(
    medicamento: str, 
    tomou: bool, 
    observacoes: str = "",
    call_context: dict = None
) -> dict:
    """
    Registra confirmação de medicamento com proteção contra race condition.
    
    Args:
        medicamento: Nome do medicamento
        tomou: True se o idoso confirmou que tomou
        observacoes: Observações adicionais
        call_context: Contexto da ligação atual
        
    Returns:
        dict com status da operação
    """
    if not call_context:
        return {'success': False, 'message': 'Contexto da ligação não fornecido'}
    
    ligacao_id = call_context.get('ligacao_id')
    if not ligacao_id:
        return {'success': False, 'message': 'ID da ligação não encontrado'}
    
    # CRÍTICO: Previne race condition se usuário interromper
    if ligacao_id not in _execution_locks:
        _execution_locks[ligacao_id] = Lock()
    
    try:
        async with _execution_locks[ligacao_id]:
            db = SessionLocal()
            try:
                historico_repo = HistoricoRepository(db)
                
                # Verifica se ligação ainda está ativa
                ligacao = await historico_repo.get_by_id(ligacao_id)
                if not ligacao:
                    return {'success': False, 'message': 'Ligação não encontrada'}
                
                if ligacao.get('status') not in ['em_andamento', 'ativa']:
                    return {'success': False, 'message': 'Ligação encerrada'}
                
                # Valida que medicamento existe no sistema
                from ..database.repositories.medicamento_repo import MedicamentoRepository
                medicamento_repo = MedicamentoRepository(db)
                med = await medicamento_repo.get_by_name(medicamento)
                
                idoso_id = call_context.get('idoso_id')
                if not med:
                    # Se não encontrar por nome exato, tenta busca parcial
                    med = await medicamento_repo.search_by_name(medicamento, idoso_id)
                
                if not med:
                    return {'success': False, 'message': f'Medicamento "{medicamento}" não encontrado no sistema'}
                
                if med.get('idoso_id') and med['idoso_id'] != idoso_id:
                    return {'success': False, 'message': 'Medicamento não pertence a este idoso'}
                
                # Registra a confirmação
                agendamento_repo = AgendamentoRepository(db)
                agendamento_id = call_context.get('agendamento_id')
                
                if tomou:
                    # Atualiza agendamento como concluído
                    await agendamento_repo.update_status(agendamento_id, 'concluido')
                    
                    # Registra ação no histórico
                    await historico_repo.add_action(ligacao_id, {
                        'acao': 'confirm_medication',
                        'medicamento': medicamento,
                        'tomou': True,
                        'observacoes': observacoes
                    })
                    
                    return {
                        'success': True, 
                        'message': f'Confirmado: {medicamento} foi tomado',
                        'objetivo_alcancado': True
                    }
                else:
                    # Registra que não tomou
                    await historico_repo.add_action(ligacao_id, {
                        'acao': 'confirm_medication',
                        'medicamento': medicamento,
                        'tomou': False,
                        'observacoes': observacoes
                    })
                    
                    return {
                        'success': True, 
                        'message': f'{medicamento} não foi tomado. Encorajar o idoso.',
                        'objetivo_alcancado': False
                    }
            finally:
                db.close()
    finally:
        # Limpa lock após uso
        if ligacao_id in _execution_locks:
            del _execution_locks[ligacao_id]
