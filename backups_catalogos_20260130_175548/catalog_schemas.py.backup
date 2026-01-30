from pydantic import BaseModel, ConfigDict

class RegionOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class ProvinceOut(BaseModel):
    id: int
    code: str
    name: str
    region_id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class CityOut(BaseModel):
    id: int
    name: str
    province_id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
