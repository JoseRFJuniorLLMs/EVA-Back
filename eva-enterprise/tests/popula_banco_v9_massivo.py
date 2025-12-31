#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular banco de dados PostgreSQL com dados de teste
Gera 100 registros para cada tabela respeitando as relações de chaves estrangeiras
web2ajax@gmail.com
"""

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
from datetime import datetime, timedelta
import json

# Configurar Faker para português do Brasil
fake = Faker('pt_BR')

# Configurações do banco de dados
DB_CONFIG = {
    'host': '34.39.249.108',
    'database': 'eva-db',
    'user': 'postgres',
    'password': 'Debian23@',
    'port': 5432
    #DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:Debian23%40@34.89.62.186:5432/eva
}

# Número de registros por tabela
NUM_REGISTROS = 100


def conectar_banco():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexão estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None


def gerar_idosos(conn, num=NUM_REGISTROS):
    """Gera registros para a tabela idosos"""
    print(f"\n📝 Gerando {num} idosos...")
    cursor = conn.cursor()

    idosos = []
    for i in range(num):
        nome = fake.name()
        data_nascimento = fake.date_of_birth(minimum_age=60, maximum_age=95)
        telefone = fake.phone_number()
        email = fake.email() if random.random() > 0.3 else None
        endereco = fake.address().replace('\n', ', ')

        preferencias = {
            "idioma": "pt-BR",
            "tom_voz": random.choice(["amigavel", "formal", "casual"]),
            "volume": random.choice(["baixo", "medio", "alto"]),
            "temas_interesse": random.sample(["familia", "saude", "hobbies", "musica", "esportes"],
                                             k=random.randint(2, 4))
        }

        idosos.append((
            nome,
            data_nascimento,
            telefone,
            email,
            endereco,
            random.choice(['ativo', 'inativo', 'suspenso']),
            json.dumps(preferencias),
            random.choice([True, False]),
            random.choice([None, fake.uuid4()]),
            fake.text(max_nb_chars=200) if random.random() > 0.5 else None
        ))

    query = """
        INSERT INTO idosos (nome, data_nascimento, telefone, email, endereco, 
                           status, preferencias, consentimento_gravacao, 
                           gemini_preferences_id, observacoes)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, idosos, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} idosos criados")
    return ids


