# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from database.connection import SessionLocal
from database.models import Agendamento
from loguru import logger  # ← Logs bonitos
import httpx
from config.settings import settings

scheduler = BackgroundScheduler()


def verificar_e_disparar_agendamentos():
    logger.info("🔍 Scheduler: Verificando agendamentos pendentes...")

    db = SessionLocal()
    try:
        agora = datetime.now()
        pendentes = db.query(Agendamento).filter(
            Agendamento.horario <= agora,
            Agendamento.status == "pendente"
        ).all()

        if not pendentes:
            logger.info("✅ Nenhum agendamento pendente no momento.")
            return

        logger.success(f"🚨 Encontrados {len(pendentes)} agendamento(s) para disparar!")

        base_url = f"http://localhost:{settings.PORT}"
        with httpx.Client(timeout=10.0) as client:
            for ag in pendentes:
                logger.warning(
                    f"📞 Disparando ligação para agendamento #{ag.id} - {ag.nome_idoso or 'Sem nome'} ({ag.telefone})")
                try:
                    response = client.post(
                        f"{base_url}/make-call",
                        json={"agendamento_id": ag.id}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        logger.success(f"✓ Ligação iniciada! SID: {data.get('sid', 'N/A')}")
                    else:
                        logger.error(f"✗ Falha ao disparar: HTTP {response.status_code} - {response.text}")
                except Exception as e:
                    logger.error(f"✗ Erro ao chamar /make-call: {e}")

    except Exception as e:
        logger.critical(f"💥 Erro crítico no scheduler: {e}")
    finally:
        db.close()


def iniciar_scheduler():
    scheduler.add_job(
        verificar_e_disparar_agendamentos,
        'interval',
        minutes=1,
        next_run_time=datetime.now()
    )
    scheduler.start()
    logger.info("🕐 Scheduler automático iniciado — verifica a cada 1 minuto")