from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_TRACK_MODIFICATIONS: str
    MAIL_SERVER: str
    MAIL_PORT: str
    MAIL_USE_TLS: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    ADMIN_EMAIL: str
    ROWS_PER_PAGE: int = 10
    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 300
    # SQLALCHEMY_ECHO = True

    SITE_NAME: str

    DEFAULT_LANGUAGE: str = "en"
    LANGUAGES: list = ["en", "es"]

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
