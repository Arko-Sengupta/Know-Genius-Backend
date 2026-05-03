from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

Config = AppSettings()