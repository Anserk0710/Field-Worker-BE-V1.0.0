from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

class DivisionCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: Role
    division_id: UUID

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    password: Optional[str]
    nama_lengkap: Optional[str]
    division_id: Optional[UUID]

class AbsensiRequest(BaseModel):
    user_id: str
    project_id: str
    division_id: str
    latitude: float
    longitude: float
    photo_base64: str
    type: Literal["masuk", "istirahat", "keluar", "lembur"]
    timezone_offset: Optional[int] = None  # offset in hours from UTC, e.g. 7 for GMT+7

class VisitorRegister(BaseModel):
    nama: Optional[str] = None
    nama_perusahaan: Optional[str] = None
    nomor_telepon: Optional[str] = None
    tujuan: Optional[str] = None
    timezone_offset: Optional[int] = None  # offset in hours from UTC, e.g. 7 for GMT+7

class ProjectCreate(BaseModel):
    nama_proyek: str
    deskripsi: str
    lokasi: str

class ProjectResponse(ProjectCreate):
    id: str
    qr_code: str