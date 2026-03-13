# Minutas Backend 🏗️

Backend para el sistema de generación de minutas de compraventa de lotes.
Migración del sistema Excel/VBA a una API REST accesible desde Android.

## Stack
- **FastAPI** — API REST
- **SQLAlchemy** — ORM
- **python-docx** — Generación de minutas Word
- **Supabase / PostgreSQL** — Base de datos en la nube
- **Google Drive API** — Almacenamiento de minutas

---

## 1. Instalación local

```bash
git clone <tu-repo>
cd minutas-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus valores
```

## 2. Copiar los templates Word

Copia tus 4 archivos originales a la carpeta `app/templates/`:
```
app/templates/
├── VERDE.docx
├── AMARILLO.docx
├── AZUL.docx
└── ROJO.docx
```

Los marcadores en los Word deben mantener el formato `«NOMBRE_VARIABLE»`.

## 3. Iniciar en desarrollo

```bash
# Crear tablas en SQLite local
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(engine)"

# Iniciar el servidor
uvicorn app.main:app --reload

# API disponible en: http://localhost:8000
# Documentación:    http://localhost:8000/docs
```

## 4. Importar datos del Excel original

```bash
python scripts/importar_excel.py --excel ruta/MINUTAS.xlsm
```

Esto migra:
- Todos los lotes (hoja LOTES)
- Todos los distritos del Perú (hoja DISTRITOS)  
- Todos los contratos existentes (hoja Hoja1)

## 5. Configurar Google Drive

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto → Habilita "Google Drive API"
3. Crea una **Service Account** → descarga el JSON de credenciales
4. Guarda el JSON como `credentials.json` en la raíz del proyecto
5. En Google Drive, crea una carpeta "MINUTAS" y compártela con el email de la Service Account
6. Copia el ID de la carpeta (de la URL) al `.env` → `DRIVE_FOLDER_ID`

## 6. Deploy en Railway (gratuito)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login y deploy
railway login
railway init
railway up

# Configurar variables de entorno en el dashboard de Railway:
# DATABASE_URL, DRIVE_FOLDER_ID, GOOGLE_CREDENTIALS_PATH
```

O en **Render**: conecta tu repositorio GitHub y configura las mismas variables.

---

## Endpoints principales

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/contratos/` | Lista todos los contratos |
| GET | `/contratos/?estado=VERDE` | Filtrar por semáforo |
| GET | `/contratos/?busqueda=Juan` | Buscar por titular |
| POST | `/contratos/` | Crear contrato |
| PUT | `/contratos/{id}` | Actualizar contrato |
| GET | `/minutas/descargar/{id}` | Generar y descargar .docx |
| POST | `/minutas/generar` | Generar + subir a Drive |
| GET | `/lotes/` | Lista de lotes |
| GET | `/lotes/manzanas` | Lista de manzanas (para ComboBox) |
| GET | `/distritos/regiones` | Regiones del Perú |
| GET | `/distritos/provincias/{region}` | Provincias de una región |
| GET | `/distritos/distritos/{region}/{provincia}` | Distritos en cascada |

---

## Variables calculadas automáticamente

El backend calcula las mismas ~60 variables que calculaba la hoja DATOS del Excel:

- **Saldo**: `precio - separacion - pago`
- **Estado (semáforo)**: VERDE / AMARILLO / AZUL / ROJO
- **Montos a letras**: `numero_a_letras(1500.50)` → `"MIL QUINIENTOS CON 50/100 SOLES"`
- **Fechas en español**: `fecha_a_texto(date(2025,5,7))` → `"07 DE MAYO DEL 2025"`
- **Estado civil concordado**: `"CASADA"`, `"SOLTERO"`, etc.
- **Porcentaje del lote**: `area_m2 / (has_totales * 10000)`
- **Plazo en meses y texto**: `"DOCE (12) MESES"`

---

## Estructura del proyecto

```
minutas-backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── database.py          # Conexión BD
│   ├── models.py            # Tablas SQLAlchemy
│   ├── schemas.py           # Validación Pydantic
│   ├── routers/
│   │   ├── contratos.py     # CRUD contratos
│   │   ├── minutas.py       # Generación Word
│   │   ├── lotes.py         # Catálogo lotes
│   │   └── distritos.py     # Distritos Perú (cascada)
│   ├── services/
│   │   ├── calculos.py      # Lógica migrada del Excel (NumeroALetras, fechas, etc.)
│   │   ├── generador_minutas.py  # Motor python-docx
│   │   └── drive_service.py      # Upload a Google Drive
│   └── templates/           # VERDE.docx, AZUL.docx, etc.
├── scripts/
│   └── importar_excel.py    # Migración del .xlsm original
├── minutas_generadas/       # Output local (gitignored)
├── requirements.txt
├── Dockerfile
└── .env.example
```
