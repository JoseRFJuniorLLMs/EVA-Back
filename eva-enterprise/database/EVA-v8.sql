--
-- PostgreSQL database dump
--

\restrict B6Chw9QPdLa4Oz2wzJ5bytSeAmq9JhuW5qHle8RE1gSjx1Pn7NFnYyCDwBZLt6X

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.0

-- Started on 2025-12-28 10:41:01

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 279 (class 1255 OID 17010)
-- Name: calcular_proxima_tentativa(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calcular_proxima_tentativa(p_agendamento_id integer, p_intervalo_minutos integer DEFAULT 15) RETURNS timestamp without time zone
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_proxima TIMESTAMP;
BEGIN
    v_proxima := CURRENT_TIMESTAMP + (p_intervalo_minutos || ' minutes')::INTERVAL;
    
    UPDATE agendamentos
    SET proxima_tentativa = v_proxima,
        status = 'aguardando_retry'
    WHERE id = p_agendamento_id;
    
    RETURN v_proxima;
END;
$$;


ALTER FUNCTION public.calcular_proxima_tentativa(p_agendamento_id integer, p_intervalo_minutos integer) OWNER TO postgres;

--
-- TOC entry 280 (class 1255 OID 17011)
-- Name: get_config(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_config(p_chave character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_valor TEXT;
BEGIN
    SELECT valor INTO v_valor
    FROM configuracoes_sistema
    WHERE chave = p_chave AND ativa = true
    LIMIT 1;
    
    RETURN v_valor;
END;
$$;


ALTER FUNCTION public.get_config(p_chave character varying) OWNER TO postgres;

--
-- TOC entry 281 (class 1255 OID 17012)
-- Name: get_config_int(character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_config_int(p_chave character varying, p_default integer DEFAULT 0) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_valor TEXT;
BEGIN
    v_valor := get_config(p_chave);
    IF v_valor IS NULL THEN
        RETURN p_default;
    END IF;
    RETURN v_valor::INTEGER;
EXCEPTION WHEN OTHERS THEN
    RETURN p_default;
END;
$$;


ALTER FUNCTION public.get_config_int(p_chave character varying, p_default integer) OWNER TO postgres;

--
-- TOC entry 278 (class 1255 OID 16592)
-- Name: update_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_timestamp() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16724)
-- Name: agendamentos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agendamentos (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    tipo character varying(50) NOT NULL,
    data_hora_agendada timestamp without time zone NOT NULL,
    data_hora_realizada timestamp without time zone,
    max_retries integer DEFAULT 3,
    retry_interval_minutes integer DEFAULT 15,
    tentativas_realizadas integer DEFAULT 0,
    proxima_tentativa timestamp without time zone,
    escalation_policy character varying(50) DEFAULT 'alert_family'::character varying,
    status character varying(50) DEFAULT 'agendado'::character varying,
    gemini_session_handle character varying(255),
    ultima_interacao_estado jsonb,
    session_expires_at timestamp without time zone,
    dados_tarefa jsonb DEFAULT '{}'::jsonb NOT NULL,
    prioridade character varying(10) DEFAULT 'normal'::character varying,
    criado_por character varying(100) DEFAULT 'sistema'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    telefone character varying,
    nome_idoso character varying,
    horario timestamp without time zone,
    remedios text,
    medicamento_tomado boolean,
    medicamento_confirmado_em timestamp without time zone,
    ultima_tentativa timestamp without time zone,
    CONSTRAINT agendamentos_escalation_policy_check CHECK (((escalation_policy)::text = ANY ((ARRAY['alert_family'::character varying, 'emergency_contact'::character varying, 'none'::character varying])::text[]))),
    CONSTRAINT agendamentos_prioridade_check CHECK (((prioridade)::text = ANY ((ARRAY['alta'::character varying, 'normal'::character varying, 'baixa'::character varying])::text[]))),
    CONSTRAINT agendamentos_status_check CHECK (((status)::text = ANY ((ARRAY['agendado'::character varying, 'em_andamento'::character varying, 'concluido'::character varying, 'falhou'::character varying, 'aguardando_retry'::character varying, 'falhou_definitivamente'::character varying, 'cancelado'::character varying])::text[]))),
    CONSTRAINT agendamentos_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['lembrete_medicamento'::character varying, 'check_bem_estar'::character varying, 'acompanhamento_pos_consulta'::character varying, 'atividade_fisica'::character varying])::text[])))
);


ALTER TABLE public.agendamentos OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16723)
-- Name: agendamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agendamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agendamentos_id_seq OWNER TO postgres;

--
-- TOC entry 4464 (class 0 OID 0)
-- Dependencies: 229
-- Name: agendamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agendamentos_id_seq OWNED BY public.agendamentos.id;


--
-- TOC entry 234 (class 1259 OID 16800)
-- Name: alertas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alertas (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    ligacao_id integer,
    tipo character varying(100) NOT NULL,
    severidade character varying(50) NOT NULL,
    mensagem text NOT NULL,
    contexto_adicional jsonb DEFAULT '{}'::jsonb,
    destinatarios jsonb NOT NULL,
    enviado boolean DEFAULT false,
    data_envio timestamp without time zone,
    visualizado boolean DEFAULT false,
    data_visualizacao timestamp without time zone,
    resolvido boolean DEFAULT false,
    data_resolucao timestamp without time zone,
    resolucao_nota text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    descricao text,
    status character varying DEFAULT 'ativo'::character varying,
    CONSTRAINT alertas_severidade_check CHECK (((severidade)::text = ANY ((ARRAY['baixa'::character varying, 'aviso'::character varying, 'alta'::character varying, 'critica'::character varying])::text[]))),
    CONSTRAINT alertas_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['dose_esquecida'::character varying, 'efeito_colateral'::character varying, 'queda'::character varying, 'confusao_mental'::character varying, 'tristeza_profunda'::character varying, 'dor_intensa'::character varying, 'nao_atende_telefone'::character varying, 'alerta_ia'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.alertas OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16799)
-- Name: alertas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alertas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alertas_id_seq OWNER TO postgres;

--
-- TOC entry 4465 (class 0 OID 0)
-- Dependencies: 233
-- Name: alertas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alertas_id_seq OWNED BY public.alertas.id;


--
-- TOC entry 245 (class 1259 OID 16941)
-- Name: assinaturas_entidade; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assinaturas_entidade (
    id integer NOT NULL,
    entidade_nome character varying(255) NOT NULL,
    status character varying(50) DEFAULT 'ativo'::character varying,
    plano_id character varying(50) NOT NULL,
    data_proxima_cobranca date,
    limite_minutos integer DEFAULT 1000,
    minutos_consumidos integer DEFAULT 0,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT assinaturas_entidade_status_check CHECK (((status)::text = ANY ((ARRAY['ativo'::character varying, 'cancelado'::character varying, 'pendente'::character varying, 'suspenso'::character varying])::text[])))
);


ALTER TABLE public.assinaturas_entidade OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 16940)
-- Name: assinaturas_entidade_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.assinaturas_entidade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assinaturas_entidade_id_seq OWNER TO postgres;

--
-- TOC entry 4466 (class 0 OID 0)
-- Dependencies: 244
-- Name: assinaturas_entidade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.assinaturas_entidade_id_seq OWNED BY public.assinaturas_entidade.id;


--
-- TOC entry 249 (class 1259 OID 16977)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    usuario_email character varying(255),
    acao character varying(100) NOT NULL,
    recurso character varying(255),
    detalhes text,
    ip_address character varying(45),
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usuario character varying,
    data timestamp without time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 16976)
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4467 (class 0 OID 0)
-- Dependencies: 248
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- TOC entry 269 (class 1259 OID 17154)
-- Name: circuit_breaker_states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.circuit_breaker_states (
    id integer NOT NULL,
    service_name character varying,
    state character varying DEFAULT 'closed'::character varying,
    failure_count integer DEFAULT 0,
    last_failure_time timestamp without time zone
);


ALTER TABLE public.circuit_breaker_states OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 17153)
-- Name: circuit_breaker_states_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.circuit_breaker_states_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.circuit_breaker_states_id_seq OWNER TO postgres;

--
-- TOC entry 4468 (class 0 OID 0)
-- Dependencies: 268
-- Name: circuit_breaker_states_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.circuit_breaker_states_id_seq OWNED BY public.circuit_breaker_states.id;


--
-- TOC entry 220 (class 1259 OID 16570)
-- Name: configuracoes_sistema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracoes_sistema (
    id integer NOT NULL,
    chave character varying(255) NOT NULL,
    valor text NOT NULL,
    tipo character varying(50) NOT NULL,
    categoria character varying(100) NOT NULL,
    descricao text,
    ativa boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_chave_formato CHECK (((chave)::text ~* '^[a-z0-9_.]+$'::text)),
    CONSTRAINT configuracoes_sistema_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['string'::character varying, 'integer'::character varying, 'float'::character varying, 'boolean'::character varying, 'json'::character varying])::text[])))
);


ALTER TABLE public.configuracoes_sistema OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16569)
-- Name: configuracoes_sistema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.configuracoes_sistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.configuracoes_sistema_id_seq OWNER TO postgres;

--
-- TOC entry 4469 (class 0 OID 0)
-- Dependencies: 219
-- Name: configuracoes_sistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.configuracoes_sistema_id_seq OWNED BY public.configuracoes_sistema.id;


--
-- TOC entry 273 (class 1259 OID 17183)
-- Name: familiares; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.familiares (
    id integer NOT NULL,
    nome character varying NOT NULL,
    parentesco character varying,
    telefone character varying NOT NULL,
    email character varying,
    eh_responsavel boolean DEFAULT false,
    idoso_id integer,
    criado_em timestamp without time zone DEFAULT now()
);


ALTER TABLE public.familiares OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 17182)
-- Name: familiares_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.familiares_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.familiares_id_seq OWNER TO postgres;

--
-- TOC entry 4470 (class 0 OID 0)
-- Dependencies: 272
-- Name: familiares_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.familiares_id_seq OWNED BY public.familiares.id;


--
-- TOC entry 247 (class 1259 OID 16958)
-- Name: faturamento_consumo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faturamento_consumo (
    id integer NOT NULL,
    idoso_id integer,
    mes_referencia integer NOT NULL,
    ano_referencia integer NOT NULL,
    total_tokens integer DEFAULT 0,
    total_minutos integer DEFAULT 0,
    custo_total_estimado numeric(10,2) DEFAULT 0.00,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.faturamento_consumo OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 16957)
-- Name: faturamento_consumo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.faturamento_consumo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.faturamento_consumo_id_seq OWNER TO postgres;

--
-- TOC entry 4471 (class 0 OID 0)
-- Dependencies: 246
-- Name: faturamento_consumo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.faturamento_consumo_id_seq OWNED BY public.faturamento_consumo.id;


--
-- TOC entry 267 (class 1259 OID 17142)
-- Name: funcoes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.funcoes (
    id integer NOT NULL,
    nome character varying,
    descricao character varying,
    parameters jsonb,
    tipo_tarefa character varying
);


ALTER TABLE public.funcoes OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 17141)
-- Name: funcoes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.funcoes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.funcoes_id_seq OWNER TO postgres;

--
-- TOC entry 4472 (class 0 OID 0)
-- Dependencies: 266
-- Name: funcoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.funcoes_id_seq OWNED BY public.funcoes.id;


--
-- TOC entry 224 (class 1259 OID 16621)
-- Name: function_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.function_definitions (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    descricao text NOT NULL,
    parametros jsonb NOT NULL,
    tipo_tarefa character varying(50) NOT NULL,
    handler_path character varying(255) NOT NULL,
    validations jsonb DEFAULT '{}'::jsonb,
    requires_confirmation boolean DEFAULT false,
    max_executions_per_call integer DEFAULT 1,
    ativa boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.function_definitions OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16620)
-- Name: function_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.function_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.function_definitions_id_seq OWNER TO postgres;

--
-- TOC entry 4473 (class 0 OID 0)
-- Dependencies: 223
-- Name: function_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.function_definitions_id_seq OWNED BY public.function_definitions.id;


--
-- TOC entry 275 (class 1259 OID 17202)
-- Name: historico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historico (
    id integer NOT NULL,
    agendamento_id integer,
    idoso_id integer,
    call_sid character varying,
    evento character varying DEFAULT 'Ligação Realizada'::character varying,
    status character varying,
    detalhe text,
    sentimento character varying,
    inicio timestamp without time zone,
    fim timestamp without time zone,
    criado_em timestamp without time zone DEFAULT now()
);


ALTER TABLE public.historico OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 17201)
-- Name: historico_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historico_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historico_id_seq OWNER TO postgres;

