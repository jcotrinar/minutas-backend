"""
scripts/importar_prada2.py — Importa los lotes de Residencial Prada II.
Fuente: scripts/data/prada2_lotes.csv (extraído de "LISTA DE PRECIOS FINAL PRADA 2.pdf").
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

# etapa → (sufijo de manzana, etapa, nombre predio, partida, área del predio en ha)
# La 1ra etapa está en el SUB LOTE A; la 2da y 3ra en el SUB LOTE B.
ETAPAS = {
    1: ("",   "PRIMERA", "SUB LOTE A", "11437364", 15.38),
    2: ("-2", "SEGUNDA", "SUB LOTE B", "11437365", 17.07),
    3: ("-3", "TERCERA", "SUB LOTE B", "11437365", 17.07),
}


def asegurar_columna_etapa():
    columnas = [c["name"] for c in inspect(engine).get_columns("lotes")]
    if "etapa" not in columnas:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE lotes ADD COLUMN etapa VARCHAR(20)"))
        print("  + columna lotes.etapa")


def main():
    asegurar_columna_etapa()

    db = SessionLocal()
    try:
        proyecto = db.query(Proyecto).filter(Proyecto.nombre == PROYECTO).first()
        if not proyecto:
            print(f"ERROR: no existe '{PROYECTO}'. Ejecuta primero scripts/setup_proyectos.py")
            sys.exit(1)

        existentes = db.query(Lote).filter(Lote.proyecto_id == proyecto.id).count()
        if existentes:
            print(f"  YA EXISTEN {existentes} lotes en {PROYECTO}, no se importa nada.")
            return

        lotes = []
        with open(CSV_PATH, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sufijo, etapa, predio, partida, area_predio = ETAPAS[int(row["etapa"])]
                lotes.append(Lote(
                    proyecto_id=proyecto.id, manzana=row["manzana"] + sufijo, numero=row["lote"],
                    area=float(row["area"]), partida=partida, nombre_predio=predio,
                    area_predio=area_predio, etapa=etapa,
                ))
        db.bulk_save_objects(lotes)
        db.commit()

        print(f"  → {len(lotes)} lotes importados en {PROYECTO} (id={proyecto.id})")
        for sufijo, etapa, predio, partida, _ in ETAPAS.values():
            n = db.query(Lote).filter(Lote.proyecto_id == proyecto.id, Lote.etapa == etapa).count()
            print(f"    {etapa} ETAPA: {n} lotes → {predio}, partida {partida}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
