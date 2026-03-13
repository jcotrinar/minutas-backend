"""
generador_minutas.py — Genera minutas Word reemplazando marcadores «VARIABLE».
Universal para todos los proyectos. Trabaja directo en XML para preservar formato.

Fix v2:
- Marcadores partidos en múltiples runs se unen correctamente
- El texto reemplazado hereda el formato (rPr) del primer run que contenía «
- No propaga negrita ni estilos de runs vacíos o adyacentes
"""
import os
import re
import zipfile
from pathlib import Path
from copy import deepcopy
from lxml import etree

from app.services.calculos import compilar_variables

TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "app/templates"))
OUTPUT_DIR    = Path(os.getenv("OUTPUT_DIR",    "minutas_generadas"))

W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"


def _run_text(run) -> str:
    return "".join(t.text or "" for t in run.findall(f"{{{W}}}t"))


def _parrafo_text(runs) -> str:
    return "".join(_run_text(r) for r in runs)


def _get_rpr(run):
    return run.find(f"{{{W}}}rPr")


def _limpiar_rpr_negrita(rpr):
    """Elimina w:b y w:bCs para no propagar negrita del marcador al valor."""
    if rpr is None:
        return None
    rpr = deepcopy(rpr)
    for tag in [f"{{{W}}}b", f"{{{W}}}bCs"]:
        for elem in rpr.findall(tag):
            rpr.remove(elem)
    return rpr


def _reemplazar_parrafo(parrafo, variables: dict):
    patron = re.compile(r"«([^»]*)»")

    runs = parrafo.findall(f".//{{{W}}}r")
    if not runs:
        return

    texto_completo = _parrafo_text(runs)
    if "«" not in texto_completo:
        return

    # rPr del primer run que contiene «
    rpr_base = None
    for r in runs:
        if "«" in _run_text(r):
            rpr_base = _get_rpr(r)
            break
    rpr_limpio = _limpiar_rpr_negrita(rpr_base)

    # Reemplazar marcadores
    def reemplazar(m):
        clave = m.group(1)
        return str(variables.get(clave, f"«{clave}»"))

    texto_nuevo = patron.sub(reemplazar, texto_completo)

    # Eliminar todos los runs del párrafo
    for r in parrafo.findall(f"{{{W}}}r"):
        parrafo.remove(r)
    for hlink in parrafo.findall(f".//{{{W}}}hyperlink"):
        for r in hlink.findall(f"{{{W}}}r"):
            hlink.remove(r)

    # Insertar run único después de pPr
    pPr = parrafo.find(f"{{{W}}}pPr")
    insert_pos = (list(parrafo).index(pPr) + 1) if pPr is not None else 0

    nuevo_run = etree.Element(f"{{{W}}}r")
    if rpr_limpio is not None:
        nuevo_run.append(rpr_limpio)
    t = etree.SubElement(nuevo_run, f"{{{W}}}t")
    t.text = texto_nuevo
    if texto_nuevo and (texto_nuevo[0] == " " or texto_nuevo[-1] == " "):
        t.set(f"{{{XML}}}space", "preserve")

    parrafo.insert(insert_pos, nuevo_run)


def _reemplazar_xml(xml_bytes: bytes, variables: dict) -> bytes:
    root = etree.fromstring(xml_bytes)
    for parrafo in root.iter(f"{{{W}}}p"):
        try:
            _reemplazar_parrafo(parrafo, variables)
        except Exception:
            pass
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def generar_minuta(contrato, lote, template, distrito1=None, distrito2=None) -> Path:
    template_path = TEMPLATES_DIR / template.ruta
    if not template_path.exists():
        raise FileNotFoundError(f"Template no encontrado: {template_path}")

    variables = compilar_variables(contrato, lote, distrito1, distrito2)

    fecha          = contrato.fecha
    nombre_arch    = f"MINUTA_{contrato.numero:04d}_{template.color.value}_{fecha.strftime('%Y%m%d')}.docx"
    carpeta_salida = OUTPUT_DIR / str(fecha.year) / f"{fecha.month:02d}"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida    = carpeta_salida / nombre_arch

    with zipfile.ZipFile(str(template_path), "r") as zin:
        archivos = {n: zin.read(n) for n in zin.namelist()}

    xml_targets = [
        "word/document.xml",
        "word/header1.xml", "word/header2.xml", "word/header3.xml",
        "word/footer1.xml",  "word/footer2.xml",  "word/footer3.xml",
    ]
    for target in xml_targets:
        if target in archivos:
            try:
                archivos[target] = _reemplazar_xml(archivos[target], variables)
            except Exception:
                pass

    tmp = str(ruta_salida) + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for nombre, data in archivos.items():
            zout.writestr(nombre, data)
    Path(tmp).replace(ruta_salida)

    return ruta_salida