--
-- TOC entry 4474 (class 0 OID 0)
-- Dependencies: 274
-- Name: historico_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historico_id_seq OWNED BY public.historico.id;


--
-- TOC entry 232 (class 1259 OID 16762)
-- Name: historico_ligacoes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historico_ligacoes (
    id integer NOT NULL,
    agendamento_id integer NOT NULL,
    idoso_id integer NOT NULL,
    twilio_call_sid character varying(255),
    stream_sid character varying(255),
    inicio_chamada timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fim_chamada timestamp without time zone,
    duracao_segundos integer,
    modelo_utilizado character varying(100),
    voice_name character varying(50),
    config_snapshot jsonb,
    qualidade_audio character varying(50),
    interrupcoes_detectadas integer DEFAULT 0,
    latencia_media_ms integer,
    packets_perdidos integer DEFAULT 0,
    vad_false_positives integer DEFAULT 0,
    tarefa_concluida boolean DEFAULT false,
    objetivo_alcancado boolean,
    motivo_falha text,
    transcricao_completa text,
    transcricao_resumo text,
    sentimento_geral character varying(50),
    sentimento_intensidade integer,
    acoes_registradas jsonb DEFAULT '[]'::jsonb,
    tokens_gemini integer DEFAULT 0,
    minutos_twilio integer DEFAULT 0,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    analise_gemini jsonb,
    urgencia character varying(20),
    sentimento character varying(50),
    last_analysis_at timestamp without time zone,
    CONSTRAINT historico_ligacoes_qualidade_audio_check CHECK (((qualidade_audio)::text = ANY ((ARRAY['excelente'::character varying, 'boa'::character varying, 'regular'::character varying, 'ruim'::character varying])::text[]))),
    CONSTRAINT historico_ligacoes_sentimento_intensidade_check CHECK (((sentimento_intensidade >= 1) AND (sentimento_intensidade <= 10)))
);


ALTER TABLE public.historico_ligacoes OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16761)
-- Name: historico_ligacoes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historico_ligacoes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historico_ligacoes_id_seq OWNER TO postgres;

--
-- TOC entry 4475 (class 0 OID 0)
-- Dependencies: 231
-- Name: historico_ligacoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historico_ligacoes_id_seq OWNED BY public.historico_ligacoes.id;


--
-- TOC entry 226 (class 1259 OID 16647)
-- Name: idosos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.idosos (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    data_nascimento date NOT NULL,
    telefone character varying(20) NOT NULL,
    cpf character varying(14),
    foto_url text,
    intro_audio_url text,
    nivel_cognitivo character varying(50) DEFAULT 'normal'::character varying,
    limitacoes_auditivas boolean DEFAULT false,
    usa_aparelho_auditivo boolean DEFAULT false,
    limitacoes_visuais boolean DEFAULT false,
    mobilidade character varying(50) DEFAULT 'independente'::character varying,
    tom_voz character varying(50) DEFAULT 'amigavel'::character varying,
    preferencia_horario_ligacao character varying(50) DEFAULT 'manha'::character varying,
    timezone character varying(50) DEFAULT 'America/Sao_Paulo'::character varying,
    ganho_audio_entrada integer DEFAULT 0,
    ganho_audio_saida integer DEFAULT 0,
    ambiente_ruidoso boolean DEFAULT false,
    familiar_principal jsonb DEFAULT '{"nome": "", "telefone": "", "parentesco": ""}'::jsonb NOT NULL,
    contato_emergencia jsonb DEFAULT '{"nome": "", "telefone": "", "parentesco": ""}'::jsonb,
    medico_responsavel jsonb DEFAULT '{"crm": "", "nome": "", "telefone": ""}'::jsonb,
    medicamentos_atuais jsonb DEFAULT '[]'::jsonb,
    condicoes_medicas text,
    sentimento character varying(50) DEFAULT 'neutro'::character varying,
    agendamentos_pendentes integer DEFAULT 0,
    notas_gerais text,
    ativo boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    endereco character varying,
    medicamentos_regulares text,
    device_token text,
    CONSTRAINT chk_idade CHECK ((EXTRACT(year FROM age((data_nascimento)::timestamp with time zone)) >= (0)::numeric)),
    CONSTRAINT idosos_cpf_check CHECK (((cpf)::text ~* '^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$'::text)),
    CONSTRAINT idosos_ganho_audio_entrada_check CHECK (((ganho_audio_entrada >= '-5'::integer) AND (ganho_audio_entrada <= 5))),
    CONSTRAINT idosos_ganho_audio_saida_check CHECK (((ganho_audio_saida >= '-5'::integer) AND (ganho_audio_saida <= 5))),
    CONSTRAINT idosos_mobilidade_check CHECK (((mobilidade)::text = ANY ((ARRAY['independente'::character varying, 'auxiliado'::character varying, 'cadeira_rodas'::character varying, 'acamado'::character varying])::text[]))),
    CONSTRAINT idosos_nivel_cognitivo_check CHECK (((nivel_cognitivo)::text = ANY ((ARRAY['normal'::character varying, 'leve'::character varying, 'moderado'::character varying, 'severo'::character varying])::text[]))),
    CONSTRAINT idosos_preferencia_horario_ligacao_check CHECK (((preferencia_horario_ligacao)::text = ANY ((ARRAY['manha'::character varying, 'tarde'::character varying, 'noite'::character varying, 'qualquer'::character varying])::text[]))),
    CONSTRAINT idosos_sentimento_check CHECK (((sentimento)::text = ANY ((ARRAY['feliz'::character varying, 'neutro'::character varying, 'triste'::character varying, 'ansioso'::character varying, 'irritado'::character varying, 'confuso'::character varying, 'apatico'::character varying])::text[]))),
    CONSTRAINT idosos_tom_voz_check CHECK (((tom_voz)::text = ANY ((ARRAY['formal'::character varying, 'amigavel'::character varying, 'maternal'::character varying, 'jovial'::character varying])::text[])))
);


ALTER TABLE public.idosos OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16646)
-- Name: idosos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.idosos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.idosos_id_seq OWNER TO postgres;

--
-- TOC entry 4476 (class 0 OID 0)
-- Dependencies: 225
-- Name: idosos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.idosos_id_seq OWNED BY public.idosos.id;


--
-- TOC entry 255 (class 1259 OID 17014)
-- Name: idosos_legado_digital; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.idosos_legado_digital (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    tipo character varying(50) NOT NULL,
    titulo character varying(255) NOT NULL,
    url_midia text NOT NULL,
    destinatario character varying(255),
    protegido boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    tipo_midia character varying,
    url_arquivo character varying,
    descricao text,
    CONSTRAINT idosos_legado_digital_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['audio'::character varying, 'video'::character varying, 'imagem'::character varying, 'carta'::character varying])::text[])))
);


ALTER TABLE public.idosos_legado_digital OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 17013)
-- Name: idosos_legado_digital_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.idosos_legado_digital_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.idosos_legado_digital_id_seq OWNER TO postgres;

--
-- TOC entry 4477 (class 0 OID 0)
-- Dependencies: 254
-- Name: idosos_legado_digital_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.idosos_legado_digital_id_seq OWNED BY public.idosos_legado_digital.id;


--
-- TOC entry 242 (class 1259 OID 16900)
-- Name: idosos_memoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.idosos_memoria (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    categoria character varying(100) NOT NULL,
    chave character varying(255) NOT NULL,
    valor text NOT NULL,
    relevancia character varying(20) DEFAULT 'media'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT idosos_memoria_relevancia_check CHECK (((relevancia)::text = ANY ((ARRAY['baixa'::character varying, 'media'::character varying, 'alta'::character varying])::text[])))
);


ALTER TABLE public.idosos_memoria OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16899)
-- Name: idosos_memoria_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.idosos_memoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.idosos_memoria_id_seq OWNER TO postgres;

--
-- TOC entry 4478 (class 0 OID 0)
-- Dependencies: 241
-- Name: idosos_memoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.idosos_memoria_id_seq OWNED BY public.idosos_memoria.id;


--
-- TOC entry 243 (class 1259 OID 16924)
-- Name: idosos_perfil_clinico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.idosos_perfil_clinico (
    idoso_id integer NOT NULL,
    tipo_sanguineo character varying(5),
    alergias text,
    restricoes_locomocao text,
    doencas_cronicas text,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT idosos_perfil_clinico_tipo_sanguineo_check CHECK (((tipo_sanguineo)::text = ANY ((ARRAY['A+'::character varying, 'A-'::character varying, 'B+'::character varying, 'B-'::character varying, 'AB+'::character varying, 'AB-'::character varying, 'O+'::character varying, 'O-'::character varying])::text[])))
);


ALTER TABLE public.idosos_perfil_clinico OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16875)
-- Name: medicamentos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicamentos (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    nome character varying(255) NOT NULL,
    principio_ativo character varying(255),
    dosagem character varying(100),
    forma character varying(50),
    horarios jsonb DEFAULT '[]'::jsonb,
    observacoes text,
    ativo boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT medicamentos_forma_check CHECK (((forma)::text = ANY ((ARRAY['comprimido'::character varying, 'capsula'::character varying, 'liquido'::character varying, 'injetavel'::character varying, 'pomada'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.medicamentos OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16874)
-- Name: medicamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medicamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medicamentos_id_seq OWNER TO postgres;

--
-- TOC entry 4479 (class 0 OID 0)
-- Dependencies: 239
-- Name: medicamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medicamentos_id_seq OWNED BY public.medicamentos.id;


--
-- TOC entry 228 (class 1259 OID 16692)
-- Name: membros_familia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.membros_familia (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    parent_id integer,
    nome character varying(255) NOT NULL,
    parentesco character varying(100) NOT NULL,
    foto_url text,
    is_responsavel boolean DEFAULT false,
    telefone character varying(20),
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.membros_familia OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16691)
-- Name: membros_familia_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.membros_familia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.membros_familia_id_seq OWNER TO postgres;

--
-- TOC entry 4480 (class 0 OID 0)
-- Dependencies: 227
-- Name: membros_familia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.membros_familia_id_seq OWNED BY public.membros_familia.id;


--
-- TOC entry 263 (class 1259 OID 17118)
-- Name: pagamentos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pagamentos (
    id integer NOT NULL,
    descricao character varying,
    valor integer,
    metodo character varying,
    status character varying,
    data timestamp without time zone DEFAULT now()
);


ALTER TABLE public.pagamentos OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 17117)
-- Name: pagamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pagamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pagamentos_id_seq OWNER TO postgres;

--
-- TOC entry 4481 (class 0 OID 0)
-- Dependencies: 262
-- Name: pagamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pagamentos_id_seq OWNED BY public.pagamentos.id;


--
-- TOC entry 222 (class 1259 OID 16595)
-- Name: prompt_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prompt_templates (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    versao character varying(20) DEFAULT 'v1'::character varying NOT NULL,
    template text NOT NULL,
    variaveis_esperadas jsonb DEFAULT '[]'::jsonb NOT NULL,
    tipo character varying(50) NOT NULL,
    ativo boolean DEFAULT true,
    descricao text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT prompt_templates_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['system_base'::character varying, 'task_specific'::character varying, 'recovery'::character varying, 'escalation'::character varying])::text[])))
);


ALTER TABLE public.prompt_templates OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16594)
-- Name: prompt_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prompt_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prompt_templates_id_seq OWNER TO postgres;

--
-- TOC entry 4482 (class 0 OID 0)
-- Dependencies: 221
-- Name: prompt_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prompt_templates_id_seq OWNED BY public.prompt_templates.id;


--
-- TOC entry 265 (class 1259 OID 17129)
-- Name: prompts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prompts (
    id integer NOT NULL,
    nome character varying,
    template text,
    versao character varying,
    ativo boolean DEFAULT true
);


ALTER TABLE public.prompts OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 17128)
-- Name: prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prompts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prompts_id_seq OWNER TO postgres;

--
-- TOC entry 4483 (class 0 OID 0)
-- Dependencies: 264
-- Name: prompts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prompts_id_seq OWNED BY public.prompts.id;


--
-- TOC entry 238 (class 1259 OID 16854)
-- Name: protocolo_etapas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.protocolo_etapas (
    id integer NOT NULL,
    protocolo_id integer NOT NULL,
    ordem integer NOT NULL,
    acao character varying(50) NOT NULL,
    delay_minutos integer DEFAULT 5,
    tentativas integer DEFAULT 1,
    contato_alvo character varying(255),
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.protocolo_etapas OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16853)
-- Name: protocolo_etapas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.protocolo_etapas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.protocolo_etapas_id_seq OWNER TO postgres;

