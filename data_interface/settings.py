from pydantic import BaseSettings

class Settings(BaseSettings):
    auth0_domain: str
    api_identifier: str
    auth0_client_id: str
    auth0_client_secret: str

    class Config:
        env_file = ".env"

settings = Settings()