def gerar_membros_familia(conn, idoso_ids):
    """Gera registros para a tabela membros_familia"""
    print(f"\n📝 Gerando membros da família...")
    cursor = conn.cursor()

    membros = []
    parent_ids = []

    # Primeiro, criar membros sem parent_id
    for idoso_id in idoso_ids:
        num_membros = random.randint(1, 4)
        for _ in range(num_membros):
            membros.append((
                idoso_id,
                fake.name(),
                random.choice(['filho', 'filha', 'neto', 'neta', 'sobrinho', 'sobrinha', 'outro']),
                fake.phone_number(),
                fake.email() if random.random() > 0.3 else None,
                random.choice([True, False]),
                None  # parent_id será None na primeira inserção
            ))

    query = """
        INSERT INTO membros_familia (idoso_id, nome, relacao, telefone, email, 
                                    contato_emergencia, parent_id)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, membros[:len(idoso_ids) * 2])
    parent_ids = [row[0] for row in cursor.fetchall()]

    # Agora criar alguns membros com parent_id
    membros_com_parent = []
    for _ in range(min(50, len(parent_ids))):
        parent_id = random.choice(parent_ids)
        idoso_id = random.choice(idoso_ids)
        membros_com_parent.append((
            idoso_id,
            fake.name(),
            random.choice(['filho', 'filha', 'neto', 'neta']),
            fake.phone_number(),
            fake.email() if random.random() > 0.3 else None,
            random.choice([True, False]),
            parent_id
        ))

    if membros_com_parent:
        execute_values(cursor, query, membros_com_parent)
        todos_ids = parent_ids + [row[0] for row in cursor.fetchall()]
    else:
        todos_ids = parent_ids

    conn.commit()
    cursor.close()

    print(f"✅ {len(todos_ids)} membros da família criados")
    return todos_ids


def gerar_agendamentos(conn, idoso_ids):
    """Gera registros para a tabela agendamentos"""
    print(f"\n📝 Gerando agendamentos...")
    cursor = conn.cursor()

    agendamentos = []
    tipos = ['lembrete_medicamento', 'check_bem_estar', 'acompanhamento_pos_consulta', 'atividade_fisica']
    status_list = ['agendado', 'em_andamento', 'concluido', 'falhou', 'aguardando_retry',
                   'falhou_definitivamente', 'cancelado', 'nao_atendido']
    prioridades = ['alta', 'normal', 'baixa']

    for idoso_id in idoso_ids:
        num_agendamentos = random.randint(1, 3)
        for _ in range(num_agendamentos):
            tipo = random.choice(tipos)
            data_agendada = fake.date_time_between(start_date='-30d', end_date='+30d')
            status = random.choice(status_list)

            dados_tarefa = {
                "descricao": fake.sentence(),
                "detalhes": fake.text(max_nb_chars=100)
            }

            if tipo == 'lembrete_medicamento':
                dados_tarefa["medicamentos"] = [
                    {"nome": fake.word(), "dosagem": f"{random.randint(1, 3)} comprimidos"}
                ]

            agendamentos.append((
                idoso_id,
                tipo,
                data_agendada,
                data_agendada + timedelta(hours=1) if status == 'concluido' else None,
                random.randint(1, 5),
                random.randint(10, 30),
                random.randint(0, 3),
                data_agendada + timedelta(minutes=15) if status == 'aguardando_retry' else None,
                random.choice(['alert_family', 'emergency_contact', 'none']),
                status,
                json.dumps(dados_tarefa),
                random.choice(prioridades),
                random.choice(['sistema', 'admin', 'familiar'])
            ))

    query = """
        INSERT INTO agendamentos (idoso_id, tipo, data_hora_agendada, data_hora_realizada,
                                 max_retries, retry_interval_minutes, tentativas_realizadas,
                                 proxima_tentativa, escalation_policy, status, dados_tarefa,
                                 prioridade, criado_por)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, agendamentos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} agendamentos criados")
    return ids


def gerar_historico_ligacoes(conn, idoso_ids, agendamento_ids):
    """Gera registros para a tabela historico_ligacoes"""
    print(f"\n📝 Gerando histórico de ligações...")
    cursor = conn.cursor()

    ligacoes = []
    resultados = ['atendida', 'nao_atendida', 'ocupado', 'erro', 'falha_sistema']

    for i in range(len(idoso_ids) * 2):
        idoso_id = random.choice(idoso_ids)
        agendamento_id = random.choice(agendamento_ids) if random.random() > 0.3 else None

        data_ligacao = fake.date_time_between(start_date='-60d', end_date='now')
        duracao = random.randint(30, 600) if random.random() > 0.3 else None
        resultado = random.choice(resultados)

        contexto = {
            "qualidade_audio": random.choice(["boa", "media", "ruim"]),
            "ambiente": random.choice(["silencioso", "barulhento", "moderado"])
        }

        ligacoes.append((
            idoso_id,
            agendamento_id,
            data_ligacao,
            duracao,
            resultado,
            fake.text(max_nb_chars=200) if random.random() > 0.5 else None,
            json.dumps(contexto)
        ))

    query = """
        INSERT INTO historico_ligacoes (idoso_id, agendamento_id, data_ligacao,
                                       duracao_segundos, resultado, observacoes, contexto)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, ligacoes)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} ligações criadas")
    return ids


def gerar_alertas(conn, idoso_ids, ligacao_ids):
    """Gera registros para a tabela alertas"""
    print(f"\n📝 Gerando alertas...")
    cursor = conn.cursor()

    alertas = []
    tipos = ['medicamento_nao_tomado', 'ligacao_nao_atendida', 'bem_estar_preocupante',
             'emergencia', 'anomalia_comportamental']
    severidades = ['baixa', 'media', 'alta', 'critica']

    for idoso_id in idoso_ids:
        num_alertas = random.randint(0, 3)
        for _ in range(num_alertas):
            tipo = random.choice(tipos)
            severidade = random.choice(severidades)
            ligacao_id = random.choice(ligacao_ids) if random.random() > 0.5 else None

            destinatarios = {
                "emails": [fake.email() for _ in range(random.randint(1, 3))],
                "telefones": [fake.phone_number() for _ in range(random.randint(1, 2))]
            }

            contexto = {
                "detalhes": fake.text(max_nb_chars=100),
                "automatico": random.choice([True, False])
            }

            alertas.append((
                idoso_id,
                ligacao_id,
                tipo,
                severidade,
                fake.sentence(),
                json.dumps(contexto),
                json.dumps(destinatarios),
                random.choice([True, False]),
                random.choice([True, False]),
                datetime.now() if random.random() > 0.5 else None
            ))

    query = """
        INSERT INTO alertas (idoso_id, ligacao_id, tipo, severidade, mensagem,
                           contexto_adicional, destinatarios, enviado, visualizado,
                           data_envio)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, alertas)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} alertas criados")
    return ids