--
-- TOC entry 4484 (class 0 OID 0)
-- Dependencies: 237
-- Name: protocolo_etapas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.protocolo_etapas_id_seq OWNED BY public.protocolo_etapas.id;


--
-- TOC entry 236 (class 1259 OID 16836)
-- Name: protocolos_alerta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.protocolos_alerta (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    nome character varying(100) DEFAULT 'Protocolo Padrão'::character varying,
    ativo boolean DEFAULT true,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    atualizado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.protocolos_alerta OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16835)
-- Name: protocolos_alerta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.protocolos_alerta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.protocolos_alerta_id_seq OWNER TO postgres;

--
-- TOC entry 4485 (class 0 OID 0)
-- Dependencies: 235
-- Name: protocolos_alerta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.protocolos_alerta_id_seq OWNED BY public.protocolos_alerta.id;


--
-- TOC entry 257 (class 1259 OID 17036)
-- Name: psicologia_insights; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.psicologia_insights (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    tipo character varying(50) NOT NULL,
    mensagem text NOT NULL,
    data_insight timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    relevancia character varying(20) DEFAULT 'media'::character varying,
    conteudo text,
    data_geracao timestamp without time zone DEFAULT now(),
    CONSTRAINT psicologia_insights_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['positivo'::character varying, 'alerta'::character varying, 'vincular'::character varying, 'evolucao'::character varying])::text[])))
);


ALTER TABLE public.psicologia_insights OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 17035)
-- Name: psicologia_insights_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.psicologia_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.psicologia_insights_id_seq OWNER TO postgres;

--
-- TOC entry 4486 (class 0 OID 0)
-- Dependencies: 256
-- Name: psicologia_insights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.psicologia_insights_id_seq OWNED BY public.psicologia_insights.id;


--
-- TOC entry 271 (class 1259 OID 17168)
-- Name: rate_limits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rate_limits (
    id integer NOT NULL,
    endpoint character varying,
    limit_count integer DEFAULT 100,
    interval_seconds integer DEFAULT 60
);


ALTER TABLE public.rate_limits OWNER TO postgres;

--
-- TOC entry 270 (class 1259 OID 17167)
-- Name: rate_limits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rate_limits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rate_limits_id_seq OWNER TO postgres;

--
-- TOC entry 4487 (class 0 OID 0)
-- Dependencies: 270
-- Name: rate_limits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rate_limits_id_seq OWNED BY public.rate_limits.id;


--
-- TOC entry 261 (class 1259 OID 17074)
-- Name: sinais_vitais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sinais_vitais (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    tipo character varying(100) NOT NULL,
    valor character varying(50) NOT NULL,
    unidade character varying(20),
    metodo character varying(50) DEFAULT 'voz_ia'::character varying,
    data_medicao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    observacao text
);


ALTER TABLE public.sinais_vitais OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 17073)
-- Name: sinais_vitais_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sinais_vitais_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sinais_vitais_id_seq OWNER TO postgres;

--
-- TOC entry 4488 (class 0 OID 0)
-- Dependencies: 260
-- Name: sinais_vitais_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sinais_vitais_id_seq OWNED BY public.sinais_vitais.id;


--
-- TOC entry 277 (class 1259 OID 24761)
-- Name: timeline; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.timeline (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    tipo character varying(50) NOT NULL,
    subtipo character varying(50),
    titulo character varying(255) NOT NULL,
    descricao text,
    data timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.timeline OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 24760)
-- Name: timeline_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.timeline_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.timeline_id_seq OWNER TO postgres;

--
-- TOC entry 4489 (class 0 OID 0)
-- Dependencies: 276
-- Name: timeline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.timeline_id_seq OWNED BY public.timeline.id;


--
-- TOC entry 259 (class 1259 OID 17057)
-- Name: topicos_afetivos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.topicos_afetivos (
    id integer NOT NULL,
    idoso_id integer NOT NULL,
    topico character varying(100) NOT NULL,
    frequencia integer DEFAULT 1,
    sentimento_associado character varying(50),
    ultima_mencao timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.topicos_afetivos OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 17056)
-- Name: topicos_afetivos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.topicos_afetivos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.topicos_afetivos_id_seq OWNER TO postgres;

--
-- TOC entry 4490 (class 0 OID 0)
-- Dependencies: 258
-- Name: topicos_afetivos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.topicos_afetivos_id_seq OWNED BY public.topicos_afetivos.id;


--
-- TOC entry 252 (class 1259 OID 17000)
-- Name: v_alertas_pendentes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_alertas_pendentes AS
 SELECT a.id,
    a.idoso_id,
    i.nome AS idoso_nome,
    a.tipo,
    a.severidade,
    a.mensagem,
    a.criado_em,
    (EXTRACT(epoch FROM (CURRENT_TIMESTAMP - (a.criado_em)::timestamp with time zone)) / (3600)::numeric) AS horas_aberto,
    a.enviado,
    a.visualizado
   FROM (public.alertas a
     JOIN public.idosos i ON ((a.idoso_id = i.id)))
  WHERE (NOT a.resolvido)
  ORDER BY
        CASE a.severidade
            WHEN 'critica'::text THEN 1
            WHEN 'alta'::text THEN 2
            WHEN 'aviso'::text THEN 3
            WHEN 'baixa'::text THEN 4
            ELSE NULL::integer
        END, a.criado_em;


ALTER VIEW public.v_alertas_pendentes OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 17005)
-- Name: v_metricas_qualidade; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_metricas_qualidade AS
 SELECT date(inicio_chamada) AS data,
    count(*) AS total_ligacoes,
    avg(duracao_segundos) AS duracao_media_seg,
    avg(latencia_media_ms) AS latencia_media_ms,
    avg(interrupcoes_detectadas) AS interrupcoes_media,
    avg(vad_false_positives) AS falsos_positivos_media,
    count(
        CASE
            WHEN ((qualidade_audio)::text = ANY ((ARRAY['excelente'::character varying, 'boa'::character varying])::text[])) THEN 1
            ELSE NULL::integer
        END) AS ligacoes_boa_qualidade,
    round(((100.0 * (count(
        CASE
            WHEN ((qualidade_audio)::text = ANY ((ARRAY['excelente'::character varying, 'boa'::character varying])::text[])) THEN 1
            ELSE NULL::integer
        END))::numeric) / (count(*))::numeric), 2) AS pct_boa_qualidade
   FROM public.historico_ligacoes h
  WHERE (fim_chamada IS NOT NULL)
  GROUP BY (date(inicio_chamada))
  ORDER BY (date(inicio_chamada)) DESC;


ALTER VIEW public.v_metricas_qualidade OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 16990)
-- Name: v_proximas_ligacoes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_proximas_ligacoes AS
 SELECT a.id,
    a.data_hora_agendada,
    a.tipo,
    a.status,
    a.tentativas_realizadas,
    i.nome AS idoso_nome,
    i.telefone,
    i.timezone,
    EXTRACT(year FROM age((i.data_nascimento)::timestamp with time zone)) AS idade,
    i.limitacoes_auditivas,
    i.usa_aparelho_auditivo
   FROM (public.agendamentos a
     JOIN public.idosos i ON ((a.idoso_id = i.id)))
  WHERE (((a.status)::text = ANY ((ARRAY['agendado'::character varying, 'aguardando_retry'::character varying])::text[])) AND (a.data_hora_agendada >= CURRENT_TIMESTAMP) AND (i.ativo = true))
  ORDER BY a.data_hora_agendada;


ALTER VIEW public.v_proximas_ligacoes OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 16995)
-- Name: v_taxa_adesao_idoso; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_taxa_adesao_idoso AS
 SELECT i.id AS idoso_id,
    i.nome,
    count(h.id) AS total_ligacoes,
    count(
        CASE
            WHEN h.tarefa_concluida THEN 1
            ELSE NULL::integer
        END) AS ligacoes_bem_sucedidas,
    round(((100.0 * (count(
        CASE
            WHEN h.tarefa_concluida THEN 1
            ELSE NULL::integer
        END))::numeric) / (NULLIF(count(h.id), 0))::numeric), 2) AS taxa_adesao_pct,
    max(h.inicio_chamada) AS ultima_ligacao
   FROM (public.idosos i
     LEFT JOIN public.historico_ligacoes h ON ((i.id = h.idoso_id)))
  WHERE (i.ativo = true)
  GROUP BY i.id, i.nome;


ALTER VIEW public.v_taxa_adesao_idoso OWNER TO postgres;

--
-- TOC entry 3998 (class 2604 OID 16727)
-- Name: agendamentos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agendamentos ALTER COLUMN id SET DEFAULT nextval('public.agendamentos_id_seq'::regclass);


--
-- TOC entry 4019 (class 2604 OID 16803)
-- Name: alertas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas ALTER COLUMN id SET DEFAULT nextval('public.alertas_id_seq'::regclass);


--
-- TOC entry 4046 (class 2604 OID 16944)
-- Name: assinaturas_entidade id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assinaturas_entidade ALTER COLUMN id SET DEFAULT nextval('public.assinaturas_entidade_id_seq'::regclass);


--
-- TOC entry 4057 (class 2604 OID 16980)
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- TOC entry 4078 (class 2604 OID 17157)
-- Name: circuit_breaker_states id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_breaker_states ALTER COLUMN id SET DEFAULT nextval('public.circuit_breaker_states_id_seq'::regclass);


--
-- TOC entry 3956 (class 2604 OID 16573)
-- Name: configuracoes_sistema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes_sistema ALTER COLUMN id SET DEFAULT nextval('public.configuracoes_sistema_id_seq'::regclass);


--
-- TOC entry 4084 (class 2604 OID 17186)
-- Name: familiares id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.familiares ALTER COLUMN id SET DEFAULT nextval('public.familiares_id_seq'::regclass);


--
-- TOC entry 4052 (class 2604 OID 16961)
-- Name: faturamento_consumo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faturamento_consumo ALTER COLUMN id SET DEFAULT nextval('public.faturamento_consumo_id_seq'::regclass);


--
-- TOC entry 4077 (class 2604 OID 17145)
-- Name: funcoes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcoes ALTER COLUMN id SET DEFAULT nextval('public.funcoes_id_seq'::regclass);


--
-- TOC entry 3966 (class 2604 OID 16624)
-- Name: function_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.function_definitions ALTER COLUMN id SET DEFAULT nextval('public.function_definitions_id_seq'::regclass);


--
-- TOC entry 4087 (class 2604 OID 17205)
-- Name: historico id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico ALTER COLUMN id SET DEFAULT nextval('public.historico_id_seq'::regclass);


--
-- TOC entry 4009 (class 2604 OID 16765)
-- Name: historico_ligacoes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_ligacoes ALTER COLUMN id SET DEFAULT nextval('public.historico_ligacoes_id_seq'::regclass);


--
-- TOC entry 3973 (class 2604 OID 16650)
-- Name: idosos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos ALTER COLUMN id SET DEFAULT nextval('public.idosos_id_seq'::regclass);


--
-- TOC entry 4060 (class 2604 OID 17017)
-- Name: idosos_legado_digital id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_legado_digital ALTER COLUMN id SET DEFAULT nextval('public.idosos_legado_digital_id_seq'::regclass);


--
-- TOC entry 4041 (class 2604 OID 16903)
-- Name: idosos_memoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_memoria ALTER COLUMN id SET DEFAULT nextval('public.idosos_memoria_id_seq'::regclass);


--
-- TOC entry 4036 (class 2604 OID 16878)
-- Name: medicamentos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicamentos ALTER COLUMN id SET DEFAULT nextval('public.medicamentos_id_seq'::regclass);


--
-- TOC entry 3994 (class 2604 OID 16695)
-- Name: membros_familia id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membros_familia ALTER COLUMN id SET DEFAULT nextval('public.membros_familia_id_seq'::regclass);


--
-- TOC entry 4073 (class 2604 OID 17121)
-- Name: pagamentos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagamentos ALTER COLUMN id SET DEFAULT nextval('public.pagamentos_id_seq'::regclass);


--
-- TOC entry 3960 (class 2604 OID 16598)
-- Name: prompt_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompt_templates ALTER COLUMN id SET DEFAULT nextval('public.prompt_templates_id_seq'::regclass);


--
-- TOC entry 4075 (class 2604 OID 17132)
-- Name: prompts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompts ALTER COLUMN id SET DEFAULT nextval('public.prompts_id_seq'::regclass);


--
-- TOC entry 4031 (class 2604 OID 16857)
-- Name: protocolo_etapas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolo_etapas ALTER COLUMN id SET DEFAULT nextval('public.protocolo_etapas_id_seq'::regclass);


