from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str = "database.db" 
    
    @property
    def DATABASE_URL_sqlite(self):
        return f"sqlite:///{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()