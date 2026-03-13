"""
calculos.py
Toda la lógica de negocio migrada desde la hoja DATOS del Excel.
Equivalente a las ~60 fórmulas y al Módulo2 (NumeroALetras) de VBA.
"""

from datetime import date
from dateutil.relativedelta import relativedelta
import locale

# ─── NÚMERO A LETRAS ─────────────────────────────────────────────────────────
# Migrado exactamente desde Módulo2 del VBA

UNIDADES = ["", "uno", "dos", "tres", "cuatro", "cinco",
            "seis", "siete", "ocho", "nueve", "diez",
            "once", "doce", "trece", "catorce", "quince",
            "dieciséis", "diecisiete", "dieciocho", "diecinueve"]

DECENAS  = ["", "diez", "veinte", "treinta", "cuarenta",
            "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]

CENTENAS = ["", "cien", "doscientos", "trescientos", "cuatrocientos",
            "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"]


def _convertir_entero(n: int) -> str:
    """Convierte un entero (0-999999) a letras en español."""
    if n == 0:
        return "cero"
    if n < 0:
        return "menos " + _convertir_entero(-n)

    resultado = ""

    if n >= 1_000_000:
        raise ValueError("Número demasiado grande (máx. 999 999)")

    if n >= 1000:
        miles = n // 1000
        if miles == 1:
            resultado += "mil "
        else:
            resultado += _convertir_entero(miles) + " mil "
        n %= 1000

    if n >= 100:
        c = n // 100
        if n == 100:
            resultado += "cien "
        else:
            resultado += CENTENAS[c] + " "
        n %= 100

    if n >= 20:
        d = n // 10
        u = n % 10
        if u == 0:
            resultado += DECENAS[d] + " "
        else:
            resultado += DECENAS[d] + " y " + UNIDADES[u] + " "
    elif n > 0:
        resultado += UNIDADES[n] + " "

    return resultado.strip()


def numero_a_letras(monto: float) -> str:
    """
    Convierte un monto a letras en español peruano.
    Ej: 1500.50 → 'MIL QUINIENTOS CON 50/100 SOLES'
    """
    monto = round(monto, 2)
    entero  = int(monto)
    decimal = round((monto - entero) * 100)

    parte_entera  = _convertir_entero(entero).upper()
    parte_decimal = f"{decimal:02d}/100"

    return f"{parte_entera} Y {parte_decimal} SOLES"


def area_a_letras(area: float) -> str:
    """
    Convierte un área a letras con decimales en palabras.
    Ej: 256.85 → 'DOSCIENTOS CINCUENTA Y SEIS PUNTO OCHO CINCO'
    Ej: 200.00 → 'DOSCIENTOS'
    """
    area = round(area, 2)
    entero  = int(area)
    decimal = round((area - entero) * 100)

    resultado = _convertir_entero(entero).upper()

    if decimal > 0:
        dec_str = f"{decimal:02d}"
        digitos = [_convertir_entero(int(d)).upper() for d in dec_str]
        resultado += " PUNTO " + " ".join(digitos)

    return resultado


# ─── FECHAS EN ESPAÑOL ────────────────────────────────────────────────────────

MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}


def fecha_a_texto(d: date) -> str:
    """
    Equivalente a =UPPER(TEXT(fecha,"[$-es-PE]dd \\d\\e mmmm \\del yyyy"))
    Ej: date(2025,5,7) → '07 DE MAYO DEL 2025'
    """
    dia = f"{d.day:02d}"
    mes = MESES_ES[d.month].upper()
    return f"{dia} DE {mes} DEL {d.year}"


def dia_formateado(d: date) -> str:
    """Día con cero si < 10. Ej: 7 → '07'"""
    return f"{d.day:02d}"


# ─── ESTADO CIVIL Y GÉNERO ───────────────────────────────────────────────────

def estado_civil_texto(estado_civil: str, genero: str) -> str:
    """
    Equivalente a la fórmula «_ESTADO_CIVIL» del Excel.
    estado_civil: S / C / D / V
    genero: M / F
    """
    base = {
        "S": "SOLTER",
        "C": "CASAD",
        "D": "DIVORCIAD",
        "V": "VIUD",
    }.get(estado_civil.upper(), "")

    sufijo = "O" if genero.upper() == "M" else "A"
    return base + sufijo


def identificado_texto(genero: str) -> str:
    """«_IDENT»: IDENTIFICADO / IDENTIFICADA"""
    return "IDENTIFICADA" if genero.upper() == "F" else "IDENTIFICADO"


def promitente_texto(genero: str) -> str:
    """«_PROMT»"""
    if genero.upper() == "F":
        return "LA PROMITENTE COMPRADORA"
    return "EL PROMITENTE COMPRADOR"


# ─── CÁLCULOS ECONÓMICOS ─────────────────────────────────────────────────────

