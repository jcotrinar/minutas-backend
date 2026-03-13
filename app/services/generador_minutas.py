"""
generador_minutas.py — Genera minutas Word reemplazando marcadores «VARIABLE».
Universal para todos los proyectos. Trabaja directo en XML para preservar formato.

Fix v3:
- Preserva negrita y cualquier formato (rPr) de cada segmento del párrafo
- Texto entre marcadores mantiene el rPr del run original que lo contenía
- El valor reemplazado hereda el rPr del run que contenía el «marcador»
- Marcadores partidos en múltiples runs se unen correctamente
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
    rpr = run.find(f"{{{W}}}rPr")
    return deepcopy(rpr) if rpr is not None else None


def _make_run(texto: str, rpr) -> etree.Element:
    """Crea un <w:r> con el texto y formato dados."""
    run = etree.Element(f"{{{W}}}r")
    if rpr is not None:
        run.append(deepcopy(rpr))
    t = etree.SubElement(run, f"{{{W}}}t")
    t.text = texto
    if texto and (texto[0] == " " or texto[-1] == " "):
        t.set(f"{{{XML}}}space", "preserve")
    return run


def _reemplazar_parrafo(parrafo, variables: dict):
    patron = re.compile(r"«([^»]*)»")

    runs = parrafo.findall(f".//{{{W}}}r")
    if not runs:
        return

    texto_completo = _parrafo_text(runs)
    if "«" not in texto_completo:
        return

    # ── Construir mapa de posición → rPr ──────────────────────────────────────
    # Para cada posición del texto completo, guardamos el rPr del run original.
    # Esto nos permite saber qué formato aplicar a cada carácter.
    pos_rpr = []
    for run in runs:
        rpr = _get_rpr(run)
        for _ in _run_text(run):
            pos_rpr.append(rpr)

    # ── Construir lista de segmentos (texto, rpr) ─────────────────────────────
    # Dividimos el texto completo en segmentos respetando los marcadores.
    # Cada segmento tendrá el rPr correspondiente a su posición original.
    segmentos = []  # lista de (texto_final, rpr)

    cursor = 0
    for match in patron.finditer(texto_completo):
        inicio, fin = match.start(), match.end()

        # Texto antes del marcador — preservar rPr carácter a carácter
        if cursor < inicio:
            _agregar_segmentos_con_formato(segmentos, texto_completo[cursor:inicio], pos_rpr[cursor:inicio])

        # Valor del marcador — hereda el rPr del «
        clave = match.group(1)
        valor = str(variables.get(clave, f"«{clave}»"))
        rpr_marcador = pos_rpr[inicio] if inicio < len(pos_rpr) else None
        if valor:
            segmentos.append((valor, rpr_marcador))

        cursor = fin

    # Texto después del último marcador
    if cursor < len(texto_completo):
        _agregar_segmentos_con_formato(segmentos, texto_completo[cursor:], pos_rpr[cursor:])

    # ── Eliminar runs originales del párrafo ──────────────────────────────────
    for r in parrafo.findall(f"{{{W}}}r"):
        parrafo.remove(r)
    for hlink in parrafo.findall(f".//{{{W}}}hyperlink"):
        for r in hlink.findall(f"{{{W}}}r"):
            hlink.remove(r)

    # ── Insertar nuevos runs después de pPr ───────────────────────────────────
    pPr = parrafo.find(f"{{{W}}}pPr")
    insert_pos = (list(parrafo).index(pPr) + 1) if pPr is not None else 0

    for i, (texto, rpr) in enumerate(segmentos):
        if texto:
            parrafo.insert(insert_pos + i, _make_run(texto, rpr))


def _agregar_segmentos_con_formato(segmentos: list, texto: str, pos_rpr: list):
    """
    Agrupa caracteres consecutivos con el mismo rPr en un solo segmento.
    Así no creamos un run por cada carácter, sino uno por cada bloque de formato igual.
    """
    if not texto:
        return

    rpr_actual = pos_rpr[0] if pos_rpr else None
    buf = ""

    for i, char in enumerate(texto):
        rpr_char = pos_rpr[i] if i < len(pos_rpr) else None
        # Comparamos el XML serializado para detectar cambio de formato
        if _rpr_igual(rpr_char, rpr_actual):
            buf += char
        else:
            if buf:
                segmentos.append((buf, rpr_actual))
            buf = char
            rpr_actual = rpr_char

    if buf:
        segmentos.append((buf, rpr_actual))


def _rpr_igual(a, b) -> bool:
    """Compara dos rPr por su XML serializado."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return etree.tostring(a) == etree.tostring(b)


def _reemplazar_xml(xml_bytes: bytes, variables: dict) -> bytes:
    root = etree.fromstring(xml_bytes)
    for parrafo in root.iter(f"{{{W}}}p"):
        try:
            _reemplazar_parrafo(parrafo, variables)
        except Exception:
            pass
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _sanitizar(texto: str) -> str:
    """Elimina caracteres inválidos para nombres de archivo."""
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()


def generar_minuta(contrato, lote, template, distrito1=None, distrito2=None) -> Path:
    template_path = TEMPLATES_DIR / template.ruta
    if not template_path.exists():
        raise FileNotFoundError(f"Template no encontrado: {template_path}")

    variables = compilar_variables(contrato, lote, distrito1, distrito2)

    fecha = contrato.fecha

    # Nombre: MZA-LT3_Proyecto_2026-03-13.docx
    manzana       = _sanitizar(lote.manzana)
    lote_num      = _sanitizar(lote.numero)
    proyecto_nom  = _sanitizar(contrato.proyecto.nombre) if contrato.proyecto else "Proyecto"
    nombre_arch   = f"{manzana}-{lote_num}, {proyecto_nom}.docx"

    carpeta_salida = OUTPUT_DIR / str(fecha.year) / f"{fecha.month:02d}"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta_salida / nombre_arch

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

    # ── Subir a Drive (no bloquea si falla) ───────────────────────────────────
    try:
        from app.services.drive_service import subir_a_drive
        proyecto_nombre = contrato.proyecto.nombre if contrato.proyecto else "Proyecto"
        subir_a_drive(ruta_salida, proyecto_nombre, fecha)
    except Exception as e:
        # El archivo local igual se retorna aunque Drive falle
        import logging
        logging.getLogger(__name__).warning(f"Drive upload falló: {e}")

    return ruta_salida
