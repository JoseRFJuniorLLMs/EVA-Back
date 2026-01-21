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
    device_token: Optional[str] = None  # 26/12/2025 update para token firebase

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
    medicamentos_atuais: Optional[Any] = None
    device_token: Optional[str] = None  # 26/12/2025 update para token firebase

class IdosoResponse(IdosoBase):
    id: int
    agendamentos_pendentes: int = 0
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FamiliarBase(BaseModel):
    nome: str
    parentesco: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    foto_url: Optional[str] = None
    is_responsavel: bool = False

class FamiliarCreate(FamiliarBase):
    parent_id: Optional[int] = None  # For hierarchical family tree

class FamiliarResponse(FamiliarBase):
    id: int
    idoso_id: int
    parent_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: datetime
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
    principio_ativo: Optional[str] = None
    forma: Optional[str] = None
    observacoes: Optional[str] = None
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
    idoso_nome: Optional[str] = None
    foto_url: Optional[str] = None
    telefone: Optional[str] = None
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
    idoso_nome: Optional[str] = None
    foto_url: Optional[str] = None
    telefone: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class InsightGenerate(BaseModel):
    idoso_id: int

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

# --- Assinaturas (Subscription System) ---
class SubscriptionBase(BaseModel):
    entidade_nome: str
    plano_id: str
    limite_minutos: int = 1000

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    plano_id: Optional[str] = None
    limite_minutos: Optional[int] = None
    status: Optional[str] = None
    data_proxima_cobranca: Optional[date] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    status: str
    minutos_consumidos: int
    data_proxima_cobranca: Optional[date]
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- IA Avançada (Advanced AI) ---
class PadraoComportamentoResponse(BaseModel):
    id: int
    idoso_id: int
    tipo_padrao: str
    descricao: str
    frequencia: Optional[str]
    confianca: Optional[Decimal]
    primeira_deteccao: Optional[datetime]
    ultima_confirmacao: Optional[datetime]
    ocorrencias: int
    dados_estatisticos: Optional[Dict[str, Any]]
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PredicaoEmergenciaResponse(BaseModel):
    id: int
    idoso_id: int
    tipo_emergencia: str
    probabilidade: Decimal
    nivel_risco: str
    fatores_contribuintes: Dict[str, Any]
    sinais_detectados: Optional[Dict[str, Any]]
    recomendacoes: Optional[Dict[str, Any]]
    data_predicao: datetime
    validade_ate: Optional[datetime]
    confirmada: bool
    data_confirmacao: Optional[datetime]
    falso_positivo: bool
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PredicaoEmergenciaCreate(BaseModel):
    idoso_id: int
    tipo_emergencia: str
    probabilidade: Decimal
    nivel_risco: str
    fatores_contribuintes: Dict[str, Any]
    sinais_detectados: Optional[Dict[str, Any]] = None
    recomendacoes: Optional[Dict[str, Any]] = None
    validade_ate: Optional[datetime] = None

class EmocaoAnaliseRequest(BaseModel):
    ligacao_id: int

class EmocaoHistoricoResponse(BaseModel):
    id: int
    data: datetime
    emocao: str
    intensidade: float
    sentimento_original: Optional[str]


# =====================================================
# HEALTH DATA SCHEMAS (Sistema de Monitoramento de Saúde)
# =====================================================

# --- Usuários ---
class UsuarioBase(BaseModel):
    nome: str
    email: Optional[str] = None
    matricula: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    matricula: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Atividade Física ---
class AtividadeCreate(BaseModel):
    cliente_id: int
    passos: Optional[int] = 0
    calorias_queimadas: Optional[Decimal] = None
    distancia_km: Optional[Decimal] = None
    andares_subidos: Optional[int] = None
    velocidade_media: Optional[Decimal] = None
    cadencia_pedalada: Optional[int] = None
    potencia_watts: Optional[int] = None
    tipo_exercicio: Optional[str] = None
    timestamp_coleta: datetime

