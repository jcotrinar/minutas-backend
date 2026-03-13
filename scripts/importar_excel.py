"""
importar_excel.py
Migra los datos del MINUTAS.xlsm original a la base de datos del nuevo sistema.
Ejecutar UNA sola vez: python scripts/importar_excel.py --excel MINUTAS.xlsm
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import openpyxl
from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)


# ─── HELPERS ROBUSTOS ────────────────────────────────────────────────────────

def _safe_float(val):
    """Convierte a float ignorando #N/A, #REF!, #VALUE! y otros errores de Excel."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.startswith("#"):
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _safe_int(val):
    f = _safe_float(val)
    return int(f) if f is not None else None


def _safe_str(val):
    if val is None:
        return None
    if hasattr(val, 'text'):   # ArrayFormula de openpyxl
        val = val.text
    s = str(val).strip()
    if not s or s.startswith("#"):
        return None
    return s


def _safe_date(val):
    if val is None:
        return None
    if hasattr(val, 'date'):
        return val.date()
    return None


def _safe_dni(val):
    """DNI puede venir como 45123456.0 (float) o '45123456' (string)."""
    f = _safe_float(val)
    if f is not None:
        return str(int(f))
    return _safe_str(val)


# ─── IMPORTADORES ────────────────────────────────────────────────────────────

def importar_distritos(ws_distritos, db):
    print("Importando distritos...")
    count = 0
    for row in ws_distritos.iter_rows(min_row=2, values_only=True):
        region, provincia, distrito = row[0], row[1], row[2]
        if not region:
            continue
        db.add(models.Distrito(
            region    = str(region).strip(),
            provincia = str(provincia).strip(),
            distrito  = str(distrito).strip(),
        ))
        count += 1
    db.commit()
    print(f"  → {count} distritos importados")


def importar_lotes(ws_lotes, db):
    print("Importando lotes...")
    count = 0
    errores = 0
    for fila, row in enumerate(ws_lotes.iter_rows(min_row=2, max_col=7, values_only=True), start=2):
        mz = _safe_str(row[0])
        if not mz:
            continue
        try:
            db.add(models.Lote(
                manzana = mz,
                numero  = _safe_int(row[1]) or 0,
                area    = _safe_float(row[2]) or 0.0,
                uc      = _safe_int(row[3]),
                partida = _safe_str(row[4]),
                has     = _safe_float(row[5]),   # #N/A → None, sin problema
                mz_lt   = _safe_str(row[6]),
            ))
            count += 1
        except Exception as e:
            print(f"  ⚠ Lote fila {fila}: {e} — {row}")
            errores += 1

    db.commit()
    print(f"  → {count} lotes importados ({errores} errores)")


def importar_contratos(ws_hoja1, db):
    print("Importando contratos desde Hoja1...")
    count = 0
    errores = 0

    # Estructura Hoja1 (fila 5 = cabecera, datos desde fila 6):
    # Col A(0)=vacío  B(1)=FECHA  C(2)=MZ  D(3)=LOTE  E(4)=PR  F(5)=ATOTAL
    # G(6)=PRECIO     H(7)=AREA   I(8)=%   J(9)=TITULAR
    # K(10)=OCUP1  L(11)=GEN1  M(12)=EC1  N(13)=DNI  O(14)=DIR1
    # P(15)=COPROP Q(16)=OCUP2 R(17)=GEN2 S(18)=EC2  T(19)=DNI2 U(20)=DIR2
    # V(21)=SEPARACION  W(22)=PAGO  X(23)=SALDO  Y(24)=FSEPARACION

    for fila, row in enumerate(ws_hoja1.iter_rows(min_row=6, values_only=True), start=6):
        fecha    = _safe_date(row[1])
        mz       = _safe_str(row[2])
        lote_num = _safe_int(row[3])

        if not fecha or not mz or not lote_num:
            continue

        try:
            lote = db.query(models.Lote).filter(
                models.Lote.manzana == mz,
                models.Lote.numero  == lote_num
            ).first()

            if not lote:
                print(f"  ⚠ Fila {fila}: lote {mz}-{lote_num} no encontrado")
                errores += 1
                continue

            db.add(models.Contrato(
                numero        = count + 1,
                lote_id       = lote.id,
                precio        = _safe_float(row[6]) or 0.0,
                separacion    = _safe_float(row[21]) or 0.0,
                pago          = _safe_float(row[22]) or 0.0,
                fecha         = fecha,
                f_separacion  = _safe_date(row[24]),
                titular       = _safe_str(row[9]) or "",
                ocupacion1    = _safe_str(row[10]),
                genero1       = _safe_str(row[11]),
                estado_civil1 = _safe_str(row[12]),
                dni           = _safe_dni(row[13]),
                direccion1    = _safe_str(row[14]),
                copropietario = _safe_str(row[15]),
                ocupacion2    = _safe_str(row[16]),
                genero2       = _safe_str(row[17]),
                estado_civil2 = _safe_str(row[18]),
                dni2          = _safe_dni(row[19]),
                direccion2    = _safe_str(row[20]),
            ))
            count += 1

        except Exception as e:
            print(f"  ✗ Error en fila {fila}: {e}")
            errores += 1

    db.commit()
    print(f"  → {count} contratos importados ({errores} errores)")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Importar MINUTAS.xlsm a la BD")
    parser.add_argument("--excel", required=True, help="Ruta al archivo MINUTAS.xlsm")
    parser.add_argument("--solo-lotes", action="store_true", help="Reimportar solo lotes (si ya tienes distritos)")
    args = parser.parse_args()

    ruta = Path(args.excel)
    if not ruta.exists():
        print(f"Archivo no encontrado: {ruta}")
        sys.exit(1)

    print(f"Abriendo {ruta.name}...")
    wb = openpyxl.load_workbook(str(ruta), keep_vba=True, data_only=True)

    db = SessionLocal()
    try:
        if not args.solo_lotes:
            importar_distritos(wb["DISTRITOS"], db)

        importar_lotes(wb["LOTES"], db)
        importar_contratos(wb["Hoja1"], db)
        print("\n✓ Importación completa")
    finally:
        db.close()


if __name__ == "__main__":
    main()