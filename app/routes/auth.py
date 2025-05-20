from fastapi import APIRouter, HTTPException
from app.db.database import database
from app.db.models import User, Induction
from app.utils.security import verify_password, hash_password
from app.utils.jwt_handler import create_token
from app.schemas import UserLogin, UserCreate
from sqlalchemy import select
import uuid

router = APIRouter()

@router.post("/register-worker")
async def register_worker(user: UserCreate):
    user_id = str(uuid.uuid4())
    try:
        existing_user = await database.fetch_one(select(User).where(User.c.username == user.username))
        if existing_user:
            raise HTTPException(status_code=400, detail="Username sudah terdaftar")

        query = User.insert().values(
            id=user_id,
            username=user.username,
            password=hash_password(user.password),
            role=user.role,
            nama_lengkap=user.nama_lengkap,
            is_inducted=False,
            is_active=False,
            division_id=str(user.division_id)
        )
        await database.execute(query)

        induction_query = Induction.insert().values(
            id=str(uuid.uuid4()),
            user_id=user_id,
            division_id=str(user.division_id)
        )
        await database.execute(induction_query)

        return {"message": "User berhasil terdaftar"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(login_data: UserLogin):
    query = select(User).where(User.c.username == login_data.username)
    result = await database.fetch_one(query)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(login_data.password, result["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not result["is_active"]:
        raise HTTPException(status_code=401, detail="Inactive user")

    if not result["is_inducted"]:
        raise HTTPException(status_code=401, detail="User not inducted")

    token = create_token({"id": result["id"], "username": result["username"], "role": result["role"].value})

    return {
        "username": result["username"],
        "role": result["role"].value,
        "nama_lengkap": result["nama_lengkap"],
        "token": token
    }
        
