"""
calculos.py — Lógica de negocio simplificada.
Marcadores estandarizados para todos los proyectos.
"""
from datetime import date

# ─── NÚMERO A LETRAS ──────────────────────────────────────────────────────────

_UNIDADES = [
    "", "uno", "dos", "tres", "cuatro", "cinco",
    "seis", "siete", "ocho", "nueve", "diez",
    "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve",
    "veinte",
]

_VEINTI = [
    "", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
    "veintiséis", "veintisiete", "veintiocho", "veintinueve",
]

_DECENAS = [
    "", "diez", "veinte", "treinta", "cuarenta",
    "cincuenta", "sesenta", "setenta", "ochenta", "noventa",
]

_CENTENAS = [
    "", "ciento", "doscientos", "trescientos", "cuatrocientos",
    "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos",
]


def _entero_a_letras(n: int) -> str:
    if n == 0:
        return "cero"
    if n < 0:
        return "menos " + _entero_a_letras(-n)
    if n >= 1_000_000:
        raise ValueError("Número demasiado grande")

    partes = []

    # Millares
    if n >= 1000:
        miles = n // 1000
        if miles == 1:
            partes.append("mil")
        else:
            txt_miles = _entero_a_letras(miles)
            # veintiuno → veintiún, uno → un (apócope antes de "mil")
            txt_miles = txt_miles.replace("veintiuno", "veintiún").replace("uno", "un") if txt_miles.endswith("uno") else txt_miles
            partes.append(txt_miles + " mil")
        n %= 1000

    # Centenas
    if n >= 100:
        c = n // 100
        resto = n % 100
        if n == 100:
            partes.append("cien")          # exactamente 100
            n = 0
        else:
            partes.append(_CENTENAS[c])    # ciento, doscientos, etc.
            n = resto
    
    # Decenas y unidades
    if n > 0:
        if n <= 20:
            partes.append(_UNIDADES[n])
        elif n < 30:
            partes.append(_VEINTI[n - 20]) # veintiuno … veintinueve
        else:
            d, u = n // 10, n % 10
            if u == 0:
                partes.append(_DECENAS[d])
            else:
                partes.append(_DECENAS[d] + " y " + _UNIDADES[u])

    return " ".join(partes)


def numero_a_letras(monto: float, moneda: str = "SOLES") -> str:
    monto   = round(monto, 2)
    entero  = int(monto)
    decimal = round((monto - entero) * 100)
    sufijo  = "DÓLARES AMERICANOS" if moneda == "DOLARES" else "SOLES"
    return f"{_entero_a_letras(entero).upper()} Y {decimal:02d}/100 {sufijo}"

def area_a_letras(area: float) -> str:
    area    = round(area, 2)
    entero  = int(area)
    decimal = round((area - entero) * 100)
    r = _entero_a_letras(entero).upper()
    if decimal > 0:
        digitos = [_entero_a_letras(int(d)).upper() for d in f"{decimal:02d}"]
        r += " PUNTO " + " ".join(digitos)
    return r

def decimal_str(monto: float) -> str:
    return f"{round((monto - int(monto)) * 100):02d}"

def fmt(monto: float) -> str:
    return f"{monto:,.2f}"

MESES = {
    1:"ENERO", 2:"FEBRERO", 3:"MARZO", 4:"ABRIL",
    5:"MAYO", 6:"JUNIO", 7:"JULIO", 8:"AGOSTO",
    9:"SEPTIEMBRE", 10:"OCTUBRE", 11:"NOVIEMBRE", 12:"DICIEMBRE"
}

def fecha_a_texto(d: date) -> str:
    return f"{d.day:02d} DE {MESES[d.month]} DEL {d.year}"

def plazo_a_texto(meses: int) -> str:
    return f"{_entero_a_letras(meses).upper()} ({meses}) MESES"


def plazo_entrega_texto(fecha_contrato, fecha_limite_entrega) -> tuple:
    from dateutil.relativedelta import relativedelta
    if not fecha_limite_entrega:
        return (0, "")
    diff  = relativedelta(fecha_limite_entrega, fecha_contrato)
    meses = diff.years * 12 + diff.months
    if meses < 0:
        meses = 0
    return (meses, _entero_a_letras(meses).upper())

def estado_civil_texto(ec: str, genero: str) -> str:
    base = {"S": "SOLTER", "C": "CASAD", "D": "DIVORCIAD", "V": "VIUD"}.get(ec.upper(), "")
    return base + ("A" if genero.upper() == "F" else "O")

def identificado_texto(genero: str) -> str:
    return "IDENTIFICADA" if genero.upper() == "F" else "IDENTIFICADO"

def comprador_texto(genero: str, tiene_coprop: bool = False) -> str:
    if tiene_coprop:
        return "LOS COMPRADORES"
    return "LA PROMITENTE COMPRADORA" if genero.upper() == "F" else "EL PROMITENTE COMPRADOR"

