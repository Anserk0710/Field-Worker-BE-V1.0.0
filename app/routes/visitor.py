from fastapi import APIRouter, Depends
from app.db.models import Visitor
from app.utils.jwt_handler import JWTBearer
from sqlalchemy import select
from app.schemas import VisitorRegister
from app.db.database import database
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/visitor")
async def register_visitor(visitor: VisitorRegister):
    offset_hours = visitor.timezone_offset if visitor.timezone_offset is not None else 7
    timestamp = datetime.utcnow() + timedelta(hours=offset_hours)
    query = Visitor.insert().values(
        id=str(uuid.uuid4()),
        nama=visitor.nama,
        nama_perusahaan=visitor.nama_perusahaan,
        no_telp=visitor.nomor_telepon,
        tujuan=visitor.tujuan,
        is_inducted=False,
        timestamp=timestamp
    )
    await database.execute(query)
    return {"message": "Visitor registered successfully"}

@router.get("/visitor", dependencies=[Depends(JWTBearer(allowed_roles=["ADMIN, STAFF"]))])
async def get_all_visitor():
    query = select(Visitor)
    result = await database.execute(query)
    return result
