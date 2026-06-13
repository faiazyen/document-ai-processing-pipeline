from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_input_usd_per_1m_tokens: float = 0.0
    openai_output_usd_per_1m_tokens: float = 0.0
    database_url: str = "sqlite:////tmp/invoices.db"
    cors_allow_origin_regex: str = r"^https://.*\.vercel\.app$"
    app_version: str = "1.0.0"
    app_name: str = "Document AI Processing Pipeline"
    api_key_hash_secret: str = "local-development-secret"
    default_tenant_id: str = "personal-lab"
    default_tenant_name: str = "Personal Lab"
    platform_dev_api_key: str = ""
    default_region: str = "local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
