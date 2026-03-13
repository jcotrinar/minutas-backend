from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contratos, lotes, distritos, minutas

app = FastAPI(
    title="Minutas API",
    description="Backend para generación de minutas de compraventa - Grupo D'Mateo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])
app.include_router(lotes.router,     prefix="/lotes",     tags=["Lotes"])
app.include_router(distritos.router, prefix="/distritos", tags=["Distritos"])
app.include_router(minutas.router,   prefix="/minutas",   tags=["Minutas"])

@app.get("/")
def root():
    return {"status": "ok", "mensaje": "Minutas API funcionando"}
