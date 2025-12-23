from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime, date
from decimal import Decimal

# --- Common ---
class MessageResponse(BaseModel):
    message: str

# --- Configs & System ---
class ConfigCreate(BaseModel):
    chave: str
    valor: str
    tipo: str
    categoria: str
    descricao: Optional[str] = None
    ativa: bool = True

class ConfigUpdate(BaseModel):
    valor: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    ativa: Optional[bool] = None

class ConfigResponse(ConfigCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PromptCreate(BaseModel):
    nome: str
    template: str
    versao: str = "v1"
    tipo: str
    ativo: bool = True
    descricao: Optional[str] = None

class PromptResponse(PromptCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FuncaoCreate(BaseModel):
    nome: str
    descricao: str
    parametros: Dict[str, Any]
    tipo_tarefa: str
    handler_path: str
    requires_confirmation: bool = False

class FuncaoResponse(FuncaoCreate):
    id: int
    ativa: bool
    model_config = ConfigDict(from_attributes=True)

class CircuitBreakerResponse(BaseModel):
    id: int
    service_name: str
    state: str
    failure_count: int
    last_failure_time: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class RateLimitResponse(BaseModel):
    id: int
    endpoint: str
    limit_count: int
    interval_seconds: int
    model_config = ConfigDict(from_attributes=True)

# --- Idosos & Related ---
class IdosoBase(BaseModel):
    nome: str
    telefone: str
    cpf: Optional[str] = None
    data_nascimento: date
    foto_url: Optional[str] = None
    condicoes_medicas: Optional[str] = None
    sentimento: Optional[str] = 'neutro'
    nivel_cognitivo: Optional[str] = 'normal'
    mobilidade: Optional[str] = 'independente'
    tom_voz: str = "amigavel"
    timezone: str = "America/Sao_Paulo"

class IdosoCreate(IdosoBase):
    pass

class IdosoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    foto_url: Optional[str] = None
    condicoes_medicas: Optional[str] = None
    sentimento: Optional[str] = None
    nivel_cognitivo: Optional[str] = None
    mobilidade: Optional[str] = None

class IdosoResponse(IdosoBase):
    id: int
    agendamentos_pendentes: int = 0
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FamiliarBase(BaseModel):
    nome: str
    parentesco: str
    telefone: str
    is_responsavel: bool = False

class FamiliarCreate(FamiliarBase):
    pass

class FamiliarResponse(FamiliarBase):
    id: int
    idoso_id: int
    model_config = ConfigDict(from_attributes=True)

class LegadoDigitalCreate(BaseModel):
    titulo: str
    tipo: str
    url_midia: str
    destinatario: Optional[str] = None

class LegadoDigitalResponse(LegadoDigitalCreate):
    id: int
    idoso_id: int
    criado_em: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Perfil e Memória ---
class PerfilClinicoBase(BaseModel):
    tipo_sanguineo: Optional[str] = None
    alergias: Optional[str] = None
    restricoes_locomocao: Optional[str] = None
    doencas_cronicas: Optional[str] = None

class PerfilClinicoResponse(PerfilClinicoBase):
    idoso_id: int
    model_config = ConfigDict(from_attributes=True)

class MemoriaBase(BaseModel):
    categoria: str
    chave: str
    valor: str
    relevancia: str = "media"

class MemoriaResponse(MemoriaBase):
    id: int
    idoso_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Medicamentos & Saude ---
class MedicamentoBase(BaseModel):
    nome: str
    dosagem: Optional[str] = None
    horarios: List[str] = []
    ativo: bool = True

class MedicamentoCreate(MedicamentoBase):
    idoso_id: int

class MedicamentoResponse(MedicamentoBase):
    id: int
    idoso_id: int
    model_config = ConfigDict(from_attributes=True)

class SinaisVitaisCreate(BaseModel):
    idoso_id: int
    tipo: str
    valor: str
    unidade: Optional[str] = None
    observacao: Optional[str] = None

class SinaisVitaisResponse(SinaisVitaisCreate):
    id: int
    data_medicao: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Agendamentos & Calls ---
class AgendamentoBase(BaseModel):
    idoso_id: int
    tipo: str
    data_hora_agendada: datetime
    status: str = "agendado"
    prioridade: str = "normal"

class AgendamentoCreate(AgendamentoBase):
    dados_tarefa: Dict[str, Any] = {}

class AgendamentoResponse(AgendamentoBase):
    id: int
    tentativas_realizadas: int
    proxima_tentativa: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class HistoricoResponse(BaseModel):
    id: int
    idoso_id: int
    agendamento_id: Optional[int]
    inicio_chamada: datetime
    fim_chamada: Optional[datetime]
    transcricao_resumo: Optional[str]
    sentimento_geral: Optional[str]
    tarefa_concluida: bool
    model_config = ConfigDict(from_attributes=True)

# --- Alertas & Insights ---
class AlertaCreate(BaseModel):
    idoso_id: int
    tipo: str
    severidade: str
    mensagem: str
    destinatarios: List[str] = []

class AlertaResponse(AlertaCreate):
    id: int
    criado_em: datetime
    resolvido: bool
    model_config = ConfigDict(from_attributes=True)

class PsicologiaInsightResponse(BaseModel):
    id: int
    idoso_id: int
    tipo: str
    mensagem: str
    data_insight: datetime
    relevancia: str
    model_config = ConfigDict(from_attributes=True)

class TopicoAfetivoResponse(BaseModel):
    id: int
    idoso_id: int
    topico: str
    frequencia: int
    sentimento_associado: Optional[str] = None
    ultima_mencao: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Faturamento ---
class AssinaturaResponse(BaseModel):
    id: int
    entidade_nome: str
    status: str
    plano_id: str
    data_proxima_cobranca: Optional[date]
    limite_minutos: int
    minutos_consumidos: int
    model_config = ConfigDict(from_attributes=True)

class ConsumoResponse(BaseModel):
    idoso_id: int
    mes_referencia: int
    ano_referencia: int
    total_tokens: int
    total_minutos: int
    custo_total_estimado: Decimal
    model_config = ConfigDict(from_attributes=True)

# --- Orchestrator ---
class ProtocoloEtapaCreate(BaseModel):
    ordem: int
    acao: str
    delay_minutos: int = 5
    tentativas: int = 1
    contato_alvo: Optional[str] = None

class ProtocoloEtapaResponse(ProtocoloEtapaCreate):
    id: int
    protocolo_id: int
    model_config = ConfigDict(from_attributes=True)

class ProtocoloCreate(BaseModel):
    idoso_id: int
    nome: str
    etapas: List[ProtocoloEtapaCreate]

class ProtocoloResponse(BaseModel):
    id: int
    idoso_id: int
    nome: str
    ativo: bool
    etapas: List[ProtocoloEtapaResponse]
    model_config = ConfigDict(from_attributes=True)
