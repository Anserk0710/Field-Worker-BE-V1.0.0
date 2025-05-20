from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.db.database import engine, database
from app.db import models
from app.routes import user, auth, division, absensi, visitor, project


app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(division.router)
app.include_router(absensi.router)
app.include_router(visitor.router)
app.include_router(project.router)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def root():
    return {"message": "Field Worker Backend API"}
