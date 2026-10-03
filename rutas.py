from pathlib import Path

RAIZ = Path(__file__).resolve().parent  # la carpeta donde está este archivo (esta ruta)
#ORIGEN = RAIZ / "origen"                # la carpeta donde están los Excel de origen  
ORIGEN = RAIZ / "data/bases_cierres"                # la carpeta donde están los Excel de origen  
BRONZE = RAIZ / "bronze"                # crudo, sin interpretar nada, todo como texto
SILVER = RAIZ / "silver"                # ya interpretado, con tipos correctos (normalizado)
GOLD   = RAIZ / "gold"                  # modelo estrella, con tablas de hechos y dimensiones, listo para análisis
ALMACEN = RAIZ / "almacen.duckdb"       # donde se guardan los Parquet finales, listos para análisis (dimensiones y hechos)
REGISTRO = RAIZ / "cargados.json"       # registro de qué archivos ya se han cargado y procesado

ENCODING = "utf-8"                      # explicito: Windows usa cp1252, Linux usa utf-8, pero mejor forzar utf-8 para que sea portable

for d in (ORIGEN, BRONZE, SILVER, GOLD):
    d.mkdir(parents=True, exist_ok=True)  # crear carpetas si no existen

def sql_ruta(p):
    return Path(p).as_posix()  # para que DuckDB pueda leer la ruta, convertir a formato POSIX (con /)

def excel_del_periodo(carpeta=ORIGEN):
    print(f"Buscando archivos Excel en {carpeta}...")
    """Los .xlsx de la carpeta, sin importar mayusculas/minusuclas ni temporales de Excel."""
    # ~$ es el prefijo de los archivos temporales de Excel, que no queremos procesar
    return sorted(f for f in carpeta.iterdir()
                  if f.suffix.lower() == ".xlsx" and not f.name.startswith("~$"))