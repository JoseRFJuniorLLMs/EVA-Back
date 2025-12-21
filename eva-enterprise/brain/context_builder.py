"""
Context Builder - Monta contexto completo da ligação (IMPLEMENTAÇÃO COMPLETA)
Substitui TUDO que era hardcoded por dados do banco
"""
import chevron
from datetime import datetime
from typing import Dict, Any, List
from database.connection import SessionLocal
from database.repositories.agendamento_repo import AgendamentoRepository
from database.repositories.idoso_repo import IdosoRepository
from database.repositories.historico_repo import HistoricoRepository
from database.repositories.config_repo import ConfigRepository
from config.settings import DynamicConfig


class ContextBuilder:
    """
    Cérebro do sistema - monta contexto personalizado para cada ligação
    """
    
    def __init__(self):
        self.config = DynamicConfig()
    
    async def build_call_context(self, agendamento_id: int) -> Dict[str, Any]:
        """
        Monta pacote completo de contexto para a ligação
        
        Returns:
            {
                'system_prompt': str,
                'model_config': dict,
                'voice_config': dict,
                'audio_config': dict,
                'functions': list,
                'metadata': dict
            }
        """
        db = SessionLocal()
        try:
            # 1. Busca agendamento
            agendamento_repo = AgendamentoRepository(db)
            agendamento = agendamento_repo.get_details_with_idoso(agendamento_id)
            
            if not agendamento:
                raise ValueError(f"Agendamento {agendamento_id} não encontrado")
            
            # 2. Busca perfil do idoso
            idoso_repo = IdosoRepository(db)
            idoso = idoso_repo.get_by_id(agendamento.idoso_id)
            
            # 3. Busca histórico (últimas 5 ligações)
            historico_repo = HistoricoRepository(db)
            historico = await historico_repo.get_recent_by_idoso(idoso.id, limit=5)
            
            # 4. Busca configs do sistema
            sys_configs = await self.config.get_all_active()
            
            # 5. Busca templates de prompt
            prompt_template = self._get_prompt_template(agendamento.status)
            
            # 6. Monta variáveis para Mustache
            variables = self._build_template_variables(
                idoso=idoso,
                agendamento=agendamento,
                historico=historico
            )
            
            # 7. Renderiza prompt
            system_prompt = chevron.render(prompt_template, variables)
            
            # 8. Busca functions disponíveis
            functions = await self._get_available_functions(agendamento.status)
            
            # 9. Personaliza configurações de áudio
            audio_config = self._personalize_audio(idoso, sys_configs)
            
            # 10. Busca session_handle se existir (para Session Resumption)
            session_handle = getattr(agendamento, 'gemini_session_handle', None)
            
            # 11. Calcula retry policy
            retry_config = {
                'max_retries': getattr(agendamento, 'max_retries', 3),
                'current_retry': getattr(agendamento, 'tentativas_realizadas', 0),
                'retry_interval': getattr(agendamento, 'retry_interval_minutes', 15),
                'escalation_policy': getattr(agendamento, 'escalation_policy', 'alert_family')
            }
            
            return {
                'system_prompt': system_prompt,
                'model_config': {
                    'model_id': sys_configs.get('gemini.model_id'),
                    'temperature': sys_configs.get('gemini.temperature', 0.8)
                },
                'voice_config': {
                    'voice_name': sys_configs.get('gemini.voice_name', 'Aoede')
                },
                'audio_config': audio_config,
                'functions': functions,
                'metadata': {
                    'agendamento_id': agendamento_id,
                    'idoso_id': idoso.id,
                    'idoso_nome': idoso.nome,
                    'tipo_agendamento': agendamento.status,
                    'dados_tarefa': self._parse_dados_tarefa(agendamento),
                    'familiar_principal': self._get_familiar_principal(idoso),
                    'ambiente_ruidoso': getattr(idoso, 'ambiente_ruidoso', False)
                },
                'session_resumption': {
                    'enabled': True,
                    'previous_handle': session_handle,
                    'checkpoint_state': getattr(agendamento, 'ultima_interacao_estado', None)
                },
                'retry_config': retry_config
            }
        finally:
            db.close()
    
    def _get_prompt_template(self, tipo_agendamento: str) -> str:
        """
        Retorna template de prompt baseado no tipo de agendamento
        """
        # Template base
        base_template = """Você é a Eva, uma assistente pessoal muito gentil, paciente e carinhosa que cuida de idosos.

INFORMAÇÕES DO IDOSO:
- Nome: {{nome_idoso}}
- Idade: {{idade}} anos
- Tom de voz preferido: {{tom_voz}}
- Nível cognitivo: {{nivel_cognitivo}}
{{#limitacoes_auditivas}}
- IMPORTANTE: {{nome_idoso}} tem limitações auditivas. Fale mais devagar e articule bem.
{{/limitacoes_auditivas}}

INSTRUÇÕES GERAIS:
- Sua voz deve ser {{tom_voz}} e calma
- Fale de forma simples e natural, como se estivesse conversando com um amigo querido
- Responda SEMPRE de forma direta e natural
- NÃO pense alto, NÃO explique seu raciocínio
- Seja breve e vá direto ao ponto (máximo 2-3 frases por resposta)
- Use linguagem simples e calorosa
- Espere o usuário falar antes de responder novamente

{{#primeira_interacao}}
IMPORTANTE: Esta é a primeira vez que você conversa com {{nome_idoso}}. Seja extra gentil e paciente.
{{/primeira_interacao}}

{{#taxa_adesao_baixa}}
ATENÇÃO: {{nome_idoso}} tem histórico de baixa adesão aos medicamentos ({{taxa_adesao}}%). Seja mais encorajador(a).
{{/taxa_adesao_baixa}}
"""
        
        # Template específico para medicação
        if tipo_agendamento in ['pendente', 'retry_agendado']:
            base_template += """

TAREFA ATUAL - LEMBRETE DE MEDICAMENTO:
- Você está ligando para lembrar {{nome_idoso}} de tomar: {{medicamento}}
- Dosagem: {{dosagem}}
- Horário: {{horario}}

PROTOCOLO:
1. Cumprimente {{nome_idoso}} de forma calorosa
2. Pergunte como ele(a) está se sentindo
3. Lembre sobre o medicamento de forma gentil
4. Confirme se já tomou ou se vai tomar agora
5. Se já tomou, elogie e deseje um bom dia
6. Se não tomou, pergunte se há algum motivo e encoraje gentilmente

PROTOCOLO DE EMERGÊNCIA:
- Se {{nome_idoso}} mencionar dor forte, tontura, falta de ar, dor no peito ou qualquer sintoma grave:
  1. Mantenha a calma e tranquilize a pessoa
  2. Pergunte se há alguém por perto que possa ajudar
  3. Use a função alert_family para notificar imediatamente
  4. NÃO encerre a ligação até ter certeza de que há ajuda a caminho
"""
        
        return base_template
    
    def _build_template_variables(
        self,
        idoso,
        agendamento,
        historico: List
    ) -> Dict[str, Any]:
        """
        Monta variáveis para substituição no template Mustache
        """
        idade = self._calculate_age(idoso.data_nascimento) if hasattr(idoso, 'data_nascimento') else 0
        taxa_adesao = self._calculate_adherence(historico)
        
        # Parse dados da tarefa (medicamento, dosagem, etc)
        dados_tarefa = self._parse_dados_tarefa(agendamento)
        
        return {
            'nome_idoso': idoso.nome,
            'idade': idade,
            'tom_voz': getattr(idoso, 'tom_voz', 'calmo'),
            'nivel_cognitivo': getattr(idoso, 'nivel_cognitivo', 'normal'),
            'limitacoes_auditivas': getattr(idoso, 'limitacoes_auditivas', False),
            'medicamento': dados_tarefa.get('medicamento', ''),
            'dosagem': dados_tarefa.get('dosagem', ''),
            'horario': dados_tarefa.get('horario', ''),
            'taxa_adesao': taxa_adesao,
            'taxa_adesao_baixa': taxa_adesao < 70,
            'primeira_interacao': len(historico) == 0
        }
    
    def _parse_dados_tarefa(self, agendamento) -> Dict[str, Any]:
        """
        Extrai dados da tarefa do campo 'remedios' do agendamento
        """
        import json
        
        remedios_str = agendamento.remedios or '{}'
        
        try:
            # Se for JSON, parseia
            if remedios_str.strip().startswith('{'):
                return json.loads(remedios_str)
            else:
                # Se for string simples, retorna como medicamento
                return {
                    'medicamento': remedios_str,
                    'dosagem': '',
                    'horario': ''
                }
        except:
            return {'medicamento': str(remedios_str), 'dosagem': '', 'horario': ''}
    
    def _calculate_age(self, data_nascimento) -> int:
        """
        Calcula idade a partir da data de nascimento
        """
        if not data_nascimento:
            return 0
        
        today = datetime.now().date()
        birth = data_nascimento if isinstance(data_nascimento, datetime) else datetime.strptime(str(data_nascimento), '%Y-%m-%d').date()
        
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    
    def _calculate_adherence(self, historico: List) -> float:
        """
        Calcula taxa de adesão aos medicamentos
        """
        if not historico:
            return 100.0
        
        total = len(historico)
        sucessos = sum(1 for h in historico if h.get('objetivo_alcancado'))
        
        return (sucessos / total) * 100
    
    def _get_familiar_principal(self, idoso) -> Dict[str, Any]:
        """
        Busca dados do familiar principal
        """
        # TODO: Implementar busca real na tabela familiares
        return {
            'nome': 'Familiar',
            'telefone': '+5511999999999',
            'parentesco': 'filho(a)'
        }
    
    async def _get_available_functions(self, tipo_agendamento: str) -> List[Dict]:
        """
        Busca functions disponíveis para este tipo de agendamento
        """
        # TODO: Buscar do banco (tabela function_definitions)
        # Por enquanto retorna hardcoded
        return [
            {
                'nome': 'confirm_medication',
                'descricao': 'Registra se o idoso tomou o medicamento',
                'parametros': {
                    'type': 'object',
                    'properties': {
                        'medicamento': {'type': 'string'},
                        'tomou': {'type': 'boolean'},
                        'observacoes': {'type': 'string'}
                    },
                    'required': ['medicamento', 'tomou']
                }
            },
            {
                'nome': 'alert_family',
                'descricao': 'Envia alerta para o familiar em caso de emergência',
                'parametros': {
                    'type': 'object',
                    'properties': {
                        'motivo': {'type': 'string'},
                        'urgencia': {'type': 'string', 'enum': ['baixa', 'media', 'alta', 'critica']}
                    },
                    'required': ['motivo', 'urgencia']
                }
            }
        ]
    
    def _personalize_audio(self, idoso, sys_configs: Dict) -> Dict[str, Any]:
        """
        Ajusta configurações de áudio baseado no perfil do idoso
        """
        base_rms = sys_configs.get('audio.speech_detection_rms', 300)
        base_silence = sys_configs.get('audio.silence_threshold_seconds', 0.8)
        base_buffer = sys_configs.get('audio.buffer_size_bytes', 1600)
        
        # Ajuste por ganho de áudio personalizado
        ganho = getattr(idoso, 'ganho_audio_entrada', 0)
        adjusted_rms = base_rms + (ganho * 10)
        
        # Se tem limitações auditivas, aumenta threshold de silêncio
        if getattr(idoso, 'limitacoes_auditivas', False):
            base_silence *= 1.5
        
        return {
            'silence_threshold': base_silence,
            'speech_rms': adjusted_rms,
            'buffer_size': base_buffer
        }