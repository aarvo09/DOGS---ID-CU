from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator

# --- Auth Models ---
class LoginRequest(BaseModel):
    email: str = Field(..., description="Administrator email address")
    password: str = Field(..., description="Plaintext password")

class AdminUserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=6)
    role: str = Field("STAFF", pattern="^(SUPER_ADMIN|ADMIN|STAFF)$")

class AdminUserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = Field(None, pattern="^(SUPER_ADMIN|ADMIN|STAFF)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AdminUserResponse

# --- Dog Models ---
class DogCreate(BaseModel):
    dog_uid: Optional[str] = Field(None, description="Optional custom unique dog ID (e.g. CU-DOG-024). Auto-generated if omitted.")
    name: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(..., pattern="^(Male|Female|Unknown)$")
    approx_age: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    photo_url: Optional[str] = None
    status: str = Field("ACTIVE", pattern="^(ACTIVE|MISSING|INACTIVE|DECEASED|TRANSFERRED|UNDER_CARE)$")

class DogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Unknown)$")
    approx_age: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|MISSING|INACTIVE|DECEASED|TRANSFERRED|UNDER_CARE)$")

class HealthOverview(BaseModel):
    vaccination_status: str
    last_vaccination_date: Optional[str] = None
    sterilization_status: str
    health_status: str

class LastSeenInfo(BaseModel):
    location: str
    timestamp: str
    time_ago: str
    activity: Optional[str] = None
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DogPublicResponse(BaseModel):
    dog_uid: str
    name: str
    gender: str
    approx_age: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    status: str
    last_seen: Optional[LastSeenInfo] = None
    health_overview: Optional[HealthOverview] = None
    active_tag: Optional[str] = None

# --- QR Tag Models ---
class QRTagCreate(BaseModel):
    status: str = Field("ACTIVE", pattern="^(ACTIVE|INACTIVE|LOST|DAMAGED|UNASSIGNED|RETIRED)$")
    assign_to_dog_id: Optional[int] = None

class QRTagAssignRequest(BaseModel):
    dog_id: int = Field(..., description="ID of the dog to assign to this tag")

class QRTagUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|LOST|DAMAGED|UNASSIGNED|RETIRED)$")

class TagAssignmentHistoryItem(BaseModel):
    id: int
    dog_id: int
    dog_uid: str
    dog_name: str
    assigned_at: str
    unassigned_at: Optional[str] = None
    assigned_by_name: Optional[str] = None
    status: str

# --- Sighting Models ---
class SightingCreate(BaseModel):
    location_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=150)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    accuracy: Optional[float] = Field(None, ge=0.0)
    activity: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = None
    note: Optional[str] = Field(None, max_length=500)
    submitted_by: Optional[str] = Field("Anonymous Campus Member", max_length=100)

class SightingPublicResponse(BaseModel):
    id: int
    dog_uid: str
    dog_name: str
    location_name: str
    activity: Optional[str] = None
    photo_url: Optional[str] = None
    note: Optional[str] = None
    time_ago: str
    created_at: str

# --- Report Models ---
class ReportCreate(BaseModel):
    report_type: str = Field(..., pattern="^(INJURED|SICK|MISSING|WRONG_INFORMATION|OTHER)$")
    severity: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    description: str = Field(..., min_length=5, max_length=2000)
    location_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=150)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    photo_url: Optional[str] = None
    submitted_by: Optional[str] = Field("Anonymous Campus Member", max_length=100)
    contact_info: Optional[str] = Field(None, max_length=150)

class ReportUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(PENDING|UNDER_REVIEW|RESOLVED|DISMISSED)$")
    admin_notes: Optional[str] = Field(None, max_length=2000)

# --- Health Record Models ---
class HealthRecordCreate(BaseModel):
    vaccination_status: str = Field(..., pattern="^(UP_TO_DATE|DUE|PARTIALLY_VACCINATED|NOT_VACCINATED|UNKNOWN)$")
    last_vaccination_date: Optional[str] = None
    sterilization_status: str = Field(..., pattern="^(STERILIZED|NOT_STERILIZED|PLANNED|UNKNOWN)$")
    health_status: str = Field(..., pattern="^(HEALTHY|NEEDS_ATTENTION|UNDER_TREATMENT|CRITICAL|MONITORING)$")
    notes: Optional[str] = None

class HealthRecordUpdate(BaseModel):
    vaccination_status: Optional[str] = Field(None, pattern="^(UP_TO_DATE|DUE|PARTIALLY_VACCINATED|NOT_VACCINATED|UNKNOWN)$")
    last_vaccination_date: Optional[str] = None
    sterilization_status: Optional[str] = Field(None, pattern="^(STERILIZED|NOT_STERILIZED|PLANNED|UNKNOWN)$")
    health_status: Optional[str] = Field(None, pattern="^(HEALTHY|NEEDS_ATTENTION|UNDER_TREATMENT|CRITICAL|MONITORING)$")
    notes: Optional[str] = None

# --- Campus Location Models ---
class CampusLocationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    area_type: str = Field("ACADEMIC", max_length=50)
    is_active: bool = True

class CampusLocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    area_type: Optional[str] = None
    is_active: Optional[bool] = None

# --- QR Resolution Models ---
class QRResolveResponse(BaseModel):
    status: str
    message: str
    tag_uid: str
    dog_uid: Optional[str] = None
    dog_name: Optional[str] = None
    redirect_url: Optional[str] = None