def gerar_protocolos_alerta(conn, idoso_ids):
    """Gera registros para a tabela protocolos_alerta"""
    print(f"\n📝 Gerando protocolos de alerta...")
    cursor = conn.cursor()

    protocolos = []
    tipos = ['medicamento_nao_tomado', 'ligacao_nao_atendida', 'bem_estar_preocupante']

    for idoso_id in idoso_ids[:50]:  # Nem todos os idosos têm protocolo
        tipo = random.choice(tipos)

        configuracao = {
            "tempo_espera": random.randint(15, 60),
            "tentativas": random.randint(2, 5),
            "escalonamento": random.choice([True, False])
        }

        protocolos.append((
            idoso_id,
            tipo,
            f"Protocolo {tipo} para {idoso_id}",
            json.dumps(configuracao),
            random.choice([True, False])
        ))

    query = """
        INSERT INTO protocolos_alerta (idoso_id, tipo_alerta, nome, configuracao, ativo)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, protocolos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} protocolos criados")
    return ids


def gerar_protocolo_etapas(conn, protocolo_ids):
    """Gera registros para a tabela protocolo_etapas"""
    print(f"\n📝 Gerando etapas de protocolo...")
    cursor = conn.cursor()

    etapas = []
    for protocolo_id in protocolo_ids:
        num_etapas = random.randint(2, 5)
        for ordem in range(1, num_etapas + 1):
            parametros = {
                "delay_minutos": random.randint(5, 30),
                "mensagem_template": fake.sentence()
            }

            etapas.append((
                protocolo_id,
                ordem,
                random.choice(['notificar_familiar', 'enviar_email', 'ligar_novamente', 'acionar_emergencia']),
                fake.text(max_nb_chars=100),
                json.dumps(parametros)
            ))

    query = """
        INSERT INTO protocolo_etapas (protocolo_id, ordem, acao, descricao, parametros)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, etapas)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} etapas de protocolo criadas")
    return ids


