from sqlalchemy import Table, Column, String, ForeignKey, Boolean, Enum, DateTime, Text, Float
import uuid
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.types import Enum as SqlAlchemyEnum
import enum
from app.db.database import metadata
from datetime import datetime



class Role(enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

Division = Table (
    "division",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("name", String(255), nullable=False)
)

User = Table (
    "user",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("username", String(50), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("nama_lengkap", String(100), nullable=False),
    Column("role", SqlAlchemyEnum(Role), nullable=False, default=Role.USER),
    Column("no_telp", String(15), nullable=False),
    Column("division_id", CHAR(36), ForeignKey("division.id"), nullable=False),
    Column("is_inducted", Boolean, default=False, server_default="0"),
    Column("is_active", Boolean, default=True, server_default="1"),
)

Induction = Table (
    "induction",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("user_id", CHAR(36), ForeignKey("user.id")),
    Column("division_id", CHAR(36), ForeignKey("division.id")),
    Column("induction_date", DateTime, default=datetime.utcnow),
)

LogAbsensi = Table (
    "log_absensi",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("user_id", CHAR(36), ForeignKey("user.id")),
    Column("Poject_id", String, ForeignKey("project.id")),
    Column("Division_id", String, ForeignKey("division.id")),
    Column("nama_lengkap", String(100), nullable=True),
    Column("username", String(50), nullable=True),
    Column("type", Enum("Masuk", "Istirahat", "Keluar", "Lembur", name="log_absensi_type"), nullable=False),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("photo_url", Text),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

Visitor = Table(
    "visitor",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("nama", String(100), nullable=False),
    Column("nama_perusahaan", String(100), nullable=False),
    Column("no_telp", String(15), nullable=False),
    Column("tujuan", String(100), nullable=False),
    Column("is_inducted", Boolean, default=False, server_default="0"),
    Column("timestamp", DateTime, default=datetime.utcnow)
)

Project = Table(
    "project",
    metadata,
    Column("id", CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("nama_proyek", String(100), nullable=False),
    Column("deskripsi", Text),
    Column("lokasi", String),
    Column("timestamp", DateTime, default=datetime.utcnow),
    Column("qr_code", Text)
)