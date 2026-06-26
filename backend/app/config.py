from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HematoScan API"
    app_version: str = "1.0.0"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "hematoscan"

    # JWT
    jwt_secret_key: str = "change-me-to-a-secure-random-string-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # CORS
    cors_origin: str = "http://localhost:5173"

    # File upload
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