def formatear_monto(monto: float) -> str:
    """Formato #,##0.00 como en Excel. Ej: 1500.5 → '1,500.50'"""
    return f"{monto:,.2f}"


def parte_entera(monto: float) -> int:
    return int(monto)


def parte_decimal(monto: float) -> str:
    """Retorna los centavos como string de 2 dígitos. Ej: 1500.5 → '50'"""
    dec = round((monto - int(monto)) * 100)
    return f"{dec:02d}"


# ─── PLAZOS ──────────────────────────────────────────────────────────────────

def calcular_plazo_meses(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Equivalente a «_PLAZO»: (YEAR(fin)-YEAR(ini))*12 + MONTH(fin)-MONTH(ini)+1
    """
    return (fecha_fin.year - fecha_inicio.year) * 12 + (fecha_fin.month - fecha_inicio.month) + 1


def plazo_a_texto(meses: int) -> str:
    """Convierte número de meses a texto. Ej: 12 → 'DOCE (12) MESES'"""
    return f"{_convertir_entero(meses).upper()} ({meses}) MESES"


# ─── PORCENTAJE ──────────────────────────────────────────────────────────────

def calcular_porcentaje(area_m2: float, area_total_has: float) -> float:
    """
    «%» = area_m2 / (area_total_has * 10000)
    """
    if area_total_has == 0:
        return 0.0
    return round(area_m2 / (area_total_has * 10_000), 6)


def porcentaje_texto(pct: float) -> str:
    """Formato 0.0000%. Ej: 0.001234 → '0.1234'"""
    return f"{pct * 100:.4f}"



# ─── MAPA PARTIDA → DESCRIPCIÓN DEL PREDIO MATRIZ ───────────────────────────

PREDIO_POR_PARTIDA = {
    "04020673": "PREDIO MOCAN LA ARENITA, VALLE CHICAMA, CON U.C. N° 1866",
    "11578607": "PREDIO MOCAN Y ANEXOS, PARCELA N° 1891",
    "04019384": "PREDIO RURAL VALLE CHICAMA FUNDO MOCAN, SECTOR LA ARENITA CON U.C. 1853",
    "04019387": "PREDIO RURAL VALLE CHICAMA FUNDO MOCAN, SECTOR LA ARENITA CON U.C. 1854",
    "04019390": "PREDIO MOCAN SECTOR LA ARENITA, PARCELA 1855, CON U.C. 1855",
    "04019385": "PREDIO FUNDO MOCAN-SECTOR LA ARENITA PARCELA 1856, CON U.C. 1856",
    "04017223": "PREDIO FUNDO MOCAN-SECTOR LA ARENITA, CON U.C. 1857",
    "04017224": "PREDIO FUNDO MOCAN-SECTOR LA ARENITA PARCELA, CON U.C. 1858",
    "11578604": "PREDIO MOCAN Y ANEXOS, PARCELA N° 1859",
    "04020058": "FUNDO MOCAN LA ARENITA, VALLE CHICAMA, CON U.C. 1865",
}


def descripcion_predio(partida: str) -> str:
    """Retorna la descripción del predio matriz según la partida del lote."""
    return PREDIO_POR_PARTIDA.get(str(partida or ""), f"PARTIDA N° {partida}")


# ─── COMPILADOR DE VARIABLES ─────────────────────────────────────────────────

def compilar_variables(contrato, lote, distrito1=None, distrito2=None) -> dict:
    """
    Genera el diccionario completo de variables para reemplazar en el template Word.
    Equivalente a toda la hoja DATOS del Excel.

    Retorna un dict con claves = marcadores del Word (sin «»), valores = texto final.
    """
    fecha         = contrato.fecha
    f_pago_total  = contrato.f_pago_total
    precio        = contrato.precio
    separacion    = contrato.separacion or 0.0
    pago          = contrato.pago or 0.0
    saldo         = round(precio - separacion - pago, 2)
    area_m2       = lote.area
    area_total    = lote.has or 1.0
    pct           = calcular_porcentaje(area_m2, area_total)
    plazo_meses   = calcular_plazo_meses(fecha, f_pago_total) if f_pago_total else 0

    # Ubicación del titular
    dist1_txt  = ""
    prov1_txt  = ""
    reg1_txt   = ""
    if distrito1:
        dist1_txt = f", DISTRITO DE {distrito1.distrito.upper()}"
        prov1_txt = f", PROVINCIA DE {distrito1.provincia.upper()}"
        reg1_txt  = f", DEPARTAMENTO DE {distrito1.region.upper()}"

    dist2_txt = prov2_txt = reg2_txt = ""
    if distrito2:
        dist2_txt = f", DISTRITO DE {distrito2.distrito.upper()}"
        prov2_txt = f", PROVINCIA DE {distrito2.provincia.upper()}"
        reg2_txt  = f", DEPARTAMENTO DE {distrito2.region.upper()}"

    vars_dict = {
        # Número y estado
        "No":                  str(contrato.numero),
        "FECHA":               str(fecha),
        "FECHA_TEXTO":         fecha_a_texto(fecha),
        "_DIA":                dia_formateado(fecha),

        # Lote
        "MZ":                  lote.manzana,
        "LOTE":                str(lote.numero),
        "PR":                  str(lote.uc or ""),
        "_PR":                 f"{lote.uc or 0:08d}",
        "ATOTAL":              str(area_total),
        "_ATOTAL":             str(area_total),
        "_ATOTAL_TEXTO":       numero_a_letras(area_total),
        "AREA (m2)":           str(area_m2),
        "_AREA":               f"{area_m2:.2f}",
        "_AREA_TEXTO":         area_a_letras(area_m2),
        "%":                   str(pct),
        "_PORCENTAJE":         porcentaje_texto(pct),
        "_PORCENT_TEXTO":      f"{porcentaje_texto(pct)} POR CIENTO",

        # Precio
        "PRECIO":              str(precio),
        "_PRECIO":             formatear_monto(precio),
        "_PRECIO_ENTERO":      str(parte_entera(precio)),
        "_PRECIO_TEXTO":       numero_a_letras(precio),
        "_PRECIO_DECIMAL":     parte_decimal(precio),

        # Separación
        "SEPARACION":          str(separacion),
        "_SEPARACION":         formatear_monto(separacion),
        "_SEPARACION_ENTERO":  str(parte_entera(separacion)),
        "_SEPARACION_TEXTO":   numero_a_letras(separacion),
        "_SEPARACION_DECIMAL": parte_decimal(separacion),

        # Pago
        "PAGO":                str(pago),
        "_PAGO":               formatear_monto(pago),
        "_PAGO_ENTERO":        str(parte_entera(pago)),
        "_PAGO_TEXTO":         numero_a_letras(pago),
        "_PAGO_DECIMAL":       parte_decimal(pago),

        # Saldo
        "SALDO":               str(saldo),
        "_SALDO":              formatear_monto(saldo),
        "_SALDO_ENTERO":       str(parte_entera(saldo)),
        "_SALDO_TEXTO":        numero_a_letras(saldo),
        "_SALDO_DECIMAL":      parte_decimal(saldo),

        # Titular
        "TITULAR":             contrato.titular.upper() if contrato.titular else "",
        "OCUPACION1":          (contrato.ocupacion1 or "").upper(),
        "GENERO1":             contrato.genero1 or "",
        "ESTADO CIVIL1":       contrato.estado_civil1 or "",
        "_ESTADO_CIVIL":       estado_civil_texto(
                                   contrato.estado_civil1 or "S",
                                   contrato.genero1 or "M"
                               ),
        "_IDENT":              identificado_texto(contrato.genero1 or "M"),
        "_PROMT":              promitente_texto(contrato.genero1 or "M"),
        "DNI":                 contrato.dni or "",
        "_DNI":                f"{int(contrato.dni or 0):08d}" if contrato.dni and contrato.dni.isdigit() else (contrato.dni or ""),
        "DIRECCION1":          (contrato.direccion1 or "").upper(),
        "DISTRITO1":           dist1_txt,
        "PROVINCIA1":          prov1_txt,
        "DEPARTAMENTO1":       reg1_txt,

        # Copropietario
        "COPROPIETARIO":       (contrato.copropietario or "").upper(),
        "OCUPACION2":          (contrato.ocupacion2 or "").upper(),
        "GENERO2":             contrato.genero2 or "",
        "ESTADO CIVIL2":       contrato.estado_civil2 or "",
        "_ESTADO_CIVIL_2":     estado_civil_texto(
                                   contrato.estado_civil2 or "S",
                                   contrato.genero2 or "M"
                               ) if contrato.copropietario else "",
        "_IDENT_2":            identificado_texto(contrato.genero2 or "M") if contrato.copropietario else "",
        "DNI2":                contrato.dni2 or "",
        "_DNI2":               f"{int(contrato.dni2 or 0):08d}" if contrato.dni2 and contrato.dni2.isdigit() else (contrato.dni2 or ""),
        "DIRECCION2":          (contrato.direccion2 or "").upper(),
        "DISTRITO2":           dist2_txt,
        "PROVINCIA2":          prov2_txt,
        "DEPARTAMENTO2":       reg2_txt,

        # Fechas de pago
        "FPAGOTOTAL":          str(f_pago_total) if f_pago_total else "",
        "FPAGOTOTAL_TEXTO":    fecha_a_texto(f_pago_total) if f_pago_total else "",
        "_PLAZO":              str(plazo_meses),
        "PLAZOEP":             str(plazo_meses),
        "PLAZOEP_TEXTO":       plazo_a_texto(plazo_meses) if plazo_meses else "",

        # Datos del lote (DATOSLOTE: "MZ-LT, área has, partida, UC")
        "DATOSLOTE":           descripcion_predio(lote.partida),
    }

    return vars_dict