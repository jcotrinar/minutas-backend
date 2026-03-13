"""
scripts/setup_proyectos.py
Crea los 3 proyectos y sus 12 templates en la BD.
Ejecutar una sola vez después del deploy.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import Proyecto, Template, Moneda, ColorSemaforo

PROYECTOS = [
    {
        "nombre": "Sol y Luna Malabrigo",
        "descripcion": "Proyecto Sol & Luna Malabrigo Campo Club",
        "moneda": Moneda.SOLES,
        "templates": {
            ColorSemaforo.VERDE:    "sol_luna/VERDE.docx",
            ColorSemaforo.AMARILLO: "sol_luna/AMARILLO.docx",
            ColorSemaforo.AZUL:     "sol_luna/AZUL.docx",
            ColorSemaforo.ROJO:     "sol_luna/ROJO.docx",
        }
    },
    {
        "nombre": "Residencial Nuevo Santa Beatriz",
        "descripcion": "Residencial Nuevo Santa Beatriz - Huanchaco",
        "moneda": Moneda.DOLARES,
        "templates": {
            ColorSemaforo.VERDE:    "santa_beatriz/VERDE.docx",
            ColorSemaforo.AMARILLO: "santa_beatriz/AMARILLO.docx",
            ColorSemaforo.AZUL:     "santa_beatriz/AZUL.docx",
            ColorSemaforo.ROJO:     "santa_beatriz/ROJO.docx",
        }
    },
    {
        "nombre": "Residencial Los Laureles de Castilla",
        "descripcion": "Residencial Los Laureles de Castilla - Huanchaco",
        "moneda": Moneda.DOLARES,
        "templates": {
            ColorSemaforo.VERDE:    "laureles/VERDE.docx",
            ColorSemaforo.AMARILLO: "laureles/AMARILLO.docx",
            ColorSemaforo.AZUL:     "laureles/AZUL.docx",
            ColorSemaforo.ROJO:     "laureles/ROJO.docx",
        }
    },
]

def main():
    db = SessionLocal()
    try:
        for p_data in PROYECTOS:
            # Verificar si ya existe
            existente = db.query(Proyecto).filter(Proyecto.nombre == p_data["nombre"]).first()
            if existente:
                print(f"  YA EXISTE: {p_data['nombre']}")
                proyecto = existente
            else:
                proyecto = Proyecto(
                    nombre=p_data["nombre"],
                    descripcion=p_data["descripcion"],
                    moneda=p_data["moneda"],
                )
                db.add(proyecto)
                db.flush()
                print(f"  CREADO: {p_data['nombre']} (id={proyecto.id})")

            # Templates
            for color, ruta in p_data["templates"].items():
                t = db.query(Template).filter(
                    Template.proyecto_id == proyecto.id,
                    Template.color == color
                ).first()
                if not t:
                    db.add(Template(proyecto_id=proyecto.id, color=color, ruta=ruta))
                    print(f"    + template {color.value}")

        db.commit()
        print("\nSetup completado.")

        # Mostrar IDs para referencia
        print("\nProyectos en BD:")
        for p in db.query(Proyecto).all():
            print(f"  id={p.id} | {p.nombre} | {p.moneda.value}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
