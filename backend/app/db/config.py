"""
Configuración de la base de datos PostgreSQL con SQLAlchemy
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os
from typing import Generator
load_dotenv()
# URL de conexión a PostgreSQL
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/tu_base_de_datos"
)

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Cambiar a False en producción
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,  # Número de conexiones en el pool
    max_overflow=20  # Conexiones adicionales permitidas
)

# SessionLocal para crear sesiones de BD
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Dependencia para obtener sesión de BD en FastAPI
def get_db() -> Generator:
    """
    Dependencia que proporciona una sesión de base de datos.
    
    Uso en FastAPI:
        @app.get("/usuarios")
        def get_usuarios(db: Session = Depends(get_db)):
            usuarios = db.query(Usuario).all()
            return usuarios
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para inicializar la base de datos
def init_db():
    """
    Crea todas las tablas en la base de datos.
    NOTA: Solo usar en desarrollo. En producción usa Alembic para migraciones.
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")


# Función para verificar conexión
def check_db_connection():
    """
    Verifica que la conexión a la base de datos funcione correctamente.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False