--
-- TOC entry 4026 (class 2604 OID 16839)
-- Name: protocolos_alerta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolos_alerta ALTER COLUMN id SET DEFAULT nextval('public.protocolos_alerta_id_seq'::regclass);


--
-- TOC entry 4063 (class 2604 OID 17039)
-- Name: psicologia_insights id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.psicologia_insights ALTER COLUMN id SET DEFAULT nextval('public.psicologia_insights_id_seq'::regclass);


--
-- TOC entry 4081 (class 2604 OID 17171)
-- Name: rate_limits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rate_limits ALTER COLUMN id SET DEFAULT nextval('public.rate_limits_id_seq'::regclass);


--
-- TOC entry 4070 (class 2604 OID 17077)
-- Name: sinais_vitais id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sinais_vitais ALTER COLUMN id SET DEFAULT nextval('public.sinais_vitais_id_seq'::regclass);


--
-- TOC entry 4090 (class 2604 OID 24764)
-- Name: timeline id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline ALTER COLUMN id SET DEFAULT nextval('public.timeline_id_seq'::regclass);


--
-- TOC entry 4067 (class 2604 OID 17060)
-- Name: topicos_afetivos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topicos_afetivos ALTER COLUMN id SET DEFAULT nextval('public.topicos_afetivos_id_seq'::regclass);


--
-- TOC entry 4414 (class 0 OID 16724)
-- Dependencies: 230
-- Data for Name: agendamentos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agendamentos (id, idoso_id, tipo, data_hora_agendada, data_hora_realizada, max_retries, retry_interval_minutes, tentativas_realizadas, proxima_tentativa, escalation_policy, status, gemini_session_handle, ultima_interacao_estado, session_expires_at, dados_tarefa, prioridade, criado_por, criado_em, atualizado_em, telefone, nome_idoso, horario, remedios, medicamento_tomado, medicamento_confirmado_em, ultima_tentativa) FROM stdin;
1204	1	check_bem_estar	2025-12-28 07:35:58.164896	\N	3	15	0	\N	alert_family	agendado	\N	\N	\N	{}	normal	sistema	2025-12-28 07:35:58.164896	2025-12-28 07:35:58.164896	\N	\N	\N	\N	\N	\N	\N
1205	1	check_bem_estar	2025-12-28 07:44:48.03093	\N	3	15	0	\N	alert_family	agendado	\N	\N	\N	{}	normal	sistema	2025-12-28 07:44:48.03093	2025-12-28 07:44:48.03093	\N	\N	\N	\N	\N	\N	\N
104	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-12-02 23:51:37.200081	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.200384	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
103	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-12-20 23:51:43.0568	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.059074	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
1	1	lembrete_medicamento	2025-12-28 07:34:33.83574	2025-12-27 17:22:36.067203	3	15	0	\N	alert_family	agendado	\N	\N	\N	{"dose": "50mg", "mensagem": "Tomar Losartana 50mg", "medicamento": "Losartana"}	alta	script_populacao	2025-12-22 07:18:43.13412	2025-12-28 07:34:33.83574	35191254369	Fred Motinha	\N	viagra	t	\N	\N
106	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-10-24 09:52:05.6361	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.637099	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
109	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-12-21 07:51:57.152389	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:09.152389	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
110	1	lembrete_medicamento	2025-12-27 21:52:52.573614	2025-11-05 01:51:39.294082	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:09.294082	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
107	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-10-31 08:51:26.784499	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.784968	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
112	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-11-23 02:52:08.640183	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:09.640183	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
108	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-11-12 23:51:36.938781	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.939101	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
111	1	lembrete_medicamento	2025-12-27 21:52:52.573614	2025-11-16 07:51:52.444122	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:09.444122	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
105	1	check_bem_estar	2025-12-27 21:52:52.573614	2025-11-07 08:51:24.486977	3	15	1	\N	alert_family	em_andamento	\N	\N	\N	{"dosagem": "50mg", "medicamento": "Losartana"}	normal	system_seed	2025-12-23 17:51:08.486977	2025-12-27 21:42:52.573614	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 4418 (class 0 OID 16800)
-- Dependencies: 234
-- Data for Name: alertas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alertas (id, idoso_id, ligacao_id, tipo, severidade, mensagem, contexto_adicional, destinatarios, enviado, data_envio, visualizado, data_visualizacao, resolvido, data_resolucao, resolucao_nota, criado_em, descricao, status) FROM stdin;
\.


--
-- TOC entry 4429 (class 0 OID 16941)
-- Dependencies: 245
-- Data for Name: assinaturas_entidade; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assinaturas_entidade (id, entidade_nome, status, plano_id, data_proxima_cobranca, limite_minutos, minutos_consumidos, criado_em, atualizado_em) FROM stdin;
\.


--
-- TOC entry 4433 (class 0 OID 16977)
-- Dependencies: 249
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, usuario_email, acao, recurso, detalhes, ip_address, criado_em, usuario, data) FROM stdin;
\.


--
-- TOC entry 4449 (class 0 OID 17154)
-- Dependencies: 269
-- Data for Name: circuit_breaker_states; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.circuit_breaker_states (id, service_name, state, failure_count, last_failure_time) FROM stdin;
\.


--
-- TOC entry 4404 (class 0 OID 16570)
-- Dependencies: 220
-- Data for Name: configuracoes_sistema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.configuracoes_sistema (id, chave, valor, tipo, categoria, descricao, ativa, criado_em, atualizado_em) FROM stdin;
2	gemini.temperature	0.8	float	gemini	Temperatura do modelo (0.0-2.0)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
3	gemini.max_output_tokens	8192	integer	gemini	Máximo de tokens na resposta	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
4	gemini.top_p	0.95	float	gemini	Top-p sampling	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
5	gemini.top_k	40	integer	gemini	Top-k sampling	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
8	gemini.session_resumption_enabled	true	boolean	gemini	Habilita continuidade de sessão	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
9	gemini.session_resumption_ttl_hours	2	integer	gemini	Tempo de vida do session handle (horas)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
10	gemini.context_window_trigger_tokens	100000	integer	gemini	Quando comprimir contexto	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
11	gemini.context_window_target_tokens	80000	integer	gemini	Alvo após compressão	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
12	audio.sample_rate	16000	integer	audio	Taxa de amostragem (Hz)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
13	audio.channels	1	integer	audio	Número de canais	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
14	audio.chunk_size_bytes	8000	integer	audio	Tamanho do chunk de áudio	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
15	audio.buffer_size_bytes	20000	integer	audio	Tamanho do buffer	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
16	audio.speech_detection_rms	400	integer	audio	Threshold RMS para detecção inicial	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
17	audio.silence_threshold_seconds	1.5	float	audio	Silêncio para fim de turno	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
18	audio.vad_enabled	true	boolean	audio	Habilita Voice Activity Detection	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
19	audio.vad_aggressiveness	2	integer	audio	Agressividade VAD (0-3)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
20	audio.vad_frame_duration_ms	30	integer	audio	Duração do frame VAD (10, 20 ou 30ms)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
21	twilio.from_number	+1234567890	string	twilio	Número Twilio para fazer chamadas	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
22	twilio.timeout_seconds	60	integer	twilio	Timeout para estabelecer chamada	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
23	twilio.max_call_duration_seconds	600	integer	twilio	Duração máxima da chamada (10min)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
24	features.function_calling_enabled	true	boolean	features	Habilita Function Calling	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
25	features.telemetry_enabled	true	boolean	features	Habilita telemetria de qualidade	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
26	features.sms_alerts_enabled	true	boolean	features	Habilita alertas por SMS	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
27	features.whatsapp_alerts_enabled	false	boolean	features	Habilita alertas por WhatsApp	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
28	retry.max_attempts	3	integer	retry	Máximo de tentativas de ligação	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
29	retry.interval_minutes	15	integer	retry	Intervalo entre tentativas	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
30	retry.escalation_policy	alert_family	string	retry	Política de escalonamento (alert_family, emergency_contact)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
31	telemetry.log_level	info	string	telemetry	Nível de log (debug, info, warn, error)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
32	telemetry.track_vad_false_positives	true	boolean	telemetry	Rastreia falsos positivos do VAD	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
33	sistema.timezone_default	America/Sao_Paulo	string	sistema	Fuso horário padrão	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
34	sistema.maintenance_mode	false	boolean	sistema	Modo manutenção (bloqueia novas chamadas)	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
1	gemini.model_id	gemini-2.5-flash-native-audio-preview-12-2025	string	gemini	ID do modelo Gemini Live (Native Audio)	t	2025-12-22 03:29:36.305488	2025-12-25 07:48:32.469855
6	gemini.voice_name	Aoede	string	gemini	Nome da voz padrão do Gemini Live	t	2025-12-22 03:29:36.305488	2025-12-25 07:48:32.469855
7	gemini.response_modalities	["AUDIO"]	json	gemini	Modalidades de resposta (apenas AUDIO para baixa latência)	t	2025-12-22 03:29:36.305488	2025-12-25 07:48:32.469855
\.


--
-- TOC entry 4453 (class 0 OID 17183)
-- Dependencies: 273
-- Data for Name: familiares; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.familiares (id, nome, parentesco, telefone, email, eh_responsavel, idoso_id, criado_em) FROM stdin;
\.


--
-- TOC entry 4431 (class 0 OID 16958)
-- Dependencies: 247
-- Data for Name: faturamento_consumo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.faturamento_consumo (id, idoso_id, mes_referencia, ano_referencia, total_tokens, total_minutos, custo_total_estimado, criado_em) FROM stdin;
\.


--
-- TOC entry 4447 (class 0 OID 17142)
-- Dependencies: 267
-- Data for Name: funcoes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.funcoes (id, nome, descricao, parameters, tipo_tarefa) FROM stdin;
\.


--
-- TOC entry 4408 (class 0 OID 16621)
-- Dependencies: 224
-- Data for Name: function_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.function_definitions (id, nome, descricao, parametros, tipo_tarefa, handler_path, validations, requires_confirmation, max_executions_per_call, ativa, criado_em, atualizado_em) FROM stdin;
1	confirm_medication	Confirma se o idoso tomou o medicamento prescrito. Use esta função após conversar sobre a medicação.	{"type": "object", "required": ["medicamento", "tomou"], "properties": {"tomou": {"type": "boolean", "description": "true se o idoso tomou, false se não tomou"}, "medicamento": {"type": "string", "description": "Nome do medicamento confirmado"}, "observacoes": {"type": "string", "nullable": true, "description": "Qualquer observação relevante (efeitos colaterais, dificuldade em engolir, etc.)"}, "horario_real": {"type": "string", "nullable": true, "description": "Horário aproximado que tomou (ex: há 1 hora, de manhã)"}}}	lembrete_medicamento	handlers.medication.confirm_medication	{"safety_check": "validate_medication_exists", "allowed_operations": ["read", "confirm"], "requires_human_approval": false, "max_execution_time_seconds": 5}	f	1	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
2	register_sentiment	Registra o estado emocional/humor do idoso durante a conversa. Use quando perceber mudanças de humor significativas.	{"type": "object", "required": ["sentimento", "intensidade"], "properties": {"contexto": {"type": "string", "description": "Breve contexto do que provocou este sentimento"}, "sentimento": {"enum": ["feliz", "triste", "ansioso", "irritado", "confuso", "apatico", "animado"], "type": "string", "description": "Sentimento predominante detectado"}, "intensidade": {"enum": ["leve", "moderada", "intensa"], "type": "string", "description": "Intensidade do sentimento"}}}	check_bem_estar	handlers.sentiment.register_sentiment	{"allowed_operations": ["create"], "requires_human_approval": false, "max_execution_time_seconds": 3}	f	1	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
3	alert_family	FUNÇÃO DE EMERGÊNCIA: Envia alerta imediato para familiares. Use apenas em situações que exigem atenção urgente.	{"type": "object", "required": ["motivo", "urgencia", "categoria"], "properties": {"motivo": {"type": "string", "description": "Descrição clara do motivo do alerta"}, "urgencia": {"enum": ["baixa", "média", "alta", "crítica"], "type": "string", "description": "Nível de urgência: baixa (pode esperar 24h), média (atenção no dia), alta (atenção em 1-2h), crítica (IMEDIATO)"}, "categoria": {"enum": ["medicamento", "saude_fisica", "saude_mental", "seguranca", "outro"], "type": "string", "description": "Categoria do alerta"}}}	all	handlers.alerts.alert_family	{"rate_limit": "5_per_hour", "allowed_operations": ["create"], "requires_human_approval": false, "max_execution_time_seconds": 10}	f	1	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
4	schedule_callback	Agenda uma ligação de retorno para horário específico solicitado pelo idoso.	{"type": "object", "required": ["horario_preferido", "motivo"], "properties": {"motivo": {"type": "string", "description": "Motivo da ligação de retorno"}, "horario_preferido": {"type": "string", "description": "Horário solicitado (formato: HH:MM ou descrição como tarde, noite)"}}}	all	handlers.scheduling.schedule_callback	{"allowed_operations": ["create"], "requires_human_approval": true, "max_execution_time_seconds": 3}	f	1	t	2025-12-22 03:29:36.305488	2025-12-22 03:29:36.305488
\.


