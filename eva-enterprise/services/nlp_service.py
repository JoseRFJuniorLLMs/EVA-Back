"""
Serviço de NLP para análise de conversas e detecção de risco
"""
import re
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NLPService:
    """Serviço para análise de linguagem natural em saúde mental"""

    # =====================================================================
    # KEYWORDS PERIGOSAS (Detecção de Risco)
    # =====================================================================

    DANGER_KEYWORDS = {
        'suicidal_ideation': [
            'suicídio', 'me matar', 'acabar com tudo', 'não aguento mais',
            'quero morrer', 'melhor morto', 'fim da vida', 'tirar minha vida',
            'não vale a pena viver', 'desaparecer', 'dormir para sempre',
            'última vez', 'despedida', 'não quero mais viver'
        ],
        'self_harm': [
            'me cortar', 'me machucar', 'automutilação', 'me ferir',
            'cortar os pulsos', 'queimar', 'me bater'
        ],
        'hopelessness': [
            'sem esperança', 'sem saída', 'sem futuro', 'nada vai melhorar',
            'nunca vai passar', 'impossível', 'desistir', 'dar up',
            'inútil', 'fracasso total', 'perdido'
        ],
        'isolation': [
            'ninguém liga', 'sozinho', 'abandonado', 'ninguém se importa',
            'invisível', 'sem amigos', 'sem família', 'isolado'
        ],
        'severe_depression': [
            'vazio', 'nada me alegra', 'sem sentido', 'buraco negro',
            'peso enorme', 'escuridão', 'dor insuportável'
        ],
        'severe_anxiety': [
            'pânico', 'sufocando', 'coração acelerado', 'vou morrer',
            'descontrole', 'terror', 'medo de tudo'
        ],
        'substance_abuse': [
            'álcool demais', 'bebendo muito', 'usando drogas', 'dependência',
            'preciso beber', 'sem controle com bebida'
        ]
    }

    # =====================================================================
    # POSITIVE KEYWORDS (Indicadores de Bem-Estar)
    # =====================================================================

    POSITIVE_KEYWORDS = {
        'gratitude': [
            'grato', 'agradecido', 'sortudo', 'abençoado', 'feliz por',
            'apreciando', 'valorizo'
        ],
        'hope': [
            'esperança', 'vai melhorar', 'futuro melhor', 'acredito',
            'confio', 'vou conseguir', 'seguir em frente'
        ],
        'social_support': [
            'minha família', 'meus amigos', 'me apoiam', 'conversando com',
            'não estou sozinho', 'tenho ajuda'
        ],
        'coping': [
            'meditação', 'exercício', 'terapia', 'respiração', 'conversar',
            'escrever', 'música', 'caminhar'
        ],
        'achievement': [
            'consegui', 'orgulhoso', 'melhor', 'progresso', 'superei',
            'realizei'
        ]
    }

    # =====================================================================
    # MÉTODOS PRINCIPAIS
    # =====================================================================

    @staticmethod
    def analyze_message(text: str) -> Dict:
        """
        Análise completa de uma mensagem

        Retorna:
        {
            'sentiment_score': float (-1 a 1),
            'sentiment_label': str,
            'danger_flags': List[str],
            'detected_keywords': List[str],
            'risk_level': str,
            'entities': Dict,
            'topics': List[str]
        }
        """
        # 1. Análise de sentimento
        sentiment_score, sentiment_label = NLPService.analyze_sentiment_simple(text)

        # 2. Detecção de keywords perigosas
        danger_flags = NLPService.detect_danger_keywords(text)

        # 3. Detecção de keywords gerais
        all_keywords = NLPService.extract_keywords(text)

        # 4. Calcular nível de risco
        risk_level = NLPService.calculate_risk_level(danger_flags, sentiment_score)

        # 5. Extração de entidades básicas
        entities = NLPService.extract_entities_simple(text)

        # 6. Classificação de tópicos
        topics = NLPService.classify_topics(text)

        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'danger_flags': danger_flags,
            'detected_keywords': all_keywords,
            'risk_level': risk_level,
            'entities': entities,
            'topics': topics,
            'analyzed_at': datetime.now().isoformat()
        }

    @staticmethod
    def analyze_sentiment_simple(text: str) -> Tuple[float, str]:
        """
        Análise de sentimento simples baseada em keywords
        (Para produção, usar modelo de ML)

        Returns: (score: float, label: str)
        """
        text_lower = text.lower()

        # Contar keywords positivas e negativas
        positive_count = 0
        negative_count = 0

        # Contar positivas
        for category, keywords in NLPService.POSITIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    positive_count += 1

        # Contar negativas
        for category, keywords in NLPService.DANGER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    negative_count += 2  # Peso maior para keywords perigosas

        # Palavras negativas comuns
        common_negative = ['não', 'nunca', 'nada', 'triste', 'ruim', 'mal', 'difícil', 'problema']
        for word in common_negative:
            if f' {word} ' in f' {text_lower} ':
                negative_count += 0.5

        # Palavras positivas comuns
        common_positive = ['sim', 'bom', 'bem', 'feliz', 'alegre', 'ótimo', 'legal', 'gosto']
        for word in common_positive:
            if f' {word} ' in f' {text_lower} ':
                positive_count += 0.5

        # Calcular score normalizado (-1 a 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            label = 'neutral'
        else:
            score = (positive_count - negative_count) / total
            score = max(-1.0, min(1.0, score))  # Clamp entre -1 e 1

            if score <= -0.6:
                label = 'very_negative'
            elif score <= -0.2:
                label = 'negative'
            elif score >= 0.6:
                label = 'very_positive'
            elif score >= 0.2:
                label = 'positive'
            else:
                label = 'neutral'

        return round(score, 4), label

    @staticmethod
    def detect_danger_keywords(text: str) -> List[str]:
        """
        Detectar keywords perigosas no texto

        Retorna lista de categorias de perigo detectadas
        """
        text_lower = text.lower()
        flags = []

        for category, keywords in NLPService.DANGER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if category not in flags:
                        flags.append(category)
                    break  # Já detectou esta categoria

        return flags

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extrair todas as keywords relevantes"""
        text_lower = text.lower()
        found_keywords = []

        # Verificar todas as keywords (positivas e negativas)
        all_keywords = {}
        all_keywords.update(NLPService.POSITIVE_KEYWORDS)
        all_keywords.update(NLPService.DANGER_KEYWORDS)

        for category, keywords in all_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)

        return list(set(found_keywords))  # Remover duplicatas

    @staticmethod
    def calculate_risk_level(danger_flags: List[str], sentiment_score: float) -> str:
        """
        Calcular nível de risco baseado em flags e sentimento

        Retorna: 'NONE', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
        """
        # Risco crítico
        if 'suicidal_ideation' in danger_flags:
            return 'CRITICAL'
        if 'self_harm' in danger_flags:
            return 'CRITICAL'

        # Risco alto
        if 'hopelessness' in danger_flags and sentiment_score < -0.5:
            return 'HIGH'
        if len(danger_flags) >= 3:
            return 'HIGH'

        # Risco moderado
        if len(danger_flags) >= 1 and sentiment_score < -0.3:
            return 'MODERATE'
        if sentiment_score < -0.7:
            return 'MODERATE'

        # Risco baixo
        if len(danger_flags) >= 1 or sentiment_score < -0.2:
            return 'LOW'

        # Sem risco
        return 'NONE'

    @staticmethod
    def extract_entities_simple(text: str) -> Dict[str, List[str]]:
        """
        Extração simples de entidades
        (Para produção, usar spaCy ou similar)
        """
        entities = {
            'people': [],
            'emotions': [],
            'health_terms': [],
            'time_references': []
        }

        text_lower = text.lower()

        # Emoções
        emotion_keywords = [
            'tristeza', 'alegria', 'raiva', 'medo', 'ansiedade', 'pânico',
            'felicidade', 'amor', 'ódio', 'frustração', 'alívio', 'esperança'
        ]
        for emotion in emotion_keywords:
            if emotion in text_lower:
                entities['emotions'].append(emotion)

        # Termos de saúde
        health_keywords = [
            'medicamento', 'terapia', 'médico', 'psicólogo', 'psiquiatra',
            'hospital', 'consulta', 'tratamento', 'remédio'
        ]
        for health_term in health_keywords:
            if health_term in text_lower:
                entities['health_terms'].append(health_term)

        # Referências temporais
        time_keywords = ['hoje', 'ontem', 'amanhã', 'semana', 'mês', 'ano']
        for time_ref in time_keywords:
            if time_ref in text_lower:
                entities['time_references'].append(time_ref)

        # Pessoas (regex simples para nomes próprios - básico)
        # Padrão: palavra começando com maiúscula
        name_pattern = r'\b[A-Z][a-zá-ú]+\b'
        potential_names = re.findall(name_pattern, text)
        entities['people'] = potential_names[:5]  # Limitar a 5

        return entities

    @staticmethod
    def classify_topics(text: str) -> List[str]:
        """
        Classificação de tópicos (simples, baseado em keywords)
        """
        topics = []
        text_lower = text.lower()

        topic_keywords = {
            'family': ['família', 'pai', 'mãe', 'filho', 'filha', 'irmão', 'irmã', 'neto', 'neta', 'esposa', 'marido'],
            'work': ['trabalho', 'emprego', 'chefe', 'colega', 'carreira', 'demissão', 'desemprego'],
            'health': ['saúde', 'doença', 'dor', 'sintoma', 'médico', 'hospital', 'medicamento'],
            'death': ['morte', 'morrer', 'funeral', 'cemitério', 'falecimento'],
            'relationships': ['relacionamento', 'namoro', 'casamento', 'amor', 'término', 'divórcio'],
            'finances': ['dinheiro', 'dívida', 'conta', 'desemprego', 'salário', 'financeiro'],
            'loneliness': ['solidão', 'sozinho', 'isolado', 'sem amigos'],
            'mental_health': ['depressão', 'ansiedade', 'pânico', 'estresse', 'terapia', 'psicólogo']
        }

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if topic not in topics:
                        topics.append(topic)
                    break

        return topics

    # =====================================================================
    # ANÁLISE DE CONVERSAÇÃO COMPLETA
    # =====================================================================

    @staticmethod
    def analyze_conversation(messages: List[Dict]) -> Dict:
        """
        Análisar uma conversação completa (múltiplas mensagens)

        Args:
            messages: Lista de dicts {'text': str, 'timestamp': datetime, 'role': str}

        Returns:
            Análise agregada da conversação
        """
        if not messages:
            return {'error': 'no_messages'}

        # Filtrar apenas mensagens do paciente
        patient_messages = [m for m in messages if m.get('role') == 'user' or m.get('role') == 'patient']

        if not patient_messages:
            return {'error': 'no_patient_messages'}

        # Análise de cada mensagem
        analyses = []
        for msg in patient_messages:
            analysis = NLPService.analyze_message(msg['text'])
            analysis['timestamp'] = msg.get('timestamp')
            analyses.append(analysis)

        # Agregação
        sentiment_scores = [a['sentiment_score'] for a in analyses]
        all_danger_flags = []
        for a in analyses:
            all_danger_flags.extend(a['danger_flags'])

        # Contar flags
        flag_counts = {}
        for flag in all_danger_flags:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

        # Calcular médias
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        # Determinar tendência
        if len(sentiment_scores) >= 3:
            first_half = sentiment_scores[:len(sentiment_scores)//2]
            second_half = sentiment_scores[len(sentiment_scores)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            trend = 'improving' if second_avg > first_avg else ('worsening' if second_avg < first_avg else 'stable')
        else:
            trend = 'insufficient_data'

        # Nível de risco geral
        if 'suicidal_ideation' in flag_counts or 'self_harm' in flag_counts:
            overall_risk = 'CRITICAL'
        elif len(flag_counts) >= 2 and avg_sentiment < -0.4:
            overall_risk = 'HIGH'
        elif len(flag_counts) >= 1 or avg_sentiment < -0.3:
            overall_risk = 'MODERATE'
        elif avg_sentiment < -0.1:
            overall_risk = 'LOW'
        else:
            overall_risk = 'NONE'

        return {
            'message_count': len(patient_messages),
            'avg_sentiment': round(avg_sentiment, 4),
            'sentiment_trend': trend,
            'danger_flag_counts': flag_counts,
            'overall_risk': overall_risk,
            'analyses': analyses
        }

    # =====================================================================
    # DETECÇÃO DE MUDANÇA DE PADRÃO
    # =====================================================================

    @staticmethod
    def detect_pattern_change(
        recent_analyses: List[Dict],
        baseline_analyses: List[Dict]
    ) -> Dict:
        """
        Detectar mudanças de padrão entre baseline e período recente

        Args:
            recent_analyses: Análises recentes (últimos 7 dias)
            baseline_analyses: Análises baseline (30-60 dias atrás)
        """
        if not recent_analyses or not baseline_analyses:
            return {'error': 'insufficient_data'}

        # Calcular médias
        recent_sentiment = sum([a['sentiment_score'] for a in recent_analyses]) / len(recent_analyses)
        baseline_sentiment = sum([a['sentiment_score'] for a in baseline_analyses]) / len(baseline_analyses)

        # Diferença
        change = recent_sentiment - baseline_sentiment
        change_percentage = (change / abs(baseline_sentiment)) * 100 if baseline_sentiment != 0 else 0

        # Determinar se é significativo (mudança > 30%)
        if abs(change_percentage) > 30:
            significant = True
            if change < 0:
                alert_message = f"⚠️ Piora significativa detectada: sentimento caiu {abs(change_percentage):.1f}%"
                alert_level = 'HIGH'
            else:
                alert_message = f"✅ Melhora significativa detectada: sentimento subiu {change_percentage:.1f}%"
                alert_level = 'INFO'
        else:
            significant = False
            alert_message = "Padrão estável, sem mudanças significativas"
            alert_level = 'NONE'

        return {
            'significant_change': significant,
            'change_percentage': round(change_percentage, 2),
            'recent_avg_sentiment': round(recent_sentiment, 4),
            'baseline_avg_sentiment': round(baseline_sentiment, 4),
            'alert_message': alert_message,
            'alert_level': alert_level
        }


# =====================================================================
# FUNÇÕES AUXILIARES PARA INTEGRAÇÃO
# =====================================================================

async def process_conversation_message_async(
    patient_id: int,
    message_text: str,
    session_id: Optional[int] = None,
    message_id: Optional[int] = None
) -> Dict:
    """
    Processar mensagem de conversa de forma assíncrona
    (Para usar com Celery ou task queue)
    """
    logger.info(f"Processando mensagem NLP para paciente {patient_id}")

    # Análise NLP
    analysis = NLPService.analyze_message(message_text)

    # Log se houver risco
    if analysis['risk_level'] in ['HIGH', 'CRITICAL']:
        logger.warning(
            f"🚨 Risco {analysis['risk_level']} detectado - Paciente {patient_id} - "
            f"Flags: {analysis['danger_flags']}"
        )

    # TODO: Salvar análise no banco de dados
    # await MentalHealthRepository.create_nlp_analysis(...)

    return analysis
