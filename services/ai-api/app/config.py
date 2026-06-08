from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    database_url: str = "sqlite:///./invoices.db"
    cors_allow_origin_regex: str = r"^https://.*\.vercel\.app$"
    app_version: str = "1.0.0"
    app_name: str = "Document AI Processing Pipeline"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
