"""
generador_minutas.py — Genera minutas Word reemplazando marcadores «VARIABLE».
Universal para todos los proyectos. Trabaja directo en XML para preservar formato.
"""
import os
import re
import zipfile
import shutil
from pathlib import Path
from lxml import etree

from app.services.calculos import compilar_variables

TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "app/templates"))
OUTPUT_DIR    = Path(os.getenv("OUTPUT_DIR",    "minutas_generadas"))

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _texto_runs(runs):
    return "".join(
        "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
        for r in runs
    )


def _reemplazar_xml(xml_bytes: bytes, variables: dict) -> bytes:
    patron = re.compile(r"«([^»]*)»")
    root   = etree.fromstring(xml_bytes)

    for parrafo in root.iter(f"{{{W}}}p"):
        runs = parrafo.findall(f".//{{{W}}}r")
        if not runs:
            continue
        texto = _texto_runs(runs)
        if "«" not in texto:
            continue

        def reemplazar(m):
            return str(variables.get(m.group(1), ""))

        texto_nuevo = patron.sub(reemplazar, texto)

        # Poner texto en el primer run que tenía «, vaciar el resto
        run_destino = next((r for r in runs if "«" in _texto_runs([r])), runs[0])

        for t in run_destino.findall(f"{{{W}}}t"):
            run_destino.remove(t)

        nuevo_t = etree.SubElement(run_destino, f"{{{W}}}t")
        nuevo_t.text = texto_nuevo
        if texto_nuevo and (texto_nuevo[0] == " " or texto_nuevo[-1] == " "):
            nuevo_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

        for r in runs:
            if r is run_destino:
                continue
            if _texto_runs([r]):
                for t in r.findall(f"{{{W}}}t"):
                    r.remove(t)

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def generar_minuta(contrato, lote, template: "Template", distrito1=None, distrito2=None) -> Path:
    """
    Genera el .docx para el contrato dado usando el template indicado.
    Retorna la ruta del archivo generado.
    """
    template_path = TEMPLATES_DIR / template.ruta
    if not template_path.exists():
        raise FileNotFoundError(f"Template no encontrado: {template_path}")

    variables = compilar_variables(contrato, lote, distrito1, distrito2)

    # Ruta de salida
    fecha          = contrato.fecha
    nombre_arch    = f"MINUTA_{contrato.numero:04d}_{template.color.value}_{fecha.strftime('%Y%m%d')}.docx"
    carpeta_salida = OUTPUT_DIR / str(fecha.year) / f"{fecha.month:02d}"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida    = carpeta_salida / nombre_arch

    # Leer ZIP, procesar XMLs, reescribir
    with zipfile.ZipFile(str(template_path), "r") as zin:
        archivos = {n: zin.read(n) for n in zin.namelist()}

    xml_targets = ["word/document.xml", "word/header1.xml", "word/header2.xml",
                   "word/footer1.xml",  "word/footer2.xml"]

    for target in xml_targets:
        if target in archivos:
            try:
                archivos[target] = _reemplazar_xml(archivos[target], variables)
            except Exception:
                pass

    import tempfile
    tmp = str(ruta_salida) + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for nombre, data in archivos.items():
            zout.writestr(nombre, data)
    Path(tmp).replace(ruta_salida)

    return ruta_salida