def gerar_medicamentos(conn, idoso_ids):
    """Gera registros para a tabela medicamentos"""
    print(f"\n📝 Gerando medicamentos...")
    cursor = conn.cursor()

    medicamentos = []
    nomes_medicamentos = ['Losartana', 'Atenolol', 'Metformina', 'Sinvastatina',
                          'Omeprazol', 'AAS', 'Insulina', 'Captopril']

    for idoso_id in idoso_ids:
        num_medicamentos = random.randint(1, 4)
        for _ in range(num_medicamentos):
            horarios = [
                f"{random.randint(6, 9):02d}:00",
                f"{random.randint(12, 14):02d}:00",
                f"{random.randint(18, 21):02d}:00"
            ]

            medicamentos.append((
                idoso_id,
                random.choice(nomes_medicamentos),
                f"{random.randint(5, 500)}mg",
                random.choice(horarios[:random.randint(1, 3)]),
                fake.text(max_nb_chars=100) if random.random() > 0.5 else None,
                random.choice([True, False])
            ))

    query = """
        INSERT INTO medicamentos (idoso_id, nome, dosagem, horarios, instrucoes_especiais, ativo)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, medicamentos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} medicamentos criados")
    return ids


def gerar_idosos_memoria(conn, idoso_ids):
    """Gera registros para a tabela idosos_memoria"""
    print(f"\n📝 Gerando memórias dos idosos...")
    cursor = conn.cursor()

    memorias = []
    for idoso_id in idoso_ids[:70]:  # Nem todos têm memórias registradas
        num_memorias = random.randint(1, 3)
        for _ in range(num_memorias):
            contexto = {
                "epoca": random.choice(["infancia", "juventude", "adulto", "recente"]),
                "pessoas": [fake.name() for _ in range(random.randint(1, 3))]
            }

            memorias.append((
                idoso_id,
                random.choice(['historia_pessoal', 'preferencia', 'familiar', 'evento_importante']),
                fake.text(max_nb_chars=200),
                json.dumps(contexto),
                fake.date_between(start_date='-10y', end_date='today')
            ))

    query = """
        INSERT INTO idosos_memoria (idoso_id, tipo, conteudo, contexto, data_referencia)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, memorias)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} memórias criadas")
    return ids


def gerar_idosos_perfil_clinico(conn, idoso_ids):
    """Gera registros para a tabela idosos_perfil_clinico"""
    print(f"\n📝 Gerando perfis clínicos...")
    cursor = conn.cursor()

    perfis = []
    doencas = ['Hipertensão', 'Diabetes', 'Artrite', 'Osteoporose', 'Alzheimer']
    alergias = ['Penicilina', 'Dipirona', 'AAS', 'Lactose', 'Glúten']

    for idoso_id in idoso_ids:
        num_doencas = random.randint(0, 3)
        num_alergias = random.randint(0, 2)

        perfis.append((
            idoso_id,
            random.sample(doencas, num_doencas) if num_doencas > 0 else [],
            random.sample(alergias, num_alergias) if num_alergias > 0 else [],
            fake.text(max_nb_chars=200) if random.random() > 0.5 else None,
            random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            fake.name() if random.random() > 0.5 else None,
            fake.phone_number() if random.random() > 0.5 else None
        ))

    query = """
        INSERT INTO idosos_perfil_clinico (idoso_id, condicoes_cronicas, alergias, 
                                          observacoes_medicas, tipo_sanguineo, 
                                          medico_responsavel, telefone_medico)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, perfis)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} perfis clínicos criados")
    return ids


def gerar_faturamento_consumo(conn, idoso_ids):
    """Gera registros para a tabela faturamento_consumo"""
    print(f"\n📝 Gerando registros de faturamento...")
    cursor = conn.cursor()

    faturamentos = []
    for idoso_id in idoso_ids:
        num_meses = random.randint(3, 12)
        for i in range(num_meses):
            mes = datetime.now() - timedelta(days=30 * i)

            faturamentos.append((
                idoso_id,
                mes.replace(day=1),
                random.randint(10, 100),
                random.randint(30, 300),
                random.uniform(50.0, 500.0),
                random.choice(['pendente', 'pago', 'vencido'])
            ))

    query = """
        INSERT INTO faturamento_consumo (idoso_id, periodo_inicio, total_ligacoes,
                                        duracao_total_minutos, valor_total, status_pagamento)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, faturamentos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} registros de faturamento criados")
    return ids


