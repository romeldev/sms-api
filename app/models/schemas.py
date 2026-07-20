from pydantic import BaseModel


class SMSRequest(BaseModel):
    phone: str
    message: str


class SMSResponse(BaseModel):
    success: bool
    message_id: str
    error: str | None = None


class ModemStatus(BaseModel):
    connected: bool
    manufacturer: str = ""
    model: str = ""
    signal: int = 0
    imei: str = ""
    error: str | None = None
