"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # ============================================
    # PROJECT INFO
    # ============================================
    PROJECT_NAME: str = "BCP Fraud Guardian"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # ============================================
    # ENVIRONMENT
    # ============================================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_URL: str = "sqlite:///./database_storage/fraud_detection.db"
    # ============================================
    

    # Azure SQL Database (cuando despliegues)
    # DATABASE_URL=mssql+pyodbc://usuario:password@servidor.database.windows.net:1433/frauddetection?driver=ODBC+Driver+18+for+SQL+Server
    
    # ============================================
    # LLM PROVIDER
    # ============================================
    LLM_PROVIDER: Literal["openai", "azure"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # ============================================
    # OPENAI API
    # ============================================
    OPENAI_API_KEY: str = "your-key-here"
    
    # ============================================
    # AZURE OPENAI
    # ============================================
    AZURE_OPENAI_API_KEY: str = "your-azure-key-here"
    AZURE_OPENAI_ENDPOINT: str = "https://your-resource.openai.azure.com/"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"
    
    # ============================================
    # API SECURITY
    # ============================================
    API_KEY_NAME: str = "X-API-Key"
    API_KEY_VALUE: str = "BCP-Fraud-Detection-2025-SecureKey-abc123xyz789"
    
    # ============================================
    # CHROMADB
    # ============================================
    CHROMA_PERSIST_DIRECTORY: str = "./chroma"
    CHROMA_COLLECTION_NAME: str = "fraud_policies"
    
    # ============================================
    # REDIS & CELERY (opcional)
    # ============================================
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ============================================
    # SECURITY (opcional)
    # ============================================
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ============================================
    # JWT AUTHENTICATION
    # ============================================
    JWT_SECRET_KEY: str = "BCP-Fraud-Guardian-Super-Secret-Key-2025"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite variables adicionales
        


@lru_cache()
def get_settings() -> Settings:
    """Obtener instancia única de configuración"""
    return Settings()