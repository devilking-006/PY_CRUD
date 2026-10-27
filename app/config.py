from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

# The values above are reference values. 
# In production env, we can set those values in the machine and these reference values are going to automatically 
# fetch those system env values and use in the application.

settings = Settings()