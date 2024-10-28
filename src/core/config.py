import os

from dotenv import load_dotenv
from pydantic import BaseModel

# This path might be custom, according to your '.env' file location
load_dotenv('C:/Users/User/PycharmProjects/autozen-auth-repo/src/.env')


class Settings(BaseModel):
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

    print(jwt_private_secret_key)

    def get_db_url(self, db_driver: str = db_driver) -> str:
        """
        Returns a database URL created with 'URL' module from SQL Alchemy.

        Returns:
            str: Database URL.
        """
        return f"{db_driver}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"


settings = Settings()
