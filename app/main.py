from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import contratos, lotes, distritos, minutas, proyectos

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Minutas API v2",
    description="Backend para generación de minutas — Grupo D'Mateo",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proyectos.router, prefix="/proyectos", tags=["Proyectos"])
app.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])
app.include_router(lotes.router,     prefix="/lotes",     tags=["Lotes"])
app.include_router(distritos.router, prefix="/distritos", tags=["Distritos"])
app.include_router(minutas.router,   prefix="/minutas",   tags=["Minutas"])

@app.get("/")
def root():
    return {"status": "ok", "version": "2.0", "mensaje": "Minutas API v2 funcionando"}
