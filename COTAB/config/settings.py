import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "AI Factory"
    groq_api_key: SecretStr | None = Field(None, env="GROQ_API_KEY")
    groq_base_url: str = Field("https://api.groq.com/openai/v1", env="GROQ_BASE_URL")
    iflow_api_key: SecretStr | None = Field(None, env="IFLOW_API_KEY")
    nvidia_api_key: SecretStr | None = Field(None, env="NVIDIA_API_KEY")
    telegram_bot_token: str | None = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(None, env="TELEGRAM_CHAT_ID")

settings = Settings()