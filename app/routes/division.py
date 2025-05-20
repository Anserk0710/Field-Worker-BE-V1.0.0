from fastapi import APIRouter, Depends
from app.db.database import database
from app.db.models import Division
from app.schemas import DivisionCreate
import uuid
from app.utils.jwt_handler import JWTBearer

router = APIRouter()

@router.post("/divisions", dependencies=[Depends(JWTBearer(allowed_roles=["admin", "staff"]))])
async def create_division(division: DivisionCreate):
    query = Division.insert().values(id=str(uuid.uuid4()), name=division.name)
    await database.execute(query)
    return {"message": "Division created successfully"}