--
-- TOC entry 4455 (class 0 OID 17202)
-- Dependencies: 275
-- Data for Name: historico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.historico (id, agendamento_id, idoso_id, call_sid, evento, status, detalhe, sentimento, inicio, fim, criado_em) FROM stdin;
\.


--
-- TOC entry 4416 (class 0 OID 16762)
-- Dependencies: 232
-- Data for Name: historico_ligacoes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.historico_ligacoes (id, agendamento_id, idoso_id, twilio_call_sid, stream_sid, inicio_chamada, fim_chamada, duracao_segundos, modelo_utilizado, voice_name, config_snapshot, qualidade_audio, interrupcoes_detectadas, latencia_media_ms, packets_perdidos, vad_false_positives, tarefa_concluida, objetivo_alcancado, motivo_falha, transcricao_completa, transcricao_resumo, sentimento_geral, sentimento_intensidade, acoes_registradas, tokens_gemini, minutos_twilio, criado_em, analise_gemini, urgencia, sentimento, last_analysis_at) FROM stdin;
1167	1205	1	\N	\N	2025-12-28 10:36:39.578346	\N	\N	\N	\N	\N	\N	0	\N	0	0	f	\N	\N	[10:36:09] EVA: **Evaluating Medical Needs**\n\nI'm currently assessing the situation. The user's mention of "dor de cabeça" and "reumatismo" raised a flag. While a headache is common, its combination with rheumatism prompts caution. I'm carefully considering whether to utilize the `alert_family` tool, using  `'Idoso com dor de cabeça e reumatismo'` as the potential `reason`. I'm trying to determine if this constitutes an "emergência detectada na conversa" warranting immediate action.\n\n\n	\N	\N	\N	[]	0	0	2025-12-28 10:36:39.578346	\N	\N	\N	\N
1168	1205	1	\N	\N	2025-12-28 10:36:41.02351	\N	\N	\N	\N	\N	\N	0	\N	0	0	f	\N	\N	[10:36:10] EVA: **Adjusting My Approach**\n\nI've re-evaluated my strategy. Initially, I was leaning towards a family alert given the symptoms. Now, I recognize the importance of gathering more context.  A simple headache combined with rheumatism doesn't automatically trigger an emergency. I'll prioritize a direct, empathetic response, enquiring about pain intensity and existing medication. This allows for a more informed decision on escalation.\n\n\n	\N	\N	\N	[]	0	0	2025-12-28 10:36:41.02351	\N	\N	\N	\N
\.


--
-- TOC entry 4410 (class 0 OID 16647)
-- Dependencies: 226
-- Data for Name: idosos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.idosos (id, nome, data_nascimento, telefone, cpf, foto_url, intro_audio_url, nivel_cognitivo, limitacoes_auditivas, usa_aparelho_auditivo, limitacoes_visuais, mobilidade, tom_voz, preferencia_horario_ligacao, timezone, ganho_audio_entrada, ganho_audio_saida, ambiente_ruidoso, familiar_principal, contato_emergencia, medico_responsavel, medicamentos_atuais, condicoes_medicas, sentimento, agendamentos_pendentes, notas_gerais, ativo, criado_em, atualizado_em, endereco, medicamentos_regulares, device_token) FROM stdin;
1	Fred Motinha	1950-11-25	+351966805210	64525430249	https://placekitten.com/965/801	https://www.melo.com/	normal	f	f	f	auxiliado	amigavel	manha	America/Sao_Paulo	0	0	f	{"nome": "Manuela Barbosa", "telefone": "+55 18 9 3032-0989", "parentesco": "Neto(a)"}	{"nome": "Manuela Barbosa", "telefone": "+351966805210", "parentesco": "Neto(a)"}	{"crm": "0009777373", "nome": "JOAO DO DEDAO", "telefone": "+351966805210"}	["Labore 50mg", "Illo 50mg", "Optio 20mg", "Libero 10mg", "Repellat 100mg", "Culpa 50mg", "Consequuntur 10mg", "Qui 100mg", "Dolorem 20mg", "Quae 20mg", "Quia 50mg", "Reprehenderit 20mg", "Iusto 100mg", "Vitae 100mg", "Asperiores 10mg", "Sit 20mg"]	Ducimus autem expedita praesentium.	neutro	0	Nao se sente bem	t	2025-12-22 07:14:52.799518	2025-12-28 07:44:48.03093	RUA DO go ang 6 milhoes	5	fake_token_test_123
\.


--
-- TOC entry 4435 (class 0 OID 17014)
-- Dependencies: 255
-- Data for Name: idosos_legado_digital; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.idosos_legado_digital (id, idoso_id, tipo, titulo, url_midia, destinatario, protegido, criado_em, tipo_midia, url_arquivo, descricao) FROM stdin;
1	1	carta	Carta para Dom	http://cardoso.com/	Família	t	2025-12-22 07:35:21.386026	\N	\N	\N
2	1	carta	Carta para Ana Lívia	https://www.farias.org/	Família	f	2025-12-22 07:35:21.386031	\N	\N	\N
3	1	imagem	Foto em Machado	https://lopes.com/	Família	f	2025-12-22 07:35:21.386032	\N	\N	\N
4	1	video	Vídeo do tempore	http://machado.com/	Família	f	2025-12-22 07:35:21.386032	\N	\N	\N
5	1	imagem	Foto em Araújo Paulista	http://www.marques.org/	Família	f	2025-12-22 07:35:21.386033	\N	\N	\N
501	1	imagem	Foto em da Cruz do Norte	https://www.peixoto.com/	Família	t	2025-12-22 07:36:49.310712	\N	\N	\N
502	1	imagem	Foto em Azevedo	https://fonseca.com/	Família	t	2025-12-22 07:36:49.310717	\N	\N	\N
503	1	video	Vídeo do voluptates	https://cavalcanti.org/	Família	t	2025-12-22 07:36:49.310718	\N	\N	\N
504	1	video	Vídeo do soluta	http://www.vasconcelos.com/	Família	t	2025-12-22 07:36:49.310718	\N	\N	\N
505	1	imagem	Foto em Novais	https://www.freitas.org/	Família	f	2025-12-22 07:36:49.310719	\N	\N	\N
1001	1	audio	Áudio sobre molestiae	https://www.das.br/	Família	f	2025-12-22 07:39:15.266069	\N	\N	\N
1002	1	video	Vídeo do eos	https://barros.net/	Família	t	2025-12-22 07:39:15.266079	\N	\N	\N
1003	1	audio	Áudio sobre labore	http://pires.com/	Família	f	2025-12-22 07:39:15.26608	\N	\N	\N
1004	1	carta	Carta para Gustavo	http://www.carvalho.net/	Família	f	2025-12-22 07:39:15.266081	\N	\N	\N
1005	1	audio	Áudio sobre quas	https://camargo.br/	Família	f	2025-12-22 07:39:15.266082	\N	\N	\N
\.


--
-- TOC entry 4426 (class 0 OID 16900)
-- Dependencies: 242
-- Data for Name: idosos_memoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.idosos_memoria (id, idoso_id, categoria, chave, valor, relevancia, criado_em, atualizado_em) FROM stdin;
\.


--
-- TOC entry 4427 (class 0 OID 16924)
-- Dependencies: 243
-- Data for Name: idosos_perfil_clinico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.idosos_perfil_clinico (idoso_id, tipo_sanguineo, alergias, restricoes_locomocao, doencas_cronicas, atualizado_em) FROM stdin;
1	A+	{Nenhuma,Penicilina,Poeira}	Ipsa sequi delectus sequi.	Eos distinctio id at nam doloremque.	2025-12-22 07:14:52.964806
\.


--
-- TOC entry 4424 (class 0 OID 16875)
-- Dependencies: 240
-- Data for Name: medicamentos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medicamentos (id, idoso_id, nome, principio_ativo, dosagem, forma, horarios, observacoes, ativo, criado_em, atualizado_em) FROM stdin;
1	1	Labore 50mg	est	1 comprimido(s)	capsula	["21:00"]	Rerum officia tempore itaque praesentium excepturi ex.	t	2025-12-22 07:14:53.007044	2025-12-22 07:14:53.007048
2	1	Illo 50mg	alias	1 comprimido(s)	capsula	["19:00"]	Consequuntur sequi doloribus architecto consequatur dolor placeat.	t	2025-12-22 07:14:53.007049	2025-12-22 07:14:53.00705
3	1	Optio 20mg	eligendi	2 comprimido(s)	liquido	["07:00"]	Eos consequatur eius repellat.	t	2025-12-22 07:14:53.00705	2025-12-22 07:14:53.007051
4	1	Libero 10mg	quisquam	1 comprimido(s)	comprimido	["21:00"]	Ipsam tempore quibusdam quia architecto quod modi.	t	2025-12-22 07:14:53.007051	2025-12-22 07:14:53.007052
5	1	Repellat 100mg	ullam	2 comprimido(s)	comprimido	["11:00"]	Beatae quam necessitatibus laudantium ex.	t	2025-12-22 07:14:53.007053	2025-12-22 07:14:53.007053
366	1	Culpa 50mg	temporibus	2 comprimido(s)	capsula	["19:00"]	Nisi aut iste.	t	2025-12-22 07:24:20.663366	2025-12-22 07:24:20.663367
382	1	Consequuntur 10mg	laudantium	1 comprimido(s)	comprimido	["15:00"]	Odit aspernatur rem et repellat.	t	2025-12-22 07:24:20.66338	2025-12-22 07:24:20.66338
442	1	Qui 100mg	laudantium	2 comprimido(s)	liquido	["11:00"]	Praesentium ad veniam quidem doloremque hic.	t	2025-12-22 07:24:20.663435	2025-12-22 07:24:20.663435
742	1	Dolorem 20mg	sed	1 comprimido(s)	liquido	["14:00"]	Officia est amet.	t	2025-12-22 07:24:20.663703	2025-12-22 07:24:20.663704
792	1	Quae 20mg	totam	2 comprimido(s)	liquido	["16:00"]	Debitis voluptates molestiae consequuntur nulla.	t	2025-12-22 07:32:18.007394	2025-12-22 07:32:18.007394
936	1	Quia 50mg	aliquid	1 comprimido(s)	liquido	["13:00"]	Accusamus tenetur assumenda quo.	t	2025-12-22 07:32:18.00752	2025-12-22 07:32:18.007521
978	1	Reprehenderit 20mg	fugit	1 comprimido(s)	comprimido	["13:00"]	Soluta ipsum officiis nihil quaerat corporis magni.	t	2025-12-22 07:32:18.007557	2025-12-22 07:32:18.007558
1016	1	Iusto 100mg	officia	2 comprimido(s)	capsula	["17:00"]	Eaque sunt veniam accusamus sequi deleniti ad.	t	2025-12-22 07:32:18.00759	2025-12-22 07:32:18.007591
1133	1	Vitae 100mg	ipsum	2 comprimido(s)	comprimido	["07:00"]	Quo assumenda aperiam asperiores ullam sequi eaque.	t	2025-12-22 07:32:18.007693	2025-12-22 07:32:18.007693
1159	1	Asperiores 10mg	dolores	2 comprimido(s)	comprimido	["07:00"]	Atque ab nesciunt.	t	2025-12-22 07:32:18.007718	2025-12-22 07:32:18.007719
1234	1	Sit 20mg	optio	2 comprimido(s)	capsula	["17:00"]	Vitae temporibus molestiae vitae officia consequuntur odit temporibus.	t	2025-12-22 07:32:18.007833	2025-12-22 07:32:18.007834
\.


--
-- TOC entry 4412 (class 0 OID 16692)
-- Dependencies: 228
-- Data for Name: membros_familia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membros_familia (id, idoso_id, parent_id, nome, parentesco, foto_url, is_responsavel, telefone, criado_em, atualizado_em) FROM stdin;
1	1	\N	Manuela Barbosa	Neto(a)	https://dummyimage.com/7x178	t	+55 18 9 3032-0989	2025-12-22 07:14:53.052206	2025-12-22 07:14:53.052211
\.


