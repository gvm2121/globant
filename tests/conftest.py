import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import sys, os

# Aseguramos ruta al proyecto
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from database import engine as real_engine
from models import Base
from main import app, obtener_db

# URL para tests en memoria
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="session")
def motor_db():
    """Crea y destruye el esquema de la BD para toda la sesión de tests"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def sesion_db(motor_db):
    """Provee una sesión de DB aislada por test"""
    conexion = motor_db.connect()
    transaccion = conexion.begin()
    session = TestingSessionLocal(bind=conexion)
    yield session
    session.close()
    transaccion.rollback()
    conexion.close()

@pytest.fixture(scope="function")
def cliente_api(sesion_db):
    """Cliente de pruebas que sobreescribe la dependencia de la BD"""
    def override_obtener_db():
        try:
            yield sesion_db
        finally:
            sesion_db.close()

    app.dependency_overrides[obtener_db] = override_obtener_db
    yield TestClient(app)
    app.dependency_overrides.clear()
