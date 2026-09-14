"""
scripts/importar_prada2.py — Importa los lotes de Residencial Prada II.
Fuente: scripts/data/prada2_lotes.csv (extraído de "LISTA DE PRECIOS FINAL PRADA 2.pdf").
Si el proyecto ya tiene lotes, solo actualiza predio, partida, área y plazo de entrega de cada etapa.
Uso:
  python scripts/setup_proyectos.py     # crea el proyecto y sus templates
  python scripts/importar_prada2.py
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import inspect, text
from app.database import SessionLocal, engine
from app.models import Proyecto, Lote

PROYECTO = "Residencial Prada II"
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "prada2_lotes.csv")

# etapa → (sufijo de manzana, etapa, nombre predio, partida, área del predio en ha, meses de entrega)
# La 1ra etapa está en el SUB LOTE A; la 2da y 3ra en el SUB LOTE B.
ETAPAS = {
    1: ("",   "PRIMERA", "SUB LOTE A", "11437364", 15.38, 18),
    2: ("-2", "SEGUNDA", "SUB LOTE B", "11437365", 17.07, 24),
    3: ("-3", "TERCERA", "SUB LOTE B", "11437365", 17.07, 30),
}

COLUMNAS_NUEVAS = {"etapa": "VARCHAR(20)", "plazo_entrega": "INTEGER"}


def asegurar_columnas():
    columnas = [c["name"] for c in inspect(engine).get_columns("lotes")]
    for nombre, tipo in COLUMNAS_NUEVAS.items():
        if nombre not in columnas:
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE lotes ADD COLUMN {nombre} {tipo}"))
            print(f"  + columna lotes.{nombre}")


def importar_lotes(db, proyecto):
    lotes = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sufijo, etapa, predio, partida, area_predio, plazo = ETAPAS[int(row["etapa"])]
            lotes.append(Lote(
                proyecto_id=proyecto.id, manzana=row["manzana"] + sufijo, numero=row["lote"],
                area=float(row["area"]), partida=partida, nombre_predio=predio,
                area_predio=area_predio, etapa=etapa, plazo_entrega=plazo,
            ))
    db.bulk_save_objects(lotes)
    db.commit()
    print(f"  → {len(lotes)} lotes importados en {PROYECTO} (id={proyecto.id})")


def actualizar_lotes(db, proyecto):
    for _, etapa, predio, partida, area_predio, plazo in ETAPAS.values():
        db.query(Lote).filter(Lote.proyecto_id == proyecto.id, Lote.etapa == etapa).update(
            {"nombre_predio": predio, "partida": partida, "area_predio": area_predio, "plazo_entrega": plazo},
            synchronize_session=False,
        )
    db.commit()


def main():
    asegurar_columnas()

    db = SessionLocal()
    try:
        proyecto = db.query(Proyecto).filter(Proyecto.nombre == PROYECTO).first()
        if not proyecto:
            print(f"ERROR: no existe '{PROYECTO}'. Ejecuta primero scripts/setup_proyectos.py")
            sys.exit(1)

        existentes = db.query(Lote).filter(Lote.proyecto_id == proyecto.id).count()
        if existentes:
            print(f"  YA EXISTEN {existentes} lotes en {PROYECTO}, se actualizan los datos de cada etapa.")
            actualizar_lotes(db, proyecto)
        else:
            importar_lotes(db, proyecto)

        for _, etapa, predio, partida, area_predio, plazo in ETAPAS.values():
            n = db.query(Lote).filter(
                Lote.proyecto_id == proyecto.id, Lote.etapa == etapa, Lote.plazo_entrega == plazo,
                Lote.partida == partida,
            ).count()
            print(f"    {etapa} ETAPA: {n} lotes → {predio}, partida {partida}, {area_predio} ha, entrega {plazo} meses")
    finally:
        db.close()


if __name__ == "__main__":
    main()