class AtividadeResponse(AtividadeCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AtividadeBulkCreate(BaseModel):
    registros: List[AtividadeCreate]
    
    class Config:
        max_items = 100  # Limite para evitar timeout


# --- Sinais Vitais ---
class SinaisVitaisHealthCreate(BaseModel):
    cliente_id: int
    bpm: Optional[int] = None
    bpm_repouso: Optional[int] = None
    pressao_sistolica: Optional[int] = None
    pressao_diastolica: Optional[int] = None
    spo2: Optional[Decimal] = None
    glicose_sangue: Optional[Decimal] = None
    frequencia_respiratoria: Optional[int] = None
    timestamp_coleta: datetime
    
    # Validações
    @classmethod
    def validate_spo2(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('SpO2 deve estar entre 0 e 100')
        return v
    
    @classmethod
    def validate_bpm(cls, v):
        if v is not None and (v < 30 or v > 250):
            raise ValueError('BPM deve estar entre 30 e 250')
        return v
    
    @classmethod
    def validate_pressao_sistolica(cls, v):
        if v is not None and (v < 50 or v > 250):
            raise ValueError('Pressão sistólica deve estar entre 50 e 250')
        return v
    
    @classmethod
    def validate_pressao_diastolica(cls, v):
        if v is not None and (v < 30 or v > 150):
            raise ValueError('Pressão diastólica deve estar entre 30 e 150')
        return v

class SinaisVitaisHealthResponse(SinaisVitaisHealthCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SinaisVitaisHealthBulkCreate(BaseModel):
    registros: List[SinaisVitaisHealthCreate]
    
    class Config:
        max_items = 100


# --- Sono ---
class SonoCreate(BaseModel):
    cliente_id: int
    duracao_total_minutos: Optional[int] = None
    estagio_leve_minutos: Optional[int] = None
    estagio_profundo_minutos: Optional[int] = None
    estagio_rem_minutos: Optional[int] = None
    tempo_acordado_minutos: Optional[int] = None
    timestamp_inicio: Optional[datetime] = None
    timestamp_fim: Optional[datetime] = None

class SonoResponse(SonoCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Medição Corporal ---
class MedicaoCorporalCreate(BaseModel):
    cliente_id: int
    peso_kg: Optional[Decimal] = None
    altura_cm: Optional[Decimal] = None
    perc_gordura_corporal: Optional[Decimal] = None
    massa_ossea_kg: Optional[Decimal] = None
    massa_magra_kg: Optional[Decimal] = None
    circunferencia_cintura_cm: Optional[Decimal] = None
    circunferencia_quadril_cm: Optional[Decimal] = None
    timestamp_coleta: datetime
    
    # Validações
    @classmethod
    def validate_peso_kg(cls, v):
        if v is not None and (v < 20 or v > 300):
            raise ValueError('Peso deve estar entre 20 e 300 kg')
        return v
    
    @classmethod
    def validate_altura_cm(cls, v):
        if v is not None and (v < 50 or v > 250):
            raise ValueError('Altura deve estar entre 50 e 250 cm')
        return v

class MedicaoCorporalResponse(MedicaoCorporalCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Nutrição ---
class NutricaoCreate(BaseModel):
    cliente_id: int
    ingestao_agua_ml: Optional[int] = None
    calorias_consumidas: Optional[int] = None
    proteinas_g: Optional[Decimal] = None
    carboidratos_g: Optional[Decimal] = None
    gorduras_g: Optional[Decimal] = None
    vitaminas_json: Optional[Dict[str, Any]] = None
    timestamp_coleta: datetime

class NutricaoResponse(NutricaoCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Ciclo Menstrual ---
class CicloMenstrualCreate(BaseModel):
    cliente_id: int
    data_menstruacao: Optional[date] = None
    teste_ovulacao: Optional[str] = None
    muco_cervical: Optional[str] = None
    atividade_sexual: Optional[bool] = None
    sintomas_json: Optional[Dict[str, Any]] = None
    timestamp_coleta: datetime

class CicloMenstrualResponse(CicloMenstrualCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Dashboard e Relatórios ---
class DashboardResumoResponse(BaseModel):
    """Resumo diário para dashboard"""
    cliente_id: int
    data: date
    passos_hoje: Optional[int] = 0
    ultimo_bpm: Optional[int] = None
    ultima_pressao: Optional[str] = None  # "120/80"
    horas_sono_ontem: Optional[float] = None
    calorias_consumidas_hoje: Optional[int] = None
    agua_ml_hoje: Optional[int] = None

class RelatorioMensalResponse(BaseModel):
    """Relatório mensal para análise de tendências"""
    cliente_id: int
    mes: int
    ano: int
    total_passos: int
    media_bpm: Optional[float] = None
    media_horas_sono: Optional[float] = None
    peso_inicial: Optional[Decimal] = None
    peso_final: Optional[Decimal] = None
    total_atividades: int


# =====================================================
# CUIDADORES SCHEMAS
# =====================================================

from pydantic import EmailStr, Field

class CuidadorBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$')
    telefone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    parentesco: Optional[str] = Field(None, max_length=100)
    tipo_cuidador: str = Field('familiar', pattern='^(familiar|profissional|voluntario)$')
    eh_responsavel: bool = False
    eh_contato_emergencia: bool = False
    observacoes: Optional[str] = None
    prioridade: int = Field(1, ge=1, le=10)
    metodo_preferido: str = Field('push', pattern='^(push|sms|email)$')

class CuidadorCreate(CuidadorBase):
    idoso_id: int = Field(..., gt=0)

class CuidadorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$')
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    parentesco: Optional[str] = None
    tipo_cuidador: Optional[str] = Field(None, pattern='^(familiar|profissional|voluntario)$')
    eh_responsavel: Optional[bool] = None
    eh_contato_emergencia: Optional[bool] = None
    device_token: Optional[str] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None
    prioridade: Optional[int] = Field(None, ge=1, le=10)
    metodo_preferido: Optional[str] = Field(None, pattern='^(push|sms|email)$')

class CuidadorResponse(CuidadorBase):
    id: int
    idoso_id: int
    device_token: Optional[str] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    model_config = ConfigDict(from_attributes=True)