def compilar_variables(contrato, lote, distrito1=None, distrito2=None) -> dict:
    moneda      = contrato.moneda
    precio      = contrato.precio      or 0.0
    separacion  = contrato.separacion  or 0.0
    sep_soles   = contrato.sep_en_soles or 0.0
    tipo_cambio = contrato.tipo_cambio  or 0.0
    pago        = contrato.pago        or 0.0
    saldo       = contrato.saldo
    tiene_coprop = bool(contrato.copropietario)

    ubigeo1 = ""
    if distrito1:
        ubigeo1 = (f"DISTRITO DE {distrito1.distrito.upper()}, "
                   f"PROVINCIA DE {distrito1.provincia.upper()}, "
                   f"DEPARTAMENTO DE {distrito1.region.upper()}")
    ubigeo2 = ""
    if distrito2:
        ubigeo2 = (f"DISTRITO DE {distrito2.distrito.upper()}, "
                   f"PROVINCIA DE {distrito2.provincia.upper()}, "
                   f"DEPARTAMENTO DE {distrito2.region.upper()}")

    fecha_pago = fecha_a_texto(contrato.f_pago_total) if contrato.f_pago_total else ""
    plazo_num  = contrato.plazo_meses or 0
    plazo_txt  = plazo_a_texto(plazo_num) if plazo_num else ""

    # Plazo de entrega dinámico
    fecha_limite = getattr(contrato.proyecto, 'fecha_limite_entrega', None) if hasattr(contrato, 'proyecto') and contrato.proyecto else None
    entrega_num, entrega_txt_calc = plazo_entrega_texto(contrato.fecha, fecha_limite)

    # Entrega configurable por proyecto (tiene prioridad sobre el cálculo dinámico)
    entrega_texto_proyecto = getattr(contrato.proyecto, 'entrega_texto', None) if contrato.proyecto else None

    return {
        "FECHA":             fecha_a_texto(contrato.fecha),
        "MZ":                lote.manzana,
        "LOTE":              str(lote.numero),
        "AREA":              f"{lote.area:.2f}",
        "AREA_TEXTO":        area_a_letras(lote.area),
        "NOMBRE_PREDIO":     lote.nombre_predio or f"PARTIDA N° {lote.partida or ''}",
        "PARTIDA":           lote.partida or "",
        "TITULAR":           (contrato.titular or "").upper(),
        "DNI":               contrato.dni or "",
        "IDENT":             identificado_texto(contrato.genero1 or "M"),
        "ESTADO_CIVIL":      estado_civil_texto(contrato.estado_civil1 or "S", contrato.genero1 or "M"),
        "OCUPACION":         (contrato.ocupacion1 or "").upper(),
        "DIRECCION":         (contrato.direccion1 or "").upper(),
        "UBIGEO":            ubigeo1,
        "COPROP":            (contrato.copropietario or "").upper(),
        "DNI2":              contrato.dni2 or "",
        "IDENT2":            identificado_texto(contrato.genero2 or "M") if tiene_coprop else "",
        "ESTADO_CIVIL2":     estado_civil_texto(contrato.estado_civil2 or "S", contrato.genero2 or "M") if tiene_coprop else "",
        "OCUPACION2":        (contrato.ocupacion2 or "").upper(),
        "DIRECCION2":        (contrato.direccion2 or "").upper(),
        "UBIGEO2":           ubigeo2,
        "COMPRADOR":         comprador_texto(contrato.genero1 or "M", tiene_coprop),
        "PRECIO":            fmt(precio),
        "PRECIO_TEXTO":      numero_a_letras(precio, moneda),
        "PRECIO_DECIMAL":    decimal_str(precio),
        "SEP":               fmt(separacion),
        "SEP_TEXTO":         numero_a_letras(separacion, moneda),
        "SEP_DECIMAL":       decimal_str(separacion),
        "SEP_SOLES":         fmt(sep_soles) if sep_soles else "",
        "SEP_SOLES_TEXTO":   numero_a_letras(sep_soles, "SOLES") if sep_soles else "",
        "SEP_SOLES_DECIMAL": decimal_str(sep_soles) if sep_soles else "",
        "TIPO_CAMBIO":       fmt(tipo_cambio) if tipo_cambio else "",
        "TC_TEXTO":          numero_a_letras(tipo_cambio, "SOLES") if tipo_cambio else "",
        "TC_DECIMAL":        decimal_str(tipo_cambio) if tipo_cambio else "",
        "PAGO":              fmt(pago),
        "PAGO_TEXTO":        numero_a_letras(pago, moneda),
        "PAGO_DECIMAL":      decimal_str(pago),
        "SALDO":             fmt(saldo),
        "SALDO_TEXTO":       numero_a_letras(saldo, moneda),
        "SALDO_DECIMAL":     decimal_str(saldo),
        "FECHA_PAGO":        fecha_pago,
        "ENTREGA":           str(entrega_num) if entrega_num else "",
        "ENTREGA_TEXTO":     entrega_texto_proyecto or entrega_txt_calc,
        "PLAZO":             str(plazo_num) if plazo_num else "",
        "PLAZO_TEXTO":       plazo_txt,
    }


def entrega_a_texto(meses: int) -> str:
    return f"{_entero_a_letras(meses).upper()} ({meses}) MESES"