from uuid import uuid4

from app.models.schemas import ModemStatus
from app.services.modem import ModemBackend, get_modem_backend


class SmsService:
    def __init__(self, backend: ModemBackend = None):
        self._backend = backend or get_modem_backend()

    def send_sms(self, phone: str, message: str) -> tuple[bool, str, str | None]:
        message_id = str(uuid4())
        try:
            ok = self._backend.send_sms(phone, message)
            return ok, message_id, None if ok else "Modem rejected the message"
        except Exception as e:
            return False, message_id, str(e)

    def check_status(self) -> ModemStatus:
        try:
            data = self._backend.get_status()
            return ModemStatus(**data)
        except Exception as e:
            return ModemStatus(connected=False, error=str(e))
