from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrgCreate(BaseModel):
    name: str
    legal_name: Optional[str] = None
    parent_org_id: Optional[int] = None
    indigenous_led: bool = False
    description: Optional[str] = None
    website: Optional[str] = None
    status: str = "active"


class OrgUpdate(OrgCreate):
    pass


class LocationCreate(BaseModel):
    organization_id: int
    label: Optional[str] = None
    address: Optional[str] = None
    quadrant: Optional[str] = None
    community: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wheelchair_accessible: bool = False
    transit_note: Optional[str] = None
    status: str = "active"


class LocationUpdate(LocationCreate):
    pass


class ServiceCreate(BaseModel):
    location_id: int
    name: str
    description: Optional[str] = None
    primary_category_id: Optional[int] = None
    recovery_subtype_id: Optional[int] = None
    cost_model: str = "unknown"
    access_mode: str = "walk_in"
    referral_required: bool = False
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender_restriction: str = "none"
    capacity: Optional[int] = None
    is_24_7: bool = False
    status: str = "active"
    category_ids: list[int] = Field(default_factory=list)
    population_ids: list[int] = Field(default_factory=list)


class ServiceUpdate(ServiceCreate):
    pass


class SourceCreate(BaseModel):
    url: Optional[str] = None
    title: str
    source_type: str = "website"
    notes: Optional[str] = None


class SaveWithProvenance(BaseModel):
    source_id: Optional[int] = None
    new_source: Optional[SourceCreate] = None
    reason: str
    editor: str = "user"


class ContactCreate(BaseModel):
    owner_type: str
    owner_id: int
    kind: str
    value: str
    is_primary: bool = False


class HourCreate(BaseModel):
    service_id: int
    day_of_week: int
    opens: Optional[str] = None
    closes: Optional[str] = None
    is_24_7: bool = False
    note: Optional[str] = None


class SearchQuery(BaseModel):
    q: Optional[str] = None
    category_id: Optional[int] = None
    recovery_subtype_id: Optional[int] = None
    population_id: Optional[int] = None
    quadrant: Optional[str] = None
    cost_model: Optional[str] = None
    access_mode: Optional[str] = None
    is_24_7: Optional[bool] = None
    wheelchair_accessible: Optional[bool] = None
    status: str = "active"
    limit: int = 50
    offset: int = 0
