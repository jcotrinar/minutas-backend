"""
generador_minutas.py
Reemplaza los marcadores «VARIABLE» en los templates Word.
Equivalente al Módulo1 (contratos) del VBA original.
"""

import os
import re
from pathlib import Path
from datetime import date
from docx import Document
from docx.oxml.ns import qn
from app.services.calculos import compilar_variables

# Carpeta donde están los 4 templates Word
TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "app/templates"))

# Carpeta donde se guardan las minutas generadas
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "minutas_generadas"))

COLORES_TEMPLATE = {
    "VERDE":    "VERDE.docx",
    "AMARILLO": "AMARILLO.docx",
    "AZUL":     "AZUL.docx",
    "ROJO":     "ROJO.docx",
}


def _reemplazar_en_parrafo(parrafo, variables: dict):
    """
    Reemplaza marcadores «VARIABLE» en un párrafo del Word.
    Maneja el caso donde el marcador está partido entre múltiples runs.
    """
    texto_completo = "".join(run.text for run in parrafo.runs)

    # Buscar si hay algún marcador en este párrafo
    patron = re.compile(r"«([^»]+)»")
    if not patron.search(texto_completo):
        return  # Sin marcadores, no tocar

    # Reconstruir el texto con reemplazos
    def reemplazar(match):
        clave = match.group(1)
        return variables.get(clave, match.group(0))  # Si no existe, dejar el marcador

    nuevo_texto = patron.sub(reemplazar, texto_completo)

    # Vaciar todos los runs excepto el primero, poner el texto en el primero
    if parrafo.runs:
        parrafo.runs[0].text = nuevo_texto
        for run in parrafo.runs[1:]:
            run.text = ""


def _reemplazar_en_tabla(tabla, variables: dict):
    """Recorre todas las celdas de una tabla y reemplaza marcadores."""
    for fila in tabla.rows:
        for celda in fila.cells:
            for parrafo in celda.paragraphs:
                _reemplazar_en_parrafo(parrafo, variables)
            # Tablas anidadas
            for subtabla in celda.tables:
                _reemplazar_en_tabla(subtabla, variables)


def generar_minuta(contrato, lote, distrito1=None, distrito2=None) -> Path:
    """
    Genera la minuta Word para el contrato dado.
    Retorna la ruta del archivo generado.
    """
    estado = contrato.estado
    template_nombre = COLORES_TEMPLATE.get(estado)

    if not template_nombre:
        raise ValueError(f"Estado desconocido: {estado}")

    template_path = TEMPLATES_DIR / template_nombre
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template no encontrado: {template_path}\n"
            f"Asegúrate de copiar los 4 archivos .docx a: {TEMPLATES_DIR}"
        )

    # Compilar todas las variables
    variables = compilar_variables(contrato, lote, distrito1, distrito2)

    # Abrir el template
    doc = Document(str(template_path))

    # Reemplazar en párrafos del cuerpo principal
    for parrafo in doc.paragraphs:
        _reemplazar_en_parrafo(parrafo, variables)

    # Reemplazar en tablas
    for tabla in doc.tables:
        _reemplazar_en_tabla(tabla, variables)

    # Reemplazar en headers y footers
    for seccion in doc.sections:
        for parrafo in seccion.header.paragraphs:
            _reemplazar_en_parrafo(parrafo, variables)
        for parrafo in seccion.footer.paragraphs:
            _reemplazar_en_parrafo(parrafo, variables)

    # Determinar nombre y carpeta de salida (igual que la macro: año/mes/archivo)
    fecha        = contrato.fecha
    año          = str(fecha.year)
    mes          = f"{fecha.month:02d}"
    nombre_arch  = f"MINUTA_{contrato.numero:04d}_{estado}_{fecha.strftime('%Y%m%d')}.docx"

    carpeta_salida = OUTPUT_DIR / año / mes
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    ruta_salida = carpeta_salida / nombre_arch
    doc.save(str(ruta_salida))

    return ruta_salida
