"""Default config for pydantic"""
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Default Settings class

    It takes default configuration from the `.env` file
    """
    gdrive_auth_path: str = Field(..., env='GDRIVE_AUTH_PATH')
    email: str = Field(..., env='EMAIL')

    class Config:
        """Sub class to define the `.env` file"""
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
