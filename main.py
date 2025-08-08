from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List
import pandas as pd

from database import SessionLocal, engine
from models import Base, Department, Job, Employee
from schemas import HiresPerQuarter, DeptHiresAvg

# Crear tablas (solo en desarrollo podís descomentar drop_all)
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Migración desde CSV",
    version="1.0.0"
)

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función pa partir en bloques
def partir_en_bloques(iterable, size: int):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

# Filtrar sólo los campos del modelo
def filtrar_campos(modelo, data: dict):
    permitidos = {c.key for c in inspect(modelo).mapper.column_attrs}
    return {k: v for k, v in data.items() if k in permitidos and pd.notna(v)}


@app.post(
    "/cargar-csv/departamentos", 
    summary="Subir archivo departments.csv"
)
async def cargar_departamentos(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_db)
):
    if archivo.filename != "departments.csv":
        raise HTTPException(
            status_code=400,
            detail="El archivo tiene que llamarse departments.csv"
        )
    df = pd.read_csv(
        archivo.file,
        header=None,
        names=["id", "name"]
    )
    filas = df.to_dict(orient="records")
    total = 0
    for lote in partir_en_bloques(filas, 1000):
        objs = [Department(**filtrar_campos(Department, fila)) for fila in lote]
        db.add_all(objs)
        db.commit()
        total += len(objs)
    return {"mensaje": f"{total} departamentos agregados"}

@app.post(
    "/cargar-csv/cargos", 
    summary="Subir archivo jobs.csv"
)
async def cargar_cargos(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_db)
):
    if archivo.filename != "jobs.csv":
        raise HTTPException(
            status_code=400,
            detail="El archivo tiene que llamarse jobs.csv"
        )
    df = pd.read_csv(
        archivo.file,
        header=None,
        names=["id", "title"]
    )
    filas = df.to_dict(orient="records")
    total = 0
    for lote in partir_en_bloques(filas, 1000):
        objs = [Job(**filtrar_campos(Job, fila)) for fila in lote]
        db.add_all(objs)
        db.commit()
        total += len(objs)
    return {"mensaje": f"{total} cargos agregados"}

@app.post(
    "/cargar-csv/empleados-contratados", 
    summary="Subir archivo hired_employees.csv"
)
async def cargar_empleados(
    archivo: UploadFile = File(...),
    db: Session = Depends(obtener_db)
):
    if archivo.filename != "hired_employees.csv":
        raise HTTPException(
            status_code=400,
            detail="El archivo tiene que llamarse hired_employees.csv"
        )
    df = pd.read_csv(
        archivo.file,
        header=None,
        names=["id", "name", "hire_date", "department_id", "job_id"],
        parse_dates=["hire_date"]
    )
    filas = df.to_dict(orient="records")
    total = 0
    for lote in partir_en_bloques(filas, 1000):
        objs = [Employee(**filtrar_campos(Employee, fila)) for fila in lote]
        db.add_all(objs)
        db.commit()
        total += len(objs)
    return {"mensaje": f"{total} empleados agregados"}

@app.get(
    "/contrataciones-por-trimestre", 
    response_model=List[HiresPerQuarter],
    summary="Contrataciones por trimestre 2021"
)
def obtener_contrataciones_trimestre(db: Session = Depends(obtener_db)):
    consulta = text(
        """
        SELECT
          d.name AS department,
          j.title AS job,
          COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.hire_date) = 1) AS q1,
          COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.hire_date) = 2) AS q2,
          COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.hire_date) = 3) AS q3,
          COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.hire_date) = 4) AS q4
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        JOIN jobs j ON e.job_id = j.id
        WHERE EXTRACT(YEAR FROM e.hire_date) = 2021
        GROUP BY d.name, j.title
        ORDER BY d.name, j.title;
        """
    )
    result = db.execute(consulta)
    return result.mappings().all()

@app.get(
    "/departamentos-sobre-promedio-contrataciones", 
    response_model=List[DeptHiresAvg],
    summary="Deptos con contrataciones sobre el promedio en 2021"
)
def obtener_deptos_sobre_promedio(db: Session = Depends(obtener_db)):
    consulta = text(
        """
        WITH hires_per_dept AS (
          SELECT department_id, COUNT(*) AS hired_count
          FROM employees
          WHERE EXTRACT(YEAR FROM hire_date) = 2021
          GROUP BY department_id
        ),
        avg_hires AS (
          SELECT AVG(hired_count) AS avg_hired
          FROM hires_per_dept
        )
        SELECT d.id, d.name, h.hired_count
        FROM hires_per_dept h
        JOIN departments d ON d.id = h.department_id
        CROSS JOIN avg_hires a
        WHERE h.hired_count > a.avg_hired
        ORDER BY h.hired_count DESC;
        """
    )
    result = db.execute(consulta)
    return result.mappings().all()