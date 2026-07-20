from fastapi import APIRouter, Depends

from app.models.schemas import SMSRequest, SMSResponse, ModemStatus
from app.services.sms_service import SmsService

router = APIRouter(prefix="/api/sms", tags=["sms"])


def get_service() -> SmsService:
    return SmsService()


@router.post("/send", response_model=SMSResponse)
async def send_sms(req: SMSRequest, service: SmsService = Depends(get_service)):
    ok, message_id, error = service.send_sms(req.phone, req.message)
    return SMSResponse(success=ok, message_id=message_id, error=error)


@router.get("/status", response_model=ModemStatus)
async def modem_status(service: SmsService = Depends(get_service)):
    return service.check_status()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/at")
async def run_at(cmd: str = "AT", service: SmsService = Depends(get_service)):
    try:
        resp = service._backend.send_at(cmd, timeout=5)
        return {"success": True, "response": resp}
    except Exception as e:
        return {"success": False, "error": str(e)}
