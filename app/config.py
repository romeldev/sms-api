from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    MODEM_PORT: str = "COM4"
    MODEM_BAUDRATE: int = 115200
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000


settings = Settings()
