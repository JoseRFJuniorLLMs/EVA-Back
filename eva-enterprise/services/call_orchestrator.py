from twilio.rest import Client
from config.settings import settings

class CallOrchestrator:
    def __init__(self):
        try:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        except Exception as e:
            print(f"Warning: Twilio client not initialized (missing creds?): {e}")
            self.client = None

    def initiate_call(self, to_number: str, agendamento_id: int):
        if not self.client:
            raise Exception("Twilio client validation failed")

        # Passa o ID do agendamento para o callback
        url = f"https://{settings.SERVICE_DOMAIN}/calls/twiml?agendamento_id={agendamento_id}"
        
        try:
            call = self.client.calls.create(
                url=url,
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER
            )
            print(f"📞 Ligação iniciada: {call.sid}")
            return call.sid
        except Exception as e:
            print(f"✗ Erro ao fazer ligação: {e}")
            raise e
