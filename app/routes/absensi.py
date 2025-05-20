from fastapi import APIRouter, Depends, Request
from app.utils.jwt_handler import JWTBearer
from app.db.models import LogAbsensi
from app.schemas import AbsensiRequest
from typing import Optional
from app.db.database import database
from sqlalchemy import select
from datetime import datetime, timedelta
from app.utils.photo import save_base64_image
import uuid

router = APIRouter()

@router.post("/absensi", dependencies=[Depends(JWTBearer(allowed_roles=["STAFF", "USER"]))])
async def log_absensi(request: Request, body:AbsensiRequest):
    photo_path = save_base64_image(body.photo_base64)
    user = request.state.user
    offset_hours = body.timezone_offset if body.timezone_offset is not None else 7
    timestamp = datetime.utcnow() + timedelta(hours=offset_hours)
    query = LogAbsensi.insert().values(
        id=str(uuid.uuid4()),
        user_id=user["id"],
        Poject_id=body.project_id,
        Division_id=body.division_id,
        nama_lengkap=user.get("nama_lengkap"),
        username=user.get("username"),
        latitude=body.latitude,
        longitude=body.longitude,
        photo_url=photo_path,
        type=body.type,
        timestamp=timestamp
    )
    await database.execute(query)
    return {"message": f"Absen {body.type} berhasil", "photo_url": photo_path}

@router.get("/absensi")
async def get_absensi(user_id: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None):
    query = select(LogAbsensi)

    if user_id:
        query = query.where(LogAbsensi.c.user_id == user_id)

    if start and end:
        try:
            start_date = datetime.fromisoformat(start)
            end_date = datetime.fromisoformat(end)
            query = query.where(LogAbsensi.c.timestamp.between(start_date, end_date))
        except ValueError:
            return {"error" : "Invalid date format"}
        
    results = await database.fetch_all(query)
    return results
