from fastapi import APIRouter, HTTPException, Depends, Request
from app.db.database import database
from app.db.models import User, Induction, Division
from app.utils.security import hash_password
from app.schemas import UserUpdate
from sqlalchemy import select, and_
from app.utils.jwt_handler import JWTBearer
from typing import Optional
import bcrypt


router = APIRouter()


@router.get("/users")
async def list_users(division_id: Optional[str] = None, token: dict = Depends(JWTBearer(allowed_roles=["admin", "staff"]))):
    query = select(User, Division).join(Division, Division.c.id == User.c.division_id)

    if division_id:
        query = query.where(User.c.division_id == division_id)

    rows = await database.fetch_all(query)
    return [
        {
            "username": r["username"],
            "nama_lengkap": r["nama_lengkap"],
            "role": r["role"],
            "division": r["name"],
            "is_active": r["is_active"],
            "is_inducted": r["is_inducted"]
        }
        for r in rows
    ]

@router.get("/me")
async def get_current_user(request: Request, token: dict = Depends(JWTBearer())):
    user = request.state.user
    query = select(User, Division.c.name.label("division_name")).join(Division, Division.c.id == User.c.division_id).where(User.c.id == user["id"])
    result = await database.fetch_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return {
        "username": result["username"],
        "nama_lengkap": result["nama_lengkap"],
        "division": result["division_name"],
        "is_active": result["is_active"],
    }

@router.put("/users/{user_id}")
async def update_user(user_id: str, data:UserUpdate, token: dict = Depends(JWTBearer(allowed_roles=["admin", "staff"]))):
    update_data = {}

    if data.password:
        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())
        update_data["password"] = hashed.decode()

    if data.nama_lengkap:
        update_data["nama_lengkap"] = data.nama_lengkap

    if data.division_id:
        update_data["division_id"] = data.division_id

    query = User.update().where(User.c.id == user_id).values(**update_data)
    await database.execute(query)
    return {"message": "User berhasil diubah"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, token: dict = Depends(JWTBearer(allowed_roles=["admin", "staff"]))):
    query = User.update().where(User.c.id == user_id).values(is_active=False)
    await database.execute(query)
    return {"message": "User berhasil dihapus"}

@router.get("/divisions")
async def get_all_divisions(token: dict = Depends(JWTBearer())):
    query = Division.select()
    result = await database.fetch_all(query)
    return result