def gerar_idosos_legado_digital(conn, idoso_ids):
    """Gera registros para a tabela idosos_legado_digital"""
    print(f"\n📝 Gerando legados digitais...")
    cursor = conn.cursor()

    legados = []
    tipos = ['mensagem', 'video', 'audio', 'documento']

    for idoso_id in idoso_ids[:40]:  # Nem todos têm legado digital
        num_legados = random.randint(1, 3)
        for _ in range(num_legados):
            tipo = random.choice(tipos)

            metadados = {
                "formato": random.choice(["mp4", "mp3", "txt", "pdf"]),
                "tamanho_kb": random.randint(100, 50000)
            }

            legados.append((
                idoso_id,
                tipo,
                fake.sentence(),
                fake.text(max_nb_chars=300) if tipo in ['mensagem', 'documento'] else None,
                fake.url() if tipo in ['video', 'audio'] else None,
                json.dumps(metadados),
                [fake.name() for _ in range(random.randint(1, 4))],
                fake.date_between(start_date='today', end_date='+5y') if random.random() > 0.5 else None
            ))

    query = """
        INSERT INTO idosos_legado_digital (idoso_id, tipo, titulo, conteudo, url_arquivo,
                                          metadados, destinatarios, data_disponibilizacao)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, legados)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} legados digitais criados")
    return ids


def gerar_psicologia_insights(conn, idoso_ids):
    """Gera registros para a tabela psicologia_insights"""
    print(f"\n📝 Gerando insights psicológicos...")
    cursor = conn.cursor()

    insights = []
    categorias = ['humor', 'memoria', 'social', 'cognitivo', 'emocional']

    for idoso_id in idoso_ids[:60]:
        num_insights = random.randint(1, 4)
        for _ in range(num_insights):
            analise = {
                "score": random.uniform(0, 10),
                "tendencia": random.choice(["positiva", "neutra", "negativa"]),
                "fatores": random.sample(["isolamento", "saude", "familia", "rotina"], k=2)
            }

            insights.append((
                idoso_id,
                random.choice(categorias),
                fake.text(max_nb_chars=200),
                json.dumps(analise),
                random.uniform(0, 10),
                fake.date_between(start_date='-30d', end_date='today')
            ))

    query = """
        INSERT INTO psicologia_insights (idoso_id, categoria, observacao, analise_ia,
                                        score_confianca, data_observacao)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, insights)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} insights psicológicos criados")
    return ids


def gerar_topicos_afetivos(conn, idoso_ids):
    """Gera registros para a tabela topicos_afetivos"""
    print(f"\n📝 Gerando tópicos afetivos...")
    cursor = conn.cursor()

    topicos = []
    tipos = ['alegria', 'tristeza', 'preocupacao', 'nostalgia', 'gratidao']

    for idoso_id in idoso_ids[:50]:
        num_topicos = random.randint(1, 3)
        for _ in range(num_topicos):
            contexto = {
                "pessoas_mencionadas": [fake.name() for _ in range(random.randint(0, 3))],
                "locais": [fake.city() for _ in range(random.randint(0, 2))]
            }

            topicos.append((
                idoso_id,
                fake.word(),
                random.choice(tipos),
                fake.text(max_nb_chars=200),
                random.randint(1, 10),
                json.dumps(contexto),
                fake.date_between(start_date='-60d', end_date='today')
            ))

    query = """
        INSERT INTO topicos_afetivos (idoso_id, topico, sentimento, descricao,
                                     frequencia_mencoes, contexto, ultima_mencao)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, topicos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} tópicos afetivos criados")
    return ids


def gerar_sinais_vitais(conn, idoso_ids):
    """Gera registros para a tabela sinais_vitais"""
    print(f"\n📝 Gerando sinais vitais...")
    cursor = conn.cursor()

    sinais = []
    for idoso_id in idoso_ids:
        num_registros = random.randint(5, 20)
        for _ in range(num_registros):
            data_medicao = fake.date_time_between(start_date='-60d', end_date='now')

            sinais.append((
                idoso_id,
                data_medicao,
                random.randint(60, 180),
                random.randint(40, 100),
                random.uniform(35.5, 38.5),
                random.randint(50, 120),
                random.randint(85, 100) if random.random() > 0.3 else None,
                random.uniform(50.0, 120.0) if random.random() > 0.5 else None,
                fake.text(max_nb_chars=100) if random.random() > 0.7 else None
            ))

    query = """
        INSERT INTO sinais_vitais (idoso_id, data_hora, pressao_sistolica, pressao_diastolica,
                                  temperatura, frequencia_cardiaca, saturacao_oxigenio,
                                  glicemia, observacoes)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, sinais)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} registros de sinais vitais criados")
    return ids


def gerar_configuracoes_sistema(conn):
    """Gera registros para a tabela configuracoes_sistema"""
    print(f"\n📝 Gerando configurações do sistema...")
    cursor = conn.cursor()

    configs = [
        ('max_tentativas_ligacao', '3', 'Número máximo de tentativas de ligação', 'sistema', True),
        ('intervalo_retry_minutos', '15', 'Intervalo entre tentativas em minutos', 'sistema', True),
        ('duracao_maxima_ligacao', '600', 'Duração máxima da ligação em segundos', 'sistema', True),
        ('horario_inicio_ligacoes', '08:00', 'Horário de início das ligações', 'horario', True),
        ('horario_fim_ligacoes', '20:00', 'Horário de término das ligações', 'horario', True),
        ('email_notificacao_admin', 'admin@sistema.com', 'Email para notificações administrativas', 'notificacao',
         True),
        ('habilitar_gravacao_audio', 'true', 'Habilitar gravação de áudio das ligações', 'privacidade', True),
        ('dias_retencao_dados', '365', 'Dias de retenção de dados históricos', 'dados', True),
        ('nivel_log', 'INFO', 'Nível de log do sistema', 'sistema', True),
        ('gemini_api_key', 'AIzaSy***********', 'Chave API do Gemini', 'integracao', False)
    ]

    query = """
        INSERT INTO configuracoes_sistema (chave, valor, descricao, categoria, ativa)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, configs)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} configurações criadas")
    return ids


def gerar_familiares(conn, idoso_ids):
    """Gera registros para a tabela familiares"""
    print(f"\n📝 Gerando familiares...")
    cursor = conn.cursor()

    familiares = []
    for idoso_id in idoso_ids:
        num_familiares = random.randint(1, 3)
        for _ in range(num_familiares):
            familiares.append((
                idoso_id,
                fake.name(),
                fake.email(),
                fake.phone_number(),
                random.choice(['filho', 'filha', 'neto', 'neta', 'sobrinho', 'sobrinha']),
                random.choice([True, False])
            ))

    query = """
        INSERT INTO familiares (idoso_id, nome, email, telefone, grau_parentesco, ativo)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, familiares)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} familiares criados")
    return ids


def gerar_historico(conn, idoso_ids):
    """Gera registros para a tabela historico"""
    print(f"\n📝 Gerando histórico...")
    cursor = conn.cursor()

    historicos = []
    tipos_evento = ['ligacao_realizada', 'medicamento_tomado', 'alerta_gerado',
                    'perfil_atualizado', 'familiar_adicionado']

    for idoso_id in idoso_ids:
        num_eventos = random.randint(5, 15)
        for _ in range(num_eventos):
            detalhes = {
                "acao": random.choice(["criar", "atualizar", "deletar", "visualizar"]),
                "resultado": random.choice(["sucesso", "falha", "pendente"])
            }

            historicos.append((
                idoso_id,
                random.choice(tipos_evento),
                fake.text(max_nb_chars=150),
                json.dumps(detalhes),
                fake.date_time_between(start_date='-90d', end_date='now')
            ))

    query = """
        INSERT INTO historico (idoso_id, tipo_evento, descricao, detalhes, data_evento)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, historicos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} registros de histórico criados")
    return ids


def gerar_timeline(conn, idoso_ids):
    """Gera registros para a tabela timeline"""
    print(f"\n📝 Gerando timeline...")
    cursor = conn.cursor()

    timelines = []
    tipos_evento = ['medicamento', 'consulta', 'exercicio', 'social', 'alerta']

    for idoso_id in idoso_ids:
        num_eventos = random.randint(10, 30)
        for _ in range(num_eventos):
            metadados = {
                "local": fake.city() if random.random() > 0.5 else None,
                "pessoas": [fake.name() for _ in range(random.randint(0, 2))]
            }

            timelines.append((
                idoso_id,
                random.choice(tipos_evento),
                fake.sentence(),
                fake.text(max_nb_chars=200),
                json.dumps(metadados),
                fake.date_time_between(start_date='-180d', end_date='now')
            ))

    query = """
        INSERT INTO timeline (idoso_id, tipo_evento, titulo, descricao, metadados, data_evento)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, timelines)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} eventos de timeline criados")
    return ids


def gerar_cuidadores(conn, idoso_ids):
    """Gera registros para a tabela cuidadores"""
    print(f"\n📝 Gerando cuidadores...")
    cursor = conn.cursor()

    cuidadores = []
    turnos = ['manha', 'tarde', 'noite', 'integral']

    for idoso_id in idoso_ids[:60]:  # Nem todos têm cuidador
        num_cuidadores = random.randint(1, 2)
        for _ in range(num_cuidadores):
            cuidadores.append((
                idoso_id,
                fake.name(),
                fake.phone_number(),
                fake.email() if random.random() > 0.3 else None,
                random.choice(turnos),
                fake.text(max_nb_chars=150) if random.random() > 0.5 else None,
                random.choice([True, False])
            ))

    query = """
        INSERT INTO cuidadores (idoso_id, nome, telefone, email, turno, observacoes, ativo)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, cuidadores)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} cuidadores criados")
    return ids


def gerar_contatos_emergencia(conn, idoso_ids):
    """Gera registros para a tabela contatos_emergencia"""
    print(f"\n📝 Gerando contatos de emergência...")
    cursor = conn.cursor()

    contatos = []
    tipos = ['familiar', 'medico', 'vizinho', 'cuidador', 'hospital']

    for idoso_id in idoso_ids:
        num_contatos = random.randint(2, 4)
        for ordem in range(1, num_contatos + 1):
            contatos.append((
                idoso_id,
                fake.name(),
                fake.phone_number(),
                fake.email() if random.random() > 0.4 else None,
                random.choice(tipos),
                ordem,
                random.choice([True, False])
            ))

    query = """
        INSERT INTO contatos_emergencia (idoso_id, nome, telefone, email, tipo, prioridade, ativo)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, contatos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} contatos de emergência criados")
    return ids


def gerar_historico_alertas(conn, alerta_ids):
    """Gera registros para a tabela historico_alertas"""
    print(f"\n📝 Gerando histórico de alertas...")
    cursor = conn.cursor()

    historicos = []
    acoes = ['criado', 'visualizado', 'enviado', 'resolvido', 'escalado']
    metodos = ['email', 'sms', 'push', 'telefone']

    for alerta_id in alerta_ids:
        num_eventos = random.randint(1, 4)
        for _ in range(num_eventos):
            historicos.append((
                alerta_id,
                random.choice(acoes),
                random.choice(metodos) if random.random() > 0.5 else None,
                random.choice([True, False]),
                fake.text(max_nb_chars=100) if random.random() > 0.5 else None,
                fake.date_time_between(start_date='-30d', end_date='now')
            ))

    query = """
        INSERT INTO historico_alertas (alerta_id, acao, metodo, sucesso, detalhes, criado_em)
        VALUES %s
        RETURNING id
    """

    execute_values(cursor, query, historicos)
    ids = [row[0] for row in cursor.fetchall()]
    conn.commit()
    cursor.close()

    print(f"✅ {len(ids)} registros de histórico de alertas criados")
    return ids


