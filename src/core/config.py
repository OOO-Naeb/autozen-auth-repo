import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv('src/.env')


class Settings(BaseSettings):
    db_driver: str = os.getenv("DB_DRIVER")
    postgres_user: str = os.getenv("POSTGRES_USER")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    postgres_database: str = os.getenv("POSTGRES_DATABASE")
    postgres_host: str = os.getenv("POSTGRES_HOST")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))

    jwt_private_secret_key: str = os.getenv("JWT_PRIVATE_SECRET_KEY")
    jwt_algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_time: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_time: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

    RABBITMQ_LOGIN: str = os.getenv('RABBITMQ_LOGIN')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT'))

    @property
    def db_url(self, db_driver: str = db_driver) -> str:
        """
        Property that represents a database URL.

        Returns:
            str: Database URL.
        """
        return f"{db_driver}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"

    @property
    def rabbitmq_url(self) -> str:
        """
        Property that represents a RabbitMQ URL.

        Returns:
            str: RabbitMQ URL.
        """
        return f'amqp://{self.RABBITMQ_LOGIN}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/'


settings = Settings()
