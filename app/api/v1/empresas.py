from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut

router = APIRouter()

@router.get("/", response_model=List[EmpresaOut])
def listar_empresas(
    skip: int = 0,
    limit: int = 100,
    tipo_empresa: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Empresa)
    if tipo_empresa:
        query = query.filter(Empresa.tipo_empresa == tipo_empresa)
    empresas = query.offset(skip).limit(limit).all()
    return empresas

@router.get("/{id}", response_model=EmpresaOut)
def obtener_empresa(id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {id} no encontrada")
    return empresa

@router.post("/", response_model=EmpresaOut, status_code=201)
def crear_empresa(empresa_data: EmpresaCreate, db: Session = Depends(get_db)):
    empresa_existente = db.query(Empresa).filter(
        Empresa.nombre_empresa == empresa_data.nombre_empresa
    ).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="Empresa ya existe")
    
    nueva_empresa = Empresa(**empresa_data.model_dump(exclude_unset=True))
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa

@router.put("/{id}", response_model=EmpresaOut)
def actualizar_empresa(id: int, empresa_data: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {id} no encontrada")
    
    update_data = empresa_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(empresa, field, value)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.delete("/{id}", status_code=204)
def eliminar_empresa(id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {id} no encontrada")
    db.delete(empresa)
    db.commit()
    return None
