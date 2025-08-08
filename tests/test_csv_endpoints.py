import io
import pytest


def test_carga_departamentos(cliente_api):
    """Test para el endpoint de carga de departamentos"""
    data = "1,Dept A\n2,Dept B\n"
    response = cliente_api.post(
        "/cargar-csv/departamentos",
        files={"archivo": ("departments.csv", io.BytesIO(data.encode()), "text/csv")}
    )
    assert response.status_code == 200
    assert "2 departamentos agregados" in response.json()["mensaje"]


def test_carga_cargos(cliente_api):
    """Test para el endpoint de carga de cargos"""
    data = "1,Job A\n"
    response = cliente_api.post(
        "/cargar-csv/cargos",
        files={"archivo": ("jobs.csv", io.BytesIO(data.encode()), "text/csv")}
    )
    assert response.status_code == 200
    assert "1 cargos agregados" in response.json()["mensaje"]


def test_carga_empleados_contratados(cliente_api):
    """Test para el endpoint de carga de empleados contratados"""
    csv = "1,Emp A,2021-01-15 00:00:00,1,1\n"
    response = cliente_api.post(
        "/cargar-csv/empleados-contratados",
        files={"archivo": ("hired_employees.csv", io.BytesIO(csv.encode()), "text/csv")}
    )
    assert response.status_code == 200
    assert "1 empleados agregados" in response.json()["mensaje"]