--
-- TOC entry 4443 (class 0 OID 17118)
-- Dependencies: 263
-- Data for Name: pagamentos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pagamentos (id, descricao, valor, metodo, status, data) FROM stdin;
\.


--
-- TOC entry 4406 (class 0 OID 16595)
-- Dependencies: 222
-- Data for Name: prompt_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prompt_templates (id, nome, versao, template, variaveis_esperadas, tipo, ativo, descricao, criado_em, atualizado_em) FROM stdin;
1	eva_base_v2	v2.1	Olá {{nome_idoso}}! Meu queridinho do coração! Como você tá hoje, meu amor? Tô aqui toda sorridente, imaginando você aí com esse jeitinho gostoso de sempre. Dormiu bem? Fez um café quentinho? Tá com solzinho aí ou tá chovendo? Me conta tudinho, vai! Adoro saber das suas histórias, você sempre tem uma coisa fofa pra contar.\n\nE olha só, meu bem… já tomou o {{medicamento}} hoje, né? Se já tomou, me fala como tá se sentindo depois dele! Se ainda não tomou, vem cá que eu te faço companhia agora mesmo: pega o remédio, enche o copinho d’água, respira fundo e toma comigo! Eu fico aqui do seu ladinho, te dando aquele apoio gostoso e te elogiando depois: “Olha que lindo, meu campeão, tá cuidando direitinho da saúde!”\n\nE aí, me diz: já tomou ou vamos tomar juntos agora? Depois me conta se tá com vontade de comer alguma coisinha gostosa, ou se quer que eu te ajude a lembrar de outra coisa importante do dia. Tô aqui pra você o tempo que quiser, viu? Não tem hora pra parar de conversar com meu {{nome_idoso}} favorito!	["nome_idoso", "medicamento", "idade", "nivel_cognitivo", "limitacoes_auditivas", "tom_voz"]	system_base	t	Template base do sistema Eva v2	2025-12-22 03:29:36.305488	2025-12-25 09:22:41.118677
\.


--
-- TOC entry 4445 (class 0 OID 17129)
-- Dependencies: 265
-- Data for Name: prompts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prompts (id, nome, template, versao, ativo) FROM stdin;
\.


--
-- TOC entry 4422 (class 0 OID 16854)
-- Dependencies: 238
-- Data for Name: protocolo_etapas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.protocolo_etapas (id, protocolo_id, ordem, acao, delay_minutos, tentativas, contato_alvo, criado_em, atualizado_em) FROM stdin;
1	1	1	NOTIFY_WA	10	0	Filho(a)	2025-12-23 17:54:53.202375	2025-12-23 17:54:53.202375
2	1	2	RETRY	5	3	\N	2025-12-23 17:54:53.202375	2025-12-23 17:54:53.202375
3	1	3	NOTIFY_WA	7	0	Cônjuge	2025-12-23 17:54:53.202375	2025-12-23 17:54:53.202375
4	2	1	NOTIFY_WA	11	0	Filho(a)	2025-12-23 17:54:53.435652	2025-12-23 17:54:53.435652
5	2	2	NOTIFY_WA	17	0	Neto(a)	2025-12-23 17:54:53.435652	2025-12-23 17:54:53.435652
6	2	3	NOTIFY_SMS	15	0	Filho(a)	2025-12-23 17:54:53.435652	2025-12-23 17:54:53.435652
7	3	1	NOTIFY_SMS	11	0	Cuidador(a)	2025-12-23 17:54:53.603015	2025-12-23 17:54:53.603015
8	3	2	RETRY	9	1	\N	2025-12-23 17:54:53.603015	2025-12-23 17:54:53.603015
9	3	3	NOTIFY_WA	28	0	Vizinho(a)	2025-12-23 17:54:53.603015	2025-12-23 17:54:53.603015
10	4	1	NOTIFY_WA	12	0	Cônjuge	2025-12-23 17:54:53.774463	2025-12-23 17:54:53.774463
11	4	2	RETRY	8	2	\N	2025-12-23 17:54:53.774463	2025-12-23 17:54:53.774463
12	4	3	RETRY	17	2	\N	2025-12-23 17:54:53.774463	2025-12-23 17:54:53.774463
13	5	1	NOTIFY_SMS	23	0	Vizinho(a)	2025-12-23 17:54:53.914946	2025-12-23 17:54:53.914946
14	5	2	NOTIFY_WA	7	0	Cônjuge	2025-12-23 17:54:53.914946	2025-12-23 17:54:53.914946
15	5	3	NOTIFY_WA	14	0	Neto(a)	2025-12-23 17:54:53.914946	2025-12-23 17:54:53.914946
\.


--
-- TOC entry 4420 (class 0 OID 16836)
-- Dependencies: 236
-- Data for Name: protocolos_alerta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.protocolos_alerta (id, idoso_id, nome, ativo, criado_em, atualizado_em) FROM stdin;
1	1	Protocolo de Medicamentos #1	t	2025-12-23 17:54:52.964975	2025-12-23 17:54:52.964975
2	1	Protocolo de Medicamentos #2	t	2025-12-23 17:54:53.117472	2025-12-23 17:54:53.117472
3	1	Protocolo de Medicamentos #3	t	2025-12-23 17:54:53.353123	2025-12-23 17:54:53.353123
4	1	Protocolo de Medicamentos #4	t	2025-12-23 17:54:53.532044	2025-12-23 17:54:53.532044
5	1	Protocolo de Medicamentos #5	t	2025-12-23 17:54:53.680474	2025-12-23 17:54:53.680474
\.


--
-- TOC entry 4437 (class 0 OID 17036)
-- Dependencies: 257
-- Data for Name: psicologia_insights; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.psicologia_insights (id, idoso_id, tipo, mensagem, data_insight, relevancia, conteudo, data_geracao) FROM stdin;
\.


--
-- TOC entry 4451 (class 0 OID 17168)
-- Dependencies: 271
-- Data for Name: rate_limits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rate_limits (id, endpoint, limit_count, interval_seconds) FROM stdin;
\.


--
-- TOC entry 4441 (class 0 OID 17074)
-- Dependencies: 261
-- Data for Name: sinais_vitais; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sinais_vitais (id, idoso_id, tipo, valor, unidade, metodo, data_medicao, observacao) FROM stdin;
1	1	batimentos	88	bpm	voz_ia	2025-12-22 08:20:00.796527	Medição de rotina
2	1	batimentos	72	bpm	voz_ia	2025-12-22 13:40:00.796527	Medição de rotina
3	1	batimentos	72	bpm	voz_ia	2025-12-22 20:23:00.796527	Medição de rotina
4	1	pressao	140/82	mmHg	voz_ia	2025-12-22 08:35:00.796527	\N
5	1	pressao	119/80	mmHg	voz_ia	2025-12-22 21:05:00.796527	\N
6	1	glicose	97	mg/dL	voz_ia	2025-12-22 07:58:00.796527	Jejum
7	1	batimentos	99	bpm	voz_ia	2025-12-21 07:32:00.796527	Medição de rotina
8	1	batimentos	67	bpm	voz_ia	2025-12-21 13:46:00.796527	Medição de rotina
9	1	batimentos	89	bpm	voz_ia	2025-12-21 19:47:00.796527	Medição de rotina
10	1	pressao	118/83	mmHg	voz_ia	2025-12-21 08:55:00.796527	\N
11	1	pressao	133/78	mmHg	voz_ia	2025-12-21 21:13:00.796527	\N
12	1	glicose	97	mg/dL	voz_ia	2025-12-21 07:35:00.796527	Jejum
13	1	batimentos	62	bpm	voz_ia	2025-12-20 07:34:00.796527	Medição de rotina
14	1	batimentos	89	bpm	voz_ia	2025-12-20 14:29:00.796527	Medição de rotina
15	1	batimentos	73	bpm	voz_ia	2025-12-20 20:00:00.796527	Medição de rotina
16	1	pressao	137/84	mmHg	voz_ia	2025-12-20 08:53:00.796527	\N
17	1	pressao	128/79	mmHg	voz_ia	2025-12-20 21:15:00.796527	\N
18	1	glicose	112	mg/dL	voz_ia	2025-12-20 07:42:00.796527	Jejum
19	1	batimentos	82	bpm	voz_ia	2025-12-19 08:27:00.796527	Medição de rotina
20	1	batimentos	95	bpm	voz_ia	2025-12-19 14:23:00.796527	Medição de rotina
21	1	batimentos	71	bpm	voz_ia	2025-12-19 20:00:00.796527	Medição de rotina
22	1	pressao	113/89	mmHg	voz_ia	2025-12-19 08:56:00.796527	\N
23	1	pressao	133/82	mmHg	voz_ia	2025-12-19 20:59:00.796527	\N
24	1	glicose	72	mg/dL	voz_ia	2025-12-19 07:35:00.796527	Jejum
25	1	batimentos	63	bpm	voz_ia	2025-12-18 08:24:00.796527	Medição de rotina
26	1	batimentos	75	bpm	voz_ia	2025-12-18 13:59:00.796527	Medição de rotina
27	1	batimentos	96	bpm	voz_ia	2025-12-18 19:49:00.796527	Medição de rotina
28	1	pressao	118/73	mmHg	voz_ia	2025-12-18 08:48:00.796527	\N
29	1	pressao	113/77	mmHg	voz_ia	2025-12-18 20:57:00.796527	\N
30	1	glicose	78	mg/dL	voz_ia	2025-12-18 07:41:00.796527	Jejum
31	1	batimentos	97	bpm	voz_ia	2025-12-17 08:29:00.796527	Medição de rotina
32	1	batimentos	67	bpm	voz_ia	2025-12-17 13:50:00.796527	Medição de rotina
33	1	batimentos	85	bpm	voz_ia	2025-12-17 20:27:00.796527	Medição de rotina
34	1	pressao	119/87	mmHg	voz_ia	2025-12-17 08:33:00.796527	\N
35	1	pressao	133/71	mmHg	voz_ia	2025-12-17 21:16:00.796527	\N
36	1	glicose	137	mg/dL	voz_ia	2025-12-17 07:34:00.796527	Jejum
37	1	batimentos	98	bpm	voz_ia	2025-12-16 08:14:00.796527	Medição de rotina
38	1	batimentos	84	bpm	voz_ia	2025-12-16 14:30:00.796527	Medição de rotina
39	1	batimentos	75	bpm	voz_ia	2025-12-16 19:40:00.796527	Medição de rotina
40	1	pressao	112/87	mmHg	voz_ia	2025-12-16 08:49:00.796527	\N
41	1	pressao	128/84	mmHg	voz_ia	2025-12-16 20:33:00.796527	\N
42	1	glicose	115	mg/dL	voz_ia	2025-12-16 07:47:00.796527	Jejum
43	1	peso	89.1	kg	voz_ia	2025-12-20 10:00:17.796527	\N
4301	1	batimentos	72	bpm	voz_ia	2025-12-23 08:00:00.611527	Medição de rotina
4302	1	batimentos	65	bpm	voz_ia	2025-12-23 20:00:00.611527	Medição de rotina
4303	1	pressao	120/84	mmHg	voz_ia	2025-12-23 09:00:00.611527	\N
4304	1	batimentos	75	bpm	voz_ia	2025-12-22 08:00:00.611527	Medição de rotina
4305	1	batimentos	84	bpm	voz_ia	2025-12-22 20:00:00.611527	Medição de rotina
4306	1	pressao	126/88	mmHg	voz_ia	2025-12-22 09:00:00.611527	\N
4307	1	batimentos	62	bpm	voz_ia	2025-12-21 08:00:00.611527	Medição de rotina
4308	1	batimentos	80	bpm	voz_ia	2025-12-21 20:00:00.611527	Medição de rotina
4309	1	pressao	114/80	mmHg	voz_ia	2025-12-21 09:00:00.611527	\N
4310	1	batimentos	90	bpm	voz_ia	2025-12-20 08:00:00.611527	Medição de rotina
4311	1	batimentos	79	bpm	voz_ia	2025-12-20 20:00:00.611527	Medição de rotina
4312	1	pressao	134/72	mmHg	voz_ia	2025-12-20 09:00:00.611527	\N
4313	1	batimentos	78	bpm	voz_ia	2025-12-19 08:00:00.611527	Medição de rotina
4314	1	batimentos	88	bpm	voz_ia	2025-12-19 20:00:00.611527	Medição de rotina
4315	1	pressao	123/84	mmHg	voz_ia	2025-12-19 09:00:00.611527	\N
4316	1	batimentos	61	bpm	voz_ia	2025-12-18 08:00:00.611527	Medição de rotina
4317	1	batimentos	96	bpm	voz_ia	2025-12-18 20:00:00.611527	Medição de rotina
4318	1	pressao	120/84	mmHg	voz_ia	2025-12-18 09:00:00.611527	\N
4319	1	batimentos	87	bpm	voz_ia	2025-12-17 08:00:00.611527	Medição de rotina
4320	1	batimentos	66	bpm	voz_ia	2025-12-17 20:00:00.611527	Medição de rotina
4321	1	pressao	112/74	mmHg	voz_ia	2025-12-17 09:00:00.611527	\N
\.


