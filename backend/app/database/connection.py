"""
Database Connection
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
from app.database.models import Base
from typing import Generator

settings = get_settings()

# Crear engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False  # Cambiar a True para ver queries SQL
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializar base de datos (crear tablas y poblar datos)
    """
    from app.services.seed_service import SeedService
    
    print("🗄️  Inicializando base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")
    
    # Poblar datos maestros
    db = SessionLocal()
    try:
        SeedService.seed_all(db)
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()