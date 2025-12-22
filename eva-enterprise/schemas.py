from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Common ---
class MessageResponse(BaseModel):
    message: str

# --- Configs & System ---
class ConfigCreate(BaseModel):
    chave: str
    valor: str
    tipo: str
    categoria: str

class ConfigUpdate(BaseModel):
    valor: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None

class ConfigResponse(ConfigCreate):
    id: int
    
    class Config:
        from_attributes = True

class PromptCreate(BaseModel):
    nome: str
    template: str
    versao: str
    ativo: bool = True

class PromptResponse(PromptCreate):
    id: int
    class Config:
        from_attributes = True

class FuncaoCreate(BaseModel):
    nome: str
    descricao: str
    parameters: Dict[str, Any]
    tipo_tarefa: str

class FuncaoResponse(FuncaoCreate):
    id: int
    class Config:
        from_attributes = True

class CircuitBreakerResponse(BaseModel):
    id: int
    service_name: str
    state: str
    failure_count: int
    last_failure_time: Optional[datetime]
    class Config:
        from_attributes = True

class RateLimitUpdate(BaseModel):
    limit_count: Optional[int]
    interval_seconds: Optional[int]

class RateLimitResponse(BaseModel):
    id: int
    endpoint: str
    limit_count: int
    interval_seconds: int
    class Config:
        from_attributes = True

# --- Idosos & Related ---
class IdosoBase(BaseModel):
    nome: str
    telefone: str
    cpf: Optional[str] = None
    data_nascimento: Optional[str] = None
    foto_url: Optional[str] = None
    endereco: Optional[str] = None
    condicoes_medicas: Optional[str] = None
    medicamentos_regulares: Optional[str] = None
    sentimento: Optional[str] = 'neutro'
    nivel_cognitivo: Optional[str] = 'normal'
    mobilidade: Optional[str] = 'independente'

class IdosoCreate(IdosoBase):
    pass

class IdosoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[str] = None
    foto_url: Optional[str] = None
    endereco: Optional[str] = None
    condicoes_medicas: Optional[str] = None
    medicamentos_regulares: Optional[str] = None
    sentimento: Optional[str] = None
    nivel_cognitivo: Optional[str] = None
    mobilidade: Optional[str] = None

class IdosoResponse(IdosoBase):
    id: int
    agendamentos_pendentes: int = 0
    criado_em: datetime
    
    # Computed field for frontend compatibility (foto is alias for foto_url)
    @property
    def foto(self) -> Optional[str]:
        return self.foto_url
    
    class Config:
        from_attributes = True

class FamiliarBase(BaseModel):
    nome: str
    parentesco: Optional[str] = None
    telefone: str
    email: Optional[str] = None
    eh_responsavel: bool = False

class FamiliarCreate(FamiliarBase):
    pass

class FamiliarUpdate(BaseModel):
    nome: Optional[str] = None
    parentesco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    eh_responsavel: Optional[bool] = None

class FamiliarResponse(FamiliarBase):
    id: int
    idoso_id: int
    class Config:
        from_attributes = True

class LegadoDigitalCreate(BaseModel):
    titulo: Optional[str] = None
    tipo_midia: Optional[str] = None
    url_arquivo: Optional[str] = None
    descricao: Optional[str] = None

class LegadoDigitalResponse(LegadoDigitalCreate):
    id: int
    idoso_id: int
    criado_em: datetime
    class Config:
        from_attributes = True

# --- Medicamentos & Saude ---
class MedicamentoBase(BaseModel):
    nome: str
    dosagem: Optional[str] = None
    horarios: Optional[List[str]] = None
    ativo: bool = True

class MedicamentoCreate(MedicamentoBase):
    idoso_id: int

class MedicamentoUpdate(BaseModel):
    nome: Optional[str] = None
    dosagem: Optional[str] = None
    horarios: Optional[List[str]] = None
    ativo: Optional[bool] = None

class MedicamentoResponse(MedicamentoBase):
    id: int
    idoso_id: int
    criado_em: datetime
    class Config:
        from_attributes = True

class SinaisVitaisCreate(BaseModel):
    idoso_id: int
    tipo: str
    valor: str
    unidade: str
    observacao: Optional[str] = None

class SinaisVitaisResponse(SinaisVitaisCreate):
    id: int
    data_medicao: datetime
    class Config:
        from_attributes = True

# --- Agendamentos & Calls ---
class AgendamentoBase(BaseModel):
    idoso_id: int
    nome_idoso: Optional[str] = None
    telefone: Optional[str] = None
    horario: datetime
    remedios: Optional[str] = None
    status: str = "pendente"

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoUpdate(BaseModel):
    horario: Optional[datetime] = None
    status: Optional[str] = None
    remedios: Optional[str] = None

class AgendamentoResponse(AgendamentoBase):
    id: int
    tentativas_realizadas: int
    proxima_tentativa: Optional[datetime]
    class Config:
        from_attributes = True

class MakeCallRequest(BaseModel):
    telephone: str

class HistoricoResponse(BaseModel):
    id: int
    agendamento_id: Optional[int]
    idoso_id: Optional[int]
    evento: str
    status: str
    detalhe: Optional[str]
    inicio: Optional[datetime]
    fim: Optional[datetime]
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    call_sid: str
    status: str

# --- Alertas & Insights ---
class AlertaCreate(BaseModel):
    tipo: str
    descricao: str
    status: str = "ativo"

class AlertaResponse(AlertaCreate):
    id: int
    criado_em: datetime
    class Config:
        from_attributes = True

class PsicologiaInsightResponse(BaseModel):
    id: int
    idoso_id: int
    conteudo: str
    data_geracao: datetime
    relevancia: int
    class Config:
        from_attributes = True

class TopicoAfetivoResponse(BaseModel):
    id: int
    idoso_id: int
    topico: str
    frequencia: int
    ultima_mencao: datetime
    class Config:
        from_attributes = True

class InsightGenerate(BaseModel):
    idoso_id: int
    contexto: Optional[str] = None

# --- Pagamentos & Audit ---
class PagamentoCreate(BaseModel):
    descricao: str
    valor: float
    metodo: str
    status: str

class PagamentoResponse(PagamentoCreate):
    id: int
    data: datetime
    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    acao: Optional[str] = None
    usuario: Optional[str] = "Sistema"
    detalhes: Optional[Dict[str, Any]] = None
    data: datetime
    class Config:
        from_attributes = True

# --- Orchestrator ---
class FlowStepCreate(BaseModel):
    delay: int
    acao: str
    vezes: int = 1
    contato: Optional[str] = None
    status: str = "Ativo"

class FlowStepResponse(FlowStepCreate):
    id: int
    flow_id: int
    class Config:
        from_attributes = True

class FlowCreate(BaseModel):
    idoso_id: int
    nome: str
    etapas: List[FlowStepCreate]

class FlowResponse(BaseModel):
    id: int
    idoso_id: int
    nome: str
    etapas: List[FlowStepResponse]
    class Config:
        from_attributes = True
