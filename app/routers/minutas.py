from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.generador_minutas import generar_minuta
from app.services.drive_service import subir_minuta

router = APIRouter()


@router.post("/generar", response_model=schemas.MinutaResponse)
def generar(
    data: schemas.MinutaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Genera la minuta Word para el contrato indicado.
    Opcionalmente la sube a Google Drive en background.
    """
    contrato = db.query(models.Contrato).filter(
        models.Contrato.id == data.contrato_id
    ).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    lote      = contrato.lote
    distrito1 = contrato.distrito1
    distrito2 = contrato.distrito2

    try:
        ruta = generar_minuta(contrato, lote, distrito1, distrito2)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando minuta: {e}")

    año = str(contrato.fecha.year)
    mes = f"{contrato.fecha.month:02d}"

    drive_url = None

    if data.subir_a_drive:
        # Subir en background para no bloquear la respuesta
        background_tasks.add_task(subir_minuta, ruta, año, mes)

    return schemas.MinutaResponse(
        contrato_id=contrato.id,
        estado=contrato.estado,
        archivo_local=str(ruta),
        drive_url=drive_url,
        nombre=ruta.name,
    )


@router.get("/descargar/{contrato_id}")
def descargar_minuta(contrato_id: int, db: Session = Depends(get_db)):
    """
    Genera y devuelve el archivo .docx directamente para descarga.
    Útil para la app Android: recibe el archivo y lo muestra/comparte.
    """
    contrato = db.query(models.Contrato).filter(
        models.Contrato.id == contrato_id
    ).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    try:
        ruta = generar_minuta(
            contrato,
            contrato.lote,
            contrato.distrito1,
            contrato.distrito2
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(
        path=str(ruta),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=ruta.name,
    )
