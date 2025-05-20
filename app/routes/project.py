from fastapi import APIRouter, HTTPException
from app.db.models import Project
from app.schemas import ProjectCreate, ProjectResponse
from app.db.database import database
from app.utils.qr import generate_qr_base64
import uuid

router = APIRouter()

@router.post("/project", response_model=ProjectResponse)
async def create_project(data: ProjectCreate):
    project_id = str(uuid.uuid4())
    qr_data = f"project{project_id}"
    qr_code = generate_qr_base64(qr_data)

    query = Project.insert().values(
        id=project_id,
        nama_proyek=data.nama_proyek,
        deskripsi=data.deskripsi,
        lokasi=data.lokasi,
        qr_code=qr_code
    )
    try:
        await database.execute(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ProjectResponse(
        id=project_id,
        nama_proyek=data.nama_proyek,
        deskripsi=data.deskripsi,
        lokasi=data.lokasi,
        qr_code=qr_code
    )
