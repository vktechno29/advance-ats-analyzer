from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 465

    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()