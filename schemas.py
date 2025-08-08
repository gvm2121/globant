from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DepartmentIn(BaseModel):
    id: Optional[int] = Field(None, description="ID (omitido si SERIAL)")
    name: Optional[str] = Field(None, description="Nombre del departamento (puede estar en blanco o null)")

    class Config:
        orm_mode = True

class JobIn(BaseModel):
    id: Optional[int] = Field(None, description="ID (omitido si SERIAL)")
    title: Optional[str] = Field(None, description="Título del cargo (puede estar en blanco o null)")

    class Config:
        orm_mode = True

class EmployeeIn(BaseModel):
    id: Optional[int] = Field(None, description="ID (omitido si SERIAL)")
    name: Optional[str] = Field(None, description="Nombre del empleado (puede estar en blanco o null)")
    hire_date: Optional[datetime] = Field(None, description="Fecha y hora de contratación ISO (puede ser null)")
    department_id: Optional[int] = Field(None, description="ID del departamento (puede ser null)")
    job_id: Optional[int] = Field(None, description="ID del cargo (puede ser null)")

    class Config:
        orm_mode = True

class HiresPerQuarter(BaseModel):
    department: str
    job: str
    q1: int
    q2: int
    q3: int
    q4: int
    class Config:
        allow_population_by_field_name = True

class DeptHiresAvg(BaseModel):
    id: int
    name: str
    hired_count: int

    class Config:
        orm_mode = True