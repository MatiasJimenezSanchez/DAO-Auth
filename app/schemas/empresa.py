from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class EmpresaBase(BaseModel):
    nombre_empresa: str
    slug: str
    tipo_empresa: str = "real_nacional"
    industria: str = "Tecnología"
    descripcion_corta: Optional[str] = None
    pais: str = "Ecuador"

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    descripcion_corta: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None

class EmpresaOut(EmpresaBase):
    id: int
    industria_secundaria: Optional[str] = None
    descripcion_completa: Optional[str] = None
    ciudad: Optional[str] = None
    es_partner_activo: bool = False
    tipo_partnership: str = "basico"
    verificado: bool = False
    total_simulaciones: int = 0
    total_usuarios_inscritos: int = 0
    calificacion_promedio: Decimal = Decimal("0.0")
    esta_activo: bool = True
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