def popular_banco_completo():
    """Função principal que popula todas as tabelas na ordem correta"""
    print("=" * 60)
    print("🚀 INICIANDO POPULAÇÃO DO BANCO DE DADOS")
    print("=" * 60)

    conn = conectar_banco()
    if not conn:
        return

    try:
        # Tabela principal sem dependências
        idoso_ids = gerar_idosos(conn, NUM_REGISTROS)

        # Tabelas que dependem apenas de idosos
        membro_ids = gerar_membros_familia(conn, idoso_ids)
        agendamento_ids = gerar_agendamentos(conn, idoso_ids)
        medicamento_ids = gerar_medicamentos(conn, idoso_ids)
        memoria_ids = gerar_idosos_memoria(conn, idoso_ids)
        perfil_ids = gerar_idosos_perfil_clinico(conn, idoso_ids)
        faturamento_ids = gerar_faturamento_consumo(conn, idoso_ids)
        legado_ids = gerar_idosos_legado_digital(conn, idoso_ids)
        insight_ids = gerar_psicologia_insights(conn, idoso_ids)
        topico_ids = gerar_topicos_afetivos(conn, idoso_ids)
        sinais_ids = gerar_sinais_vitais(conn, idoso_ids)
        familiar_ids = gerar_familiares(conn, idoso_ids)
        historico_ids = gerar_historico(conn, idoso_ids)
        timeline_ids = gerar_timeline(conn, idoso_ids)
        cuidador_ids = gerar_cuidadores(conn, idoso_ids)
        contato_ids = gerar_contatos_emergencia(conn, idoso_ids)

        # Tabelas que dependem de agendamentos
        ligacao_ids = gerar_historico_ligacoes(conn, idoso_ids, agendamento_ids)

        # Tabelas que dependem de ligações
        alerta_ids = gerar_alertas(conn, idoso_ids, ligacao_ids)

        # Tabelas de protocolos
        protocolo_ids = gerar_protocolos_alerta(conn, idoso_ids)
        etapa_ids = gerar_protocolo_etapas(conn, protocolo_ids)

        # Histórico de alertas
        historico_alerta_ids = gerar_historico_alertas(conn, alerta_ids)

        # Configurações do sistema
        config_ids = gerar_configuracoes_sistema(conn)

        print("\n" + "=" * 60)
        print("✅ POPULAÇÃO DO BANCO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"\n📊 RESUMO:")
        print(f"   • Idosos: {len(idoso_ids)}")
        print(f"   • Membros da Família: {len(membro_ids)}")
        print(f"   • Agendamentos: {len(agendamento_ids)}")
        print(f"   • Ligações: {len(ligacao_ids)}")
        print(f"   • Alertas: {len(alerta_ids)}")
        print(f"   • Protocolos: {len(protocolo_ids)}")
        print(f"   • Medicamentos: {len(medicamento_ids)}")
        print(f"   • Total de registros criados em todas as tabelas!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERRO durante a população: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n🔒 Conexão fechada.")


if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO: Certifique-se de que:")
    print("   1. O PostgreSQL está rodando")
    print("   2. As credenciais no DB_CONFIG estão corretas")
    print("   3. O banco de dados existe e o schema está criado")
    print("\n" + "=" * 60)

    resposta = input("\nDeseja continuar? (s/n): ")
    if resposta.lower() == 's':
        popular_banco_completo()
    else:
        print("❌ Operação cancelada.")