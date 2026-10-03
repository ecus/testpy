"""PASO 1 — Cada Excel a un parquet, todo como texto. No interpreta nada."""
import json, re, time
import duckdb
from rutas import ORIGEN, BRONZE, REGISTRO, ENCODING, sql_ruta, excel_del_periodo

HOJAS = ["Base", "Castigo", "Venta"]   # Base es obligatoria; Castigo y Venta, si existen
MIN_FILAS_BASE = 1000                  # si Base trae menos, algo se leyó mal (antes pasaban 0 o 1 fila)

def periodo_de(nombre):
    """Extrae el periodo de un nombre de archivo, por ejemplo Base_31012024.xlsx → 202401"""
    m = re.search(r"(\d{2})(\d{2})(\d{4})", nombre)    # Base_31012024 -> 202401
    return f"{m.group(3)}{m.group(2)}" if m else None

def a_bronze(xlsx, periodo, hoja, con):
    """Convierte un Excel a Parquet en la carpeta BRONZE, TODO como texto."""
    BRONZE.mkdir(parents=True, exist_ok=True)
    destino = BRONZE / hoja.lower() / f"{periodo}.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""COPY (
        SELECT *, '{periodo}' AS _periodo, '{xlsx.name}' AS _archivo, '{hoja}' AS _hoja, current_date AS _cargado
        FROM read_xlsx('{sql_ruta(xlsx)}', sheet='{hoja}', all_varchar=true)
    ) TO '{sql_ruta(destino)}' (FORMAT parquet, COMPRESSION zstd)""")

    # Otra forma de hacerlo, usando parámetros para evitar problemas con comillas en los nombres de archivo:
    #con.execute(f"""COPY (
    #    SELECT *, ? AS _periodo, ? AS _archivo, ? AS _hoja, current_date AS _cargado
    #    FROM read_xlsx(?, all_varchar=true)
    #) TO '{sql_ruta(destino)}' (FORMAT parquet, COMPRESSION zstd)""",
    #    [periodo, xlsx.name, hoja, sql_ruta(xlsx)])

    
    n = con.execute("SELECT count(*) FROM read_parquet(?)",
                    [sql_ruta(destino)]).fetchone()[0]

    # Otra forma de contar las filas, usando DuckDB para leer el parquet recién creado: 
    #n = con.execute(f"SELECT count(*) FROM '{sql_ruta(destino)}'").fetchone()[0]
    
    #return n, destino.stat().st_size / 1024**2  retorna el número de filas y el tamaño en MB del parquet
    return n, destino.stat().st_size / 1024**2

def main():
    con = duckdb.connect(); con.sql("INSTALL excel; LOAD excel")  # instalar y cargar el módulo de Excel
    
    hechos = json.loads(REGISTRO.read_text(encoding=ENCODING)) if REGISTRO.exists() and REGISTRO.stat().st_size > 0 else {} # es un diccionario con los archivos ya procesados y sus periodos
    
    #Ordenar periodos , no por nombre de archivo, para que se procesen en orden cronológico
    pendientes = sorted(((periodo_de(f.name), f) for f in excel_del_periodo()), key=lambda x: x[0])  # lista de tuplas (periodo, archivo) de los Excel pendientes de procesar
    
    for p, xlsx in pendientes:    
        if hechos.get(p, {}).get("ok"):
            print(f"Ya procesado {xlsx.name} para el periodo {p}, saltando...")
            continue  # ya procesado, saltar al siguiente
        else:
            print(f"Procesando {xlsx.name} para el periodo {p}...")

        print(f"Procesando {xlsx.name} para el periodo {p}...")
        t = time.time()
        hechos[p] = {"ok": False, "archivo": xlsx.name, "hojas": {}}

        try:
            for hoja in HOJAS:  # HOJAS es una lista de nombres de hojas a procesar, definida en otro lugar
                try:
                    n, mb = a_bronze(xlsx, p, hoja,  con)
                    hechos[p]["hojas"][hoja] = {"filas": n, "mb": round(mb, 2)}
                    print(f"   {hoja}: {n} filas, {mb:.2f} MB")
                    #print(f"Procesado {xlsx.name} para el periodo {p}: {n} filas, {mb:.2f} MB en {time.time() - t:.2f} segundos")
                except Exception as e:
                    # si falta Castigo o Venta seguimos; el error queda anotado
                    hechos[p]["hojas"][hoja] = {"error": str(e)}
                    print(f"   {hoja}: ERROR {e}")
                    #print(f"Error al procesar {xlsx.name} para el periodo {p}: {e}")

            filas_base = hechos[p]["hojas"].get("Base", {}).get("filas", 0)
            hechos[p]["ok"] = filas_base >= MIN_FILAS_BASE
            estado = "OK" if hechos[p]["ok"] else "REVISAR (Base Vacía o con error)"
            print(f"    {estado} en {time.time() - t:.1f} segundos")
        finally:
            REGISTRO.write_text(json.dumps(hechos, indent=3, ensure_ascii=False), encoding=ENCODING)
    
    con.close()

if __name__ == "__main__":
    main()
