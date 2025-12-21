# tests/test_full_flow.py
import sys
import os

# Adiciona a raiz do projeto ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import asyncio
from datetime import datetime, timedelta
from database.connection import SessionLocal
from database.models import Idoso, Agendamento
from loguru import logger


async def teste_completo_jose():
    logger.info("🧪 Iniciando teste completo com Jose R F Junior (+351 966 805 210)")

    db = SessionLocal()
    try:
        # 1. Busca ou cadastra o Jose
        telefone = "+351966805210"
        nome = "Jose R F Junior"

        idoso = db.query(Idoso).filter(Idoso.telefone == telefone).first()
        if not idoso:
            idoso = Idoso(
                nome=nome,
                telefone=telefone,
                endereco="Portugal (teste)",
                condicoes_medicas="Nenhuma (teste)",
                medicamentos_regulares="Nenhum (teste)"
            )
            db.add(idoso)
            db.commit()
            db.refresh(idoso)
            logger.success(f"✓ Jose R F Junior cadastrado! (ID: {idoso.id})")
        else:
            logger.info(f"✓ Jose R F Junior já existe (ID: {idoso.id})")

        # 2. Cria agendamento para daqui a 40 segundos
        horario = datetime.now() + timedelta(seconds=40)
        agendamento = Agendamento(
            idoso_id=idoso.id,
            telefone=idoso.telefone,
            nome_idoso=idoso.nome,
            horario=horario,
            remedios="Teste de ligação automática - tudo bem por aí?",
            status="pendente"
        )
        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)

        logger.success(f"✓ Agendamento criado (ID: {agendamento.id}) para {horario.strftime('%H:%M:%S')}")
        logger.info("⏳ Aguarde ~40 segundos...")
        logger.info("   O scheduler vai detectar e disparar a ligação automaticamente.")
        logger.info("   Observe os logs no terminal do servidor (python main.py)!")

        # Aguarda para ver o resultado
        await asyncio.sleep(60)

        # Verifica status final
        db.refresh(agendamento)
        logger.info(f"📊 Status final do agendamento: {agendamento.status}")

        if agendamento.status in ["em_andamento", "concluido"]:
            logger.success("🎉 TESTE COMPLETO BEM-SUCEDIDO! EVA disparou a ligação para o Jose automaticamente!")
        else:
            logger.warning("⚠️ Scheduler não disparou ainda. Espere mais um minuto ou verifique os logs.")

    except Exception as e:
        logger.error(f"💥 Erro no teste: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(teste_completo_jose())