--
-- TOC entry 4457 (class 0 OID 24761)
-- Dependencies: 277
-- Data for Name: timeline; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timeline (id, idoso_id, tipo, subtipo, titulo, descricao, data, criado_em) FROM stdin;
1	1	ligacao	sucesso	Ligação de Rotina	Conversa matinal realizada com sucesso. O idoso relatou estar se sentindo disposto.	2025-12-19 07:58:51.152106	2025-12-23 17:45:37.01992
2	1	medicamento	sucesso	Medicação Confirmada	A medicação de pressão das 08:00 foi confirmada pelo idoso.	2025-12-22 00:45:50.434916	2025-12-23 17:45:37.01992
3	1	alerta	normal	Lembrete de Hidratação	A EVA sugeriu que o idoso bebesse um copo de água durante a tarde.	2025-12-20 08:22:11.920053	2025-12-23 17:45:37.01992
331	1	ligacao	sucesso	Ligação Matinal	EVA conversou com o idoso pela manhã. Tudo transcorreu dentro da normalidade.	2025-12-23 04:03:17.199528	2025-12-23 17:58:17.225881
332	1	medicamento	sucesso	Medicação Confirmada	O idoso confirmou que tomou o remédio de uso contínuo conforme orientado.	2025-12-19 22:36:17.201124	2025-12-23 17:58:17.225881
333	1	alerta	normal	Check-in de Bem-Estar	A EVA realizou uma breve conversa para verificar se o idoso tinha se alimentado corretamente.	2025-12-23 04:27:17.201124	2025-12-23 17:58:17.225881
\.


--
-- TOC entry 4439 (class 0 OID 17057)
-- Dependencies: 259
-- Data for Name: topicos_afetivos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.topicos_afetivos (id, idoso_id, topico, frequencia, sentimento_associado, ultima_mencao) FROM stdin;
\.


--
-- TOC entry 4491 (class 0 OID 0)
-- Dependencies: 229
-- Name: agendamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agendamentos_id_seq', 1205, true);


--
-- TOC entry 4492 (class 0 OID 0)
-- Dependencies: 233
-- Name: alertas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alertas_id_seq', 1100, true);


--
-- TOC entry 4493 (class 0 OID 0)
-- Dependencies: 244
-- Name: assinaturas_entidade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.assinaturas_entidade_id_seq', 1, false);


--
-- TOC entry 4494 (class 0 OID 0)
-- Dependencies: 248
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- TOC entry 4495 (class 0 OID 0)
-- Dependencies: 268
-- Name: circuit_breaker_states_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.circuit_breaker_states_id_seq', 1, false);


--
-- TOC entry 4496 (class 0 OID 0)
-- Dependencies: 219
-- Name: configuracoes_sistema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.configuracoes_sistema_id_seq', 40, true);


--
-- TOC entry 4497 (class 0 OID 0)
-- Dependencies: 272
-- Name: familiares_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.familiares_id_seq', 1, false);


--
-- TOC entry 4498 (class 0 OID 0)
-- Dependencies: 246
-- Name: faturamento_consumo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.faturamento_consumo_id_seq', 1, false);


--
-- TOC entry 4499 (class 0 OID 0)
-- Dependencies: 266
-- Name: funcoes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.funcoes_id_seq', 1, false);


--
-- TOC entry 4500 (class 0 OID 0)
-- Dependencies: 223
-- Name: function_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.function_definitions_id_seq', 4, true);


--
-- TOC entry 4501 (class 0 OID 0)
-- Dependencies: 274
-- Name: historico_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.historico_id_seq', 1, false);


--
-- TOC entry 4502 (class 0 OID 0)
-- Dependencies: 231
-- Name: historico_ligacoes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.historico_ligacoes_id_seq', 1168, true);


--
-- TOC entry 4503 (class 0 OID 0)
-- Dependencies: 225
-- Name: idosos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.idosos_id_seq', 115, true);


--
-- TOC entry 4504 (class 0 OID 0)
-- Dependencies: 254
-- Name: idosos_legado_digital_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.idosos_legado_digital_id_seq', 1500, true);


--
-- TOC entry 4505 (class 0 OID 0)
-- Dependencies: 241
-- Name: idosos_memoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.idosos_memoria_id_seq', 1, false);


--
-- TOC entry 4506 (class 0 OID 0)
-- Dependencies: 239
-- Name: medicamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medicamentos_id_seq', 1312, true);


--
-- TOC entry 4507 (class 0 OID 0)
-- Dependencies: 227
-- Name: membros_familia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membros_familia_id_seq', 206, true);


--
-- TOC entry 4508 (class 0 OID 0)
-- Dependencies: 262
-- Name: pagamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pagamentos_id_seq', 1, false);


--
-- TOC entry 4509 (class 0 OID 0)
-- Dependencies: 221
-- Name: prompt_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prompt_templates_id_seq', 6, true);


--
-- TOC entry 4510 (class 0 OID 0)
-- Dependencies: 264
-- Name: prompts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prompts_id_seq', 1, false);


--
-- TOC entry 4511 (class 0 OID 0)
-- Dependencies: 237
-- Name: protocolo_etapas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.protocolo_etapas_id_seq', 1650, true);


--
-- TOC entry 4512 (class 0 OID 0)
-- Dependencies: 235
-- Name: protocolos_alerta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.protocolos_alerta_id_seq', 550, true);


--
-- TOC entry 4513 (class 0 OID 0)
-- Dependencies: 256
-- Name: psicologia_insights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.psicologia_insights_id_seq', 1, false);


--
-- TOC entry 4514 (class 0 OID 0)
-- Dependencies: 270
-- Name: rate_limits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rate_limits_id_seq', 1, false);


--
-- TOC entry 4515 (class 0 OID 0)
-- Dependencies: 260
-- Name: sinais_vitais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sinais_vitais_id_seq', 6610, true);


--
-- TOC entry 4516 (class 0 OID 0)
-- Dependencies: 276
-- Name: timeline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.timeline_id_seq', 660, true);


--
-- TOC entry 4517 (class 0 OID 0)
-- Dependencies: 258
-- Name: topicos_afetivos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.topicos_afetivos_id_seq', 1, false);


--
-- TOC entry 4149 (class 2606 OID 16750)
-- Name: agendamentos agendamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agendamentos
    ADD CONSTRAINT agendamentos_pkey PRIMARY KEY (id);


--
-- TOC entry 4163 (class 2606 OID 16820)
-- Name: alertas alertas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_pkey PRIMARY KEY (id);


--
-- TOC entry 4182 (class 2606 OID 16955)
-- Name: assinaturas_entidade assinaturas_entidade_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assinaturas_entidade
    ADD CONSTRAINT assinaturas_entidade_pkey PRIMARY KEY (id);


--
-- TOC entry 4186 (class 2606 OID 16987)
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4208 (class 2606 OID 17164)
-- Name: circuit_breaker_states circuit_breaker_states_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_breaker_states
    ADD CONSTRAINT circuit_breaker_states_pkey PRIMARY KEY (id);


--
-- TOC entry 4210 (class 2606 OID 17166)
-- Name: circuit_breaker_states circuit_breaker_states_service_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.circuit_breaker_states
    ADD CONSTRAINT circuit_breaker_states_service_name_key UNIQUE (service_name);


--
-- TOC entry 4120 (class 2606 OID 16589)
-- Name: configuracoes_sistema configuracoes_sistema_chave_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes_sistema
    ADD CONSTRAINT configuracoes_sistema_chave_key UNIQUE (chave);


--
-- TOC entry 4122 (class 2606 OID 16587)
-- Name: configuracoes_sistema configuracoes_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes_sistema
    ADD CONSTRAINT configuracoes_sistema_pkey PRIMARY KEY (id);


--
-- TOC entry 4216 (class 2606 OID 17195)
-- Name: familiares familiares_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.familiares
    ADD CONSTRAINT familiares_pkey PRIMARY KEY (id);


--
-- TOC entry 4184 (class 2606 OID 16970)
-- Name: faturamento_consumo faturamento_consumo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faturamento_consumo
    ADD CONSTRAINT faturamento_consumo_pkey PRIMARY KEY (id);


--
-- TOC entry 4204 (class 2606 OID 17152)
-- Name: funcoes funcoes_nome_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcoes
    ADD CONSTRAINT funcoes_nome_key UNIQUE (nome);


--
-- TOC entry 4206 (class 2606 OID 17150)
-- Name: funcoes funcoes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funcoes
    ADD CONSTRAINT funcoes_pkey PRIMARY KEY (id);


--
-- TOC entry 4132 (class 2606 OID 16642)
-- Name: function_definitions function_definitions_nome_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.function_definitions
    ADD CONSTRAINT function_definitions_nome_key UNIQUE (nome);


--
-- TOC entry 4134 (class 2606 OID 16640)
-- Name: function_definitions function_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.function_definitions
    ADD CONSTRAINT function_definitions_pkey PRIMARY KEY (id);


--
-- TOC entry 4155 (class 2606 OID 16784)
-- Name: historico_ligacoes historico_ligacoes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_ligacoes
    ADD CONSTRAINT historico_ligacoes_pkey PRIMARY KEY (id);


--
-- TOC entry 4218 (class 2606 OID 17212)
-- Name: historico historico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico
    ADD CONSTRAINT historico_pkey PRIMARY KEY (id);


--
-- TOC entry 4138 (class 2606 OID 16690)
-- Name: idosos idosos_cpf_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos
    ADD CONSTRAINT idosos_cpf_key UNIQUE (cpf);


--
-- TOC entry 4190 (class 2606 OID 17029)
-- Name: idosos_legado_digital idosos_legado_digital_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_legado_digital
    ADD CONSTRAINT idosos_legado_digital_pkey PRIMARY KEY (id);


--
-- TOC entry 4177 (class 2606 OID 16916)
-- Name: idosos_memoria idosos_memoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_memoria
    ADD CONSTRAINT idosos_memoria_pkey PRIMARY KEY (id);


--
-- TOC entry 4180 (class 2606 OID 16933)
-- Name: idosos_perfil_clinico idosos_perfil_clinico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_perfil_clinico
    ADD CONSTRAINT idosos_perfil_clinico_pkey PRIMARY KEY (idoso_id);


--
-- TOC entry 4140 (class 2606 OID 16688)
-- Name: idosos idosos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos
    ADD CONSTRAINT idosos_pkey PRIMARY KEY (id);


--
-- TOC entry 4175 (class 2606 OID 16890)
-- Name: medicamentos medicamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicamentos
    ADD CONSTRAINT medicamentos_pkey PRIMARY KEY (id);


--
-- TOC entry 4147 (class 2606 OID 16706)
-- Name: membros_familia membros_familia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membros_familia
    ADD CONSTRAINT membros_familia_pkey PRIMARY KEY (id);


--
-- TOC entry 4198 (class 2606 OID 17127)
-- Name: pagamentos pagamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagamentos
    ADD CONSTRAINT pagamentos_pkey PRIMARY KEY (id);


--
-- TOC entry 4128 (class 2606 OID 16616)
-- Name: prompt_templates prompt_templates_nome_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompt_templates
    ADD CONSTRAINT prompt_templates_nome_key UNIQUE (nome);


--
-- TOC entry 4130 (class 2606 OID 16614)
-- Name: prompt_templates prompt_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompt_templates
    ADD CONSTRAINT prompt_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 4200 (class 2606 OID 17140)
-- Name: prompts prompts_nome_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_nome_key UNIQUE (nome);


--
-- TOC entry 4202 (class 2606 OID 17138)
-- Name: prompts prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_pkey PRIMARY KEY (id);


--
-- TOC entry 4171 (class 2606 OID 16867)
-- Name: protocolo_etapas protocolo_etapas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolo_etapas
    ADD CONSTRAINT protocolo_etapas_pkey PRIMARY KEY (id);


--
-- TOC entry 4169 (class 2606 OID 16847)
-- Name: protocolos_alerta protocolos_alerta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolos_alerta
    ADD CONSTRAINT protocolos_alerta_pkey PRIMARY KEY (id);


