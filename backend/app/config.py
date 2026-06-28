from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HematoScan API"
    app_version: str = "1.0.0"

    # MongoDB (required from .env)
    mongodb_uri: str
    mongodb_db_name: str

    # JWT (secret_key required from .env)
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # CORS (required from .env)
    cors_origin: str

    # File upload
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
