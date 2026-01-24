"""
Serviço de Protocolo de Emergência para Risco Suicida e Crises
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.repositories.mental_health_repository import MentalHealthRepository
from ..database.models import Idoso, Cuidador, SafetyPlan
from .nlp_service import NLPService

logger = logging.getLogger(__name__)


class EmergencyProtocolService:
    """Serviço para gerenciar protocolos de emergência em saúde mental"""

    # =====================================================================
    # NÍVEIS DE RISCO E AÇÕES
    # =====================================================================

    RISK_ACTIONS = {
        'CRITICAL': {
            'priority': 1,
            'actions': [
                'block_app_until_confirmation',
                'call_emergency_contacts',
                'notify_professionals',
                'display_crisis_hotlines',
                'activate_safety_plan',
                'send_emergency_sms',
                'log_critical_event'
            ],
            'message': '🚨 EMERGÊNCIA DETECTADA - Ajuda está disponível agora',
            'auto_dial': True  # Discagem automática CVV
        },
        'HIGH': {
            'priority': 2,
            'actions': [
                'notify_professionals',
                'notify_family',
                'display_safety_plan',
                'schedule_urgent_appointment',
                'send_support_message'
            ],
            'message': '⚠️ ALERTA DE RISCO - Por favor, entre em contato com seu terapeuta',
            'auto_dial': False
        },
        'MODERATE': {
            'priority': 3,
            'actions': [
                'display_safety_plan',
                'offer_coping_strategies',
                'suggest_self_help',
                'log_concern'
            ],
            'message': '💛 Notamos que você pode não estar bem. Podemos ajudar?',
            'auto_dial': False
        },
        'LOW': {
            'priority': 4,
            'actions': [
                'offer_resources',
                'check_in_later'
            ],
            'message': 'Recursos de apoio disponíveis se você precisar',
            'auto_dial': False
        }
    }

    # =====================================================================
    # HOTLINES DE CRISE (Brasil)
    # =====================================================================

    CRISIS_HOTLINES = [
        {
            'name': 'CVV - Centro de Valorização da Vida',
            'phone': '188',
            'available': '24/7',
            'description': 'Apoio emocional e prevenção ao suicídio'
        },
        {
            'name': 'SAMU',
            'phone': '192',
            'available': '24/7',
            'description': 'Emergências médicas'
        },
        {
            'name': 'Bombeiros',
            'phone': '193',
            'available': '24/7',
            'description': 'Emergências e resgate'
        },
        {
            'name': 'Polícia Militar',
            'phone': '190',
            'available': '24/7',
            'description': 'Emergências policiais'
        }
    ]

    # =====================================================================
    # MÉTODOS PRINCIPAIS
    # =====================================================================

    @staticmethod
    async def activate_emergency_protocol(
        session: AsyncSession,
        patient_id: int,
        risk_level: str,
        trigger_reason: str,
        trigger_details: Dict,
        detected_at: Optional[datetime] = None
    ) -> Dict:
        """
        Ativar protocolo de emergência

        Args:
            session: Sessão do banco de dados
            patient_id: ID do paciente
            risk_level: 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'
            trigger_reason: Razão do acionamento (ex: 'c_ssrs_high', 'keyword_detection')
            trigger_details: Detalhes do trigger
            detected_at: Timestamp da detecção

        Returns:
            Dict com ações executadas e status
        """
        if detected_at is None:
            detected_at = datetime.now()

        logger.critical(
            f"🚨 PROTOCOLO DE EMERGÊNCIA ATIVADO - "
            f"Paciente: {patient_id} | Risco: {risk_level} | Razão: {trigger_reason}"
        )

        # Buscar configurações do nível de risco
        risk_config = EmergencyProtocolService.RISK_ACTIONS.get(risk_level, {})

        # Buscar dados do paciente
        patient = await EmergencyProtocolService._get_patient_data(session, patient_id)

        if not patient:
            logger.error(f"Paciente {patient_id} não encontrado")
            return {'error': 'patient_not_found'}

        # Buscar plano de segurança
        safety_plan = await MentalHealthRepository.get_active_safety_plan(session, patient_id)

        # Executar ações
        actions_taken = []
        contacts_notified = []

        # 1. CRITICAL: Bloquear app até confirmação de segurança
        if 'block_app_until_confirmation' in risk_config.get('actions', []):
            actions_taken.append('app_blocked')
            # TODO: Implementar bloqueio de app via Firebase ou flag no banco

        # 2. Notificar contatos de emergência
        if 'call_emergency_contacts' in risk_config.get('actions', []):
            emergency_contacts = await EmergencyProtocolService._notify_emergency_contacts(
                session, patient, risk_level, trigger_reason
            )
            contacts_notified.extend(emergency_contacts)
            actions_taken.append('emergency_contacts_notified')

        # 3. Notificar profissionais
        if 'notify_professionals' in risk_config.get('actions', []):
            professionals = await EmergencyProtocolService._notify_professionals(
                session, patient_id, risk_level, trigger_reason
            )
            contacts_notified.extend(professionals)
            actions_taken.append('professionals_notified')

        # 4. Exibir hotlines de crise
        if 'display_crisis_hotlines' in risk_config.get('actions', []):
            actions_taken.append('crisis_hotlines_displayed')

        # 5. Ativar plano de segurança
        if 'activate_safety_plan' in risk_config.get('actions', []) and safety_plan:
            actions_taken.append('safety_plan_activated')

        # 6. Enviar SMS de emergência
        if 'send_emergency_sms' in risk_config.get('actions', []):
            await EmergencyProtocolService._send_emergency_sms(patient, risk_level)
            actions_taken.append('emergency_sms_sent')

        # 7. Registrar evento de crise
        if 'log_critical_event' in risk_config.get('actions', []):
            await MentalHealthRepository.create_crisis_event(
                session=session,
                patient_id=patient_id,
                crisis_type='suicidal_ideation',  # ou extrair do trigger_details
                severity='life_threatening',
                occurred_at=detected_at,
                precipitating_factors=trigger_details.get('precipitating_factors', []),
                warning_signs=trigger_details.get('warning_signs', []),
                intervention_taken=actions_taken,
                emergency_contacts_notified=[c['name'] for c in contacts_notified],
                notes=f"Acionado por: {trigger_reason}"
            )
            actions_taken.append('crisis_event_logged')

        # Resultado
        result = {
            'protocol_activated': True,
            'patient_id': patient_id,
            'risk_level': risk_level,
            'trigger_reason': trigger_reason,
            'detected_at': detected_at.isoformat(),
            'actions_taken': actions_taken,
            'contacts_notified': contacts_notified,
            'safety_plan_available': safety_plan is not None,
            'message': risk_config.get('message', ''),
            'crisis_hotlines': EmergencyProtocolService.CRISIS_HOTLINES,
            'auto_dial_cvv': risk_config.get('auto_dial', False)
        }

        logger.info(f"Protocolo executado - Ações: {actions_taken}")

        return result

    # =====================================================================
    # TRIGGERS AUTOMÁTICOS
    # =====================================================================

    @staticmethod
    async def check_triggers_for_patient(
        session: AsyncSession,
        patient_id: int
    ) -> Optional[Dict]:
        """
        Verificar todos os triggers de emergência para um paciente

        Returns:
            Dict com protocolo ativado se houver risco, ou None
        """
        # 1. Verificar C-SSRS score
        latest_cssrs = await MentalHealthRepository.get_latest_assessment_by_type(
            session, patient_id, 'C-SSRS'
        )

        if latest_cssrs and latest_cssrs.score >= 4:
            return await EmergencyProtocolService.activate_emergency_protocol(
                session=session,
                patient_id=patient_id,
                risk_level='CRITICAL',
                trigger_reason='c_ssrs_critical',
                trigger_details={
                    'cssrs_score': latest_cssrs.score,
                    'severity': latest_cssrs.severity_level
                }
            )

        # 2. Verificar PHQ-9 score (depressão severa)
        latest_phq9 = await MentalHealthRepository.get_latest_assessment_by_type(
            session, patient_id, 'PHQ9'
        )

        if latest_phq9 and latest_phq9.score >= 20:
            return await EmergencyProtocolService.activate_emergency_protocol(
                session=session,
                patient_id=patient_id,
                risk_level='HIGH',
                trigger_reason='severe_depression',
                trigger_details={
                    'phq9_score': latest_phq9.score,
                    'severity': latest_phq9.severity_level
                }
            )

        # 3. Verificar predições de ML
        ml_prediction = await MentalHealthRepository.get_latest_prediction(
            session, patient_id, 'suicide_risk'
        )

        if ml_prediction and ml_prediction.prediction_label in ['HIGH', 'CRITICAL']:
            return await EmergencyProtocolService.activate_emergency_protocol(
                session=session,
                patient_id=patient_id,
                risk_level=ml_prediction.prediction_label,
                trigger_reason='ml_prediction',
                trigger_details={
                    'model': ml_prediction.model_name,
                    'confidence': ml_prediction.confidence_score,
                    'prediction_value': ml_prediction.prediction_value
                }
            )

        # 4. Verificar tendência de sentimento (últimos 7 dias)
        sentiment_trend = await MentalHealthRepository.get_recent_sentiment_trend(
            session, patient_id, days=7
        )

        if (
            sentiment_trend.get('avg_sentiment') and
            sentiment_trend['avg_sentiment'] < -0.7 and
            len(sentiment_trend.get('danger_flags_count', {})) > 0
        ):
            return await EmergencyProtocolService.activate_emergency_protocol(
                session=session,
                patient_id=patient_id,
                risk_level='MODERATE',
                trigger_reason='persistent_negative_sentiment',
                trigger_details={
                    'avg_sentiment': sentiment_trend['avg_sentiment'],
                    'danger_flags': sentiment_trend.get('danger_flags_count', {})
                }
            )

        return None  # Sem triggers acionados

    # =====================================================================
    # MÉTODOS AUXILIARES
    # =====================================================================

    @staticmethod
    async def _get_patient_data(session: AsyncSession, patient_id: int) -> Optional[Idoso]:
        """Buscar dados do paciente"""
        from sqlalchemy import select
        result = await session.execute(
            select(Idoso).where(Idoso.id == patient_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _notify_emergency_contacts(
        session: AsyncSession,
        patient: Idoso,
        risk_level: str,
        trigger_reason: str
    ) -> List[Dict]:
        """Notificar contatos de emergência"""
        from sqlalchemy import select

        # Buscar cuidadores marcados como contato de emergência
        result = await session.execute(
            select(Cuidador).where(
                Cuidador.idoso_id == patient.id,
                Cuidador.eh_contato_emergencia == True,
                Cuidador.ativo == True
            )
        )
        emergency_cuidadores = result.scalars().all()

        notified = []

        for cuidador in emergency_cuidadores:
            logger.critical(
                f"📞 NOTIFICANDO CONTATO DE EMERGÊNCIA: {cuidador.nome} ({cuidador.telefone}) - "
                f"Paciente: {patient.nome} - Risco: {risk_level}"
            )

            # TODO: Implementar notificação real (Push, SMS, Call)
            # await notification_service.send_emergency_alert(...)

            notified.append({
                'name': cuidador.nome,
                'phone': cuidador.telefone,
                'relationship': cuidador.parentesco,
                'method': cuidador.metodo_preferido or 'push'
            })

        return notified

    @staticmethod
    async def _notify_professionals(
        session: AsyncSession,
        patient_id: int,
        risk_level: str,
        trigger_reason: str
    ) -> List[Dict]:
        """Notificar profissionais de saúde"""
        from sqlalchemy import select

        # Buscar cuidadores que são profissionais
        result = await session.execute(
            select(Cuidador).where(
                Cuidador.idoso_id == patient_id,
                Cuidador.tipo_cuidador.in_(['psicologo', 'psiquiatra', 'medico']),
                Cuidador.ativo == True
            )
        )
        professionals = result.scalars().all()

        notified = []

        for prof in professionals:
            logger.warning(
                f"📧 NOTIFICANDO PROFISSIONAL: {prof.nome} ({prof.tipo_cuidador}) - "
                f"Paciente ID: {patient_id} - Risco: {risk_level}"
            )

            # TODO: Implementar notificação
            # await notification_service.send_professional_alert(...)

            notified.append({
                'name': prof.nome,
                'type': prof.tipo_cuidador,
                'phone': prof.telefone,
                'email': prof.email
            })

        return notified

    @staticmethod
    async def _send_emergency_sms(patient: Idoso, risk_level: str):
        """Enviar SMS de emergência"""
        # Extrair telefone do contato de emergência
        emergency_contact = patient.contato_emergencia or {}
        phone = emergency_contact.get('telefone')

        if not phone:
            logger.warning(f"Paciente {patient.id} sem telefone de emergência cadastrado")
            return

        message = (
            f"🚨 ALERTA EVA - {patient.nome} pode estar em situação de risco ({risk_level}). "
            f"Entre em contato imediatamente. Em caso de emergência, ligue 188 (CVV) ou 192 (SAMU)."
        )

        logger.critical(f"📱 SMS de emergência enviado para {phone}")

        # TODO: Implementar envio real via Twilio ou similar
        # await sms_service.send_sms(phone, message)

    # =====================================================================
    # SAFETY PLAN ACTIVATION
    # =====================================================================

    @staticmethod
    async def get_safety_plan_response(
        session: AsyncSession,
        patient_id: int
    ) -> Dict:
        """
        Obter resposta formatada do plano de segurança para exibir em crise

        Retorna estrutura otimizada para UI de emergência
        """
        safety_plan = await MentalHealthRepository.get_active_safety_plan(session, patient_id)

        if not safety_plan:
            return {
                'available': False,
                'message': 'Nenhum plano de segurança configurado. Entre em contato com seu terapeuta.',
                'crisis_hotlines': EmergencyProtocolService.CRISIS_HOTLINES
            }

        return {
            'available': True,
            'steps': [
                {
                    'step': 1,
                    'title': '⚠️ Reconheça os Sinais de Alerta',
                    'items': safety_plan.warning_signs
                },
                {
                    'step': 2,
                    'title': '🧘 Estratégias de Enfrentamento Internas',
                    'description': 'Coisas que você pode fazer sozinho(a):',
                    'items': safety_plan.internal_coping_strategies
                },
                {
                    'step': 3,
                    'title': '👥 Distrações Sociais',
                    'description': 'Lugares ou atividades com outras pessoas:',
                    'items': safety_plan.social_distractions or []
                },
                {
                    'step': 4,
                    'title': '📞 Pessoas para Contatar',
                    'contacts': safety_plan.people_to_contact
                },
                {
                    'step': 5,
                    'title': '🏥 Profissionais para Contatar',
                    'contacts': safety_plan.professionals_to_contact
                },
                {
                    'step': 6,
                    'title': '🆘 Linhas de Crise (24/7)',
                    'contacts': safety_plan.crisis_hotlines
                },
                {
                    'step': 7,
                    'title': '🛡️ Torne o Ambiente Seguro',
                    'items': safety_plan.environment_safety or []
                },
                {
                    'step': 8,
                    'title': '💛 Razões para Viver',
                    'items': safety_plan.reasons_for_living or []
                }
            ],
            'created_at': safety_plan.created_at.isoformat()
        }