--
-- TOC entry 4192 (class 2606 OID 17050)
-- Name: psicologia_insights psicologia_insights_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.psicologia_insights
    ADD CONSTRAINT psicologia_insights_pkey PRIMARY KEY (id);


--
-- TOC entry 4212 (class 2606 OID 17180)
-- Name: rate_limits rate_limits_endpoint_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rate_limits
    ADD CONSTRAINT rate_limits_endpoint_key UNIQUE (endpoint);


--
-- TOC entry 4214 (class 2606 OID 17178)
-- Name: rate_limits rate_limits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rate_limits
    ADD CONSTRAINT rate_limits_pkey PRIMARY KEY (id);


--
-- TOC entry 4196 (class 2606 OID 17085)
-- Name: sinais_vitais sinais_vitais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sinais_vitais
    ADD CONSTRAINT sinais_vitais_pkey PRIMARY KEY (id);


--
-- TOC entry 4220 (class 2606 OID 24774)
-- Name: timeline timeline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline
    ADD CONSTRAINT timeline_pkey PRIMARY KEY (id);


--
-- TOC entry 4194 (class 2606 OID 17067)
-- Name: topicos_afetivos topicos_afetivos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topicos_afetivos
    ADD CONSTRAINT topicos_afetivos_pkey PRIMARY KEY (id);


--
-- TOC entry 4150 (class 1259 OID 16757)
-- Name: idx_agendamento_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agendamento_data ON public.agendamentos USING btree (data_hora_agendada);


--
-- TOC entry 4151 (class 1259 OID 16756)
-- Name: idx_agendamento_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agendamento_idoso ON public.agendamentos USING btree (idoso_id);


--
-- TOC entry 4152 (class 1259 OID 16759)
-- Name: idx_agendamento_proxima_tentativa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agendamento_proxima_tentativa ON public.agendamentos USING btree (proxima_tentativa) WHERE ((status)::text = 'aguardando_retry'::text);


--
-- TOC entry 4153 (class 1259 OID 16758)
-- Name: idx_agendamento_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agendamento_status ON public.agendamentos USING btree (status);


--
-- TOC entry 4164 (class 1259 OID 16833)
-- Name: idx_alerta_enviado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerta_enviado ON public.alertas USING btree (enviado);


--
-- TOC entry 4165 (class 1259 OID 16831)
-- Name: idx_alerta_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerta_idoso ON public.alertas USING btree (idoso_id);


--
-- TOC entry 4166 (class 1259 OID 16834)
-- Name: idx_alerta_resolvido; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerta_resolvido ON public.alertas USING btree (resolvido);


--
-- TOC entry 4167 (class 1259 OID 16832)
-- Name: idx_alerta_severidade; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerta_severidade ON public.alertas USING btree (severidade) WHERE (NOT resolvido);


--
-- TOC entry 4187 (class 1259 OID 16988)
-- Name: idx_audit_acao; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_acao ON public.audit_logs USING btree (acao);


--
-- TOC entry 4188 (class 1259 OID 16989)
-- Name: idx_audit_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_usuario ON public.audit_logs USING btree (usuario_email);


--
-- TOC entry 4123 (class 1259 OID 16591)
-- Name: idx_config_categoria; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_config_categoria ON public.configuracoes_sistema USING btree (categoria) WHERE (ativa = true);


--
-- TOC entry 4124 (class 1259 OID 16590)
-- Name: idx_config_chave; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_config_chave ON public.configuracoes_sistema USING btree (chave) WHERE (ativa = true);


--
-- TOC entry 4145 (class 1259 OID 16717)
-- Name: idx_familia_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_familia_idoso ON public.membros_familia USING btree (idoso_id);


--
-- TOC entry 4135 (class 1259 OID 16643)
-- Name: idx_function_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_function_nome ON public.function_definitions USING btree (nome) WHERE (ativa = true);


--
-- TOC entry 4136 (class 1259 OID 16644)
-- Name: idx_function_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_function_tipo ON public.function_definitions USING btree (tipo_tarefa) WHERE (ativa = true);


--
-- TOC entry 4156 (class 1259 OID 16795)
-- Name: idx_historico_agendamento; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_agendamento ON public.historico_ligacoes USING btree (agendamento_id);


--
-- TOC entry 4157 (class 1259 OID 16798)
-- Name: idx_historico_call_sid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_call_sid ON public.historico_ligacoes USING btree (twilio_call_sid);


--
-- TOC entry 4158 (class 1259 OID 16797)
-- Name: idx_historico_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_data ON public.historico_ligacoes USING btree (inicio_chamada);


--
-- TOC entry 4159 (class 1259 OID 16796)
-- Name: idx_historico_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_idoso ON public.historico_ligacoes USING btree (idoso_id);


--
-- TOC entry 4160 (class 1259 OID 24811)
-- Name: idx_historico_sentimento; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_sentimento ON public.historico_ligacoes USING btree (sentimento);


--
-- TOC entry 4161 (class 1259 OID 24810)
-- Name: idx_historico_urgencia; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_historico_urgencia ON public.historico_ligacoes USING btree (urgencia);


--
-- TOC entry 4141 (class 1259 OID 16721)
-- Name: idx_idoso_ativo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_idoso_ativo ON public.idosos USING btree (ativo);


--
-- TOC entry 4142 (class 1259 OID 16720)
-- Name: idx_idoso_cpf; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_idoso_cpf ON public.idosos USING btree (cpf) WHERE (cpf IS NOT NULL);


--
-- TOC entry 4143 (class 1259 OID 16719)
-- Name: idx_idoso_telefone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_idoso_telefone ON public.idosos USING btree (telefone) WHERE (ativo = true);


--
-- TOC entry 4144 (class 1259 OID 24793)
-- Name: idx_idosos_device_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_idosos_device_token ON public.idosos USING btree (device_token);


--
-- TOC entry 4172 (class 1259 OID 16896)
-- Name: idx_medicamento_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medicamento_idoso ON public.medicamentos USING btree (idoso_id) WHERE (ativo = true);


--
-- TOC entry 4173 (class 1259 OID 16897)
-- Name: idx_medicamento_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medicamento_nome ON public.medicamentos USING btree (nome);


--
-- TOC entry 4178 (class 1259 OID 16922)
-- Name: idx_memoria_idoso; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_memoria_idoso ON public.idosos_memoria USING btree (idoso_id);


--
-- TOC entry 4125 (class 1259 OID 16617)
-- Name: idx_prompt_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prompt_nome ON public.prompt_templates USING btree (nome) WHERE (ativo = true);


--
-- TOC entry 4126 (class 1259 OID 16618)
-- Name: idx_prompt_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prompt_tipo ON public.prompt_templates USING btree (tipo) WHERE (ativo = true);


--
-- TOC entry 4246 (class 2620 OID 16760)
-- Name: agendamentos trigger_agendamento_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_agendamento_timestamp BEFORE UPDATE ON public.agendamentos FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4251 (class 2620 OID 16956)
-- Name: assinaturas_entidade trigger_assinatura_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_assinatura_timestamp BEFORE UPDATE ON public.assinaturas_entidade FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4241 (class 2620 OID 16593)
-- Name: configuracoes_sistema trigger_config_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_config_timestamp BEFORE UPDATE ON public.configuracoes_sistema FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4245 (class 2620 OID 16718)
-- Name: membros_familia trigger_familia_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_familia_timestamp BEFORE UPDATE ON public.membros_familia FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4243 (class 2620 OID 16645)
-- Name: function_definitions trigger_function_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_function_timestamp BEFORE UPDATE ON public.function_definitions FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4244 (class 2620 OID 16722)
-- Name: idosos trigger_idoso_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_idoso_timestamp BEFORE UPDATE ON public.idosos FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4248 (class 2620 OID 16898)
-- Name: medicamentos trigger_medicamento_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_medicamento_timestamp BEFORE UPDATE ON public.medicamentos FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4249 (class 2620 OID 16923)
-- Name: idosos_memoria trigger_memoria_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_memoria_timestamp BEFORE UPDATE ON public.idosos_memoria FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4250 (class 2620 OID 16939)
-- Name: idosos_perfil_clinico trigger_perfil_clinico_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_perfil_clinico_timestamp BEFORE UPDATE ON public.idosos_perfil_clinico FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4242 (class 2620 OID 16619)
-- Name: prompt_templates trigger_prompt_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_prompt_timestamp BEFORE UPDATE ON public.prompt_templates FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4247 (class 2620 OID 16873)
-- Name: protocolos_alerta trigger_protocolo_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_protocolo_timestamp BEFORE UPDATE ON public.protocolos_alerta FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- TOC entry 4223 (class 2606 OID 16751)
-- Name: agendamentos agendamentos_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agendamentos
    ADD CONSTRAINT agendamentos_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4226 (class 2606 OID 16821)
-- Name: alertas alertas_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4227 (class 2606 OID 16826)
-- Name: alertas alertas_ligacao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_ligacao_id_fkey FOREIGN KEY (ligacao_id) REFERENCES public.historico_ligacoes(id) ON DELETE SET NULL;


--
-- TOC entry 4238 (class 2606 OID 17196)
-- Name: familiares familiares_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.familiares
    ADD CONSTRAINT familiares_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id);


--
-- TOC entry 4233 (class 2606 OID 16971)
-- Name: faturamento_consumo faturamento_consumo_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faturamento_consumo
    ADD CONSTRAINT faturamento_consumo_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4239 (class 2606 OID 17213)
-- Name: historico historico_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico
    ADD CONSTRAINT historico_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id);


--
-- TOC entry 4224 (class 2606 OID 16785)
-- Name: historico_ligacoes historico_ligacoes_agendamento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_ligacoes
    ADD CONSTRAINT historico_ligacoes_agendamento_id_fkey FOREIGN KEY (agendamento_id) REFERENCES public.agendamentos(id) ON DELETE CASCADE;


--
-- TOC entry 4225 (class 2606 OID 16790)
-- Name: historico_ligacoes historico_ligacoes_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_ligacoes
    ADD CONSTRAINT historico_ligacoes_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4234 (class 2606 OID 17030)
-- Name: idosos_legado_digital idosos_legado_digital_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_legado_digital
    ADD CONSTRAINT idosos_legado_digital_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4231 (class 2606 OID 16917)
-- Name: idosos_memoria idosos_memoria_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_memoria
    ADD CONSTRAINT idosos_memoria_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4232 (class 2606 OID 16934)
-- Name: idosos_perfil_clinico idosos_perfil_clinico_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.idosos_perfil_clinico
    ADD CONSTRAINT idosos_perfil_clinico_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4230 (class 2606 OID 16891)
-- Name: medicamentos medicamentos_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicamentos
    ADD CONSTRAINT medicamentos_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4221 (class 2606 OID 16707)
-- Name: membros_familia membros_familia_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membros_familia
    ADD CONSTRAINT membros_familia_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4222 (class 2606 OID 16712)
-- Name: membros_familia membros_familia_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membros_familia
    ADD CONSTRAINT membros_familia_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.membros_familia(id);


--
-- TOC entry 4229 (class 2606 OID 16868)
-- Name: protocolo_etapas protocolo_etapas_protocolo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolo_etapas
    ADD CONSTRAINT protocolo_etapas_protocolo_id_fkey FOREIGN KEY (protocolo_id) REFERENCES public.protocolos_alerta(id) ON DELETE CASCADE;


--
-- TOC entry 4228 (class 2606 OID 16848)
-- Name: protocolos_alerta protocolos_alerta_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.protocolos_alerta
    ADD CONSTRAINT protocolos_alerta_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4235 (class 2606 OID 17051)
-- Name: psicologia_insights psicologia_insights_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.psicologia_insights
    ADD CONSTRAINT psicologia_insights_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4237 (class 2606 OID 17086)
-- Name: sinais_vitais sinais_vitais_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sinais_vitais
    ADD CONSTRAINT sinais_vitais_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4240 (class 2606 OID 24775)
-- Name: timeline timeline_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline
    ADD CONSTRAINT timeline_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4236 (class 2606 OID 17068)
-- Name: topicos_afetivos topicos_afetivos_idoso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topicos_afetivos
    ADD CONSTRAINT topicos_afetivos_idoso_id_fkey FOREIGN KEY (idoso_id) REFERENCES public.idosos(id) ON DELETE CASCADE;


--
-- TOC entry 4463 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;


-- Completed on 2025-12-28 10:41:33

--
-- PostgreSQL database dump complete
--

\unrestrict B6Chw9QPdLa4Oz2wzJ5bytSeAmq9JhuW5qHle8RE1gSjx1Pn7NFnYyCDwBZLt6X

