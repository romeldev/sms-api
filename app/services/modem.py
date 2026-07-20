import abc
import sys
import time

import serial

from app.config import settings


class ModemBackend(abc.ABC):
    @abc.abstractmethod
    def send_at(self, command: str, timeout: float = 5.0) -> str:
        ...

    @abc.abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        ...

    @abc.abstractmethod
    def get_status(self) -> dict:
        ...


class SerialBackend(ModemBackend):
    def __init__(self, port: str = None, baudrate: int = None):
        self._port = port or settings.MODEM_PORT
        self._baudrate = baudrate or settings.MODEM_BAUDRATE

    def _connect(self, timeout: float = 3) -> serial.Serial:
        port = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )
        return port

    def _write_at(self, port: serial.Serial, cmd: str, timeout: float) -> str:
        port.timeout = timeout
        port.reset_input_buffer()
        port.write(f"{cmd}\r".encode())
        port.flush()
        lines = []
        while True:
            raw = port.readline()
            if not raw:
                break
            line = raw.decode(errors="replace").strip()
            if not line:
                continue
            lines.append(line)
        return "\n".join(lines)

    def send_at(self, command: str, timeout: float = 5.0) -> str:
        port = self._connect(timeout)
        try:
            return self._write_at(port, command, timeout)
        finally:
            port.close()

    def send_sms(self, phone: str, message: str) -> bool:
        port = self._connect(5)
        try:
            self._write_at(port, "AT+CMGF=1", 2)
            port.write(f'AT+CMGS="{phone}"\r'.encode())
            port.flush()
            time.sleep(0.5)
            resp = port.read(200).decode(errors="replace")
            if ">" not in resp:
                return False
            port.write(f"{message}\x1a".encode())
            port.flush()
            time.sleep(1)
            final = port.read(500).decode(errors="replace")
            return "+CMGS:" in final
        finally:
            port.close()

    def get_status(self) -> dict:
        data = {"connected": False, "manufacturer": "", "model": "", "signal": 0, "imei": ""}
        try:
            port = self._connect()
            try:
                data["connected"] = True
                data["manufacturer"] = self._write_at(port, "AT+CGMI", 3)
                data["model"] = self._write_at(port, "AT+CGMM", 3)
                csq = self._write_at(port, "AT+CSQ", 3)
                for line in csq.split("\n"):
                    if ":" in line:
                        try:
                            parts = line.split(":")[1].strip().split(",")
                            data["signal"] = int(parts[0])
                        except (IndexError, ValueError):
                            pass
                data["imei"] = self._write_at(port, "AT+CGSN", 3)
            finally:
                port.close()
        except Exception as e:
            data["error"] = str(e)
        return data


def get_modem_backend() -> ModemBackend:
    return SerialBackend()
