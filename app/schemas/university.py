from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List


class UniversityBase(BaseModel):
    name: str
    code: str
    acronym: Optional[str] = None
    university_type: str
    accreditation: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    city_id: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UniversityOut(UniversityBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class CareerBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    duration_semesters: Optional[int] = None
    university_id: int
    modality: Optional[str] = None


class CareerOut(CareerBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UniversityWithCareers(UniversityOut):
    careers: List[CareerOut] = []
