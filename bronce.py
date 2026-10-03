"""Bronze: cada Excel a un parquet, TODO como texto, sin interpretar nada."""
import re, json, time, duckdb
from pathlib import Path

ORIGEN = Path("demo/origen")
BRONZE = Path("demo/bronze")
REG    = Path("demo/cargados.json")

def periodo_de(nombre):
    m = re.search(r"(\d{2})(\d{2})(\d{4})", nombre)    # Base_31012024 -> 202401
    return f"{m.group(3)}{m.group(2)}" if m else None

def a_bronze(xlsx, periodo, con):
    BRONZE.mkdir(parents=True, exist_ok=True)
    destino = BRONZE / f"{periodo}.parquet"
    con.sql(f"""COPY (
        SELECT *, '{periodo}' AS _periodo, '{xlsx.name}' AS _archivo,
               current_date AS _cargado
        FROM read_xlsx('{xlsx}', all_varchar=true)
    ) TO '{destino}' (FORMAT parquet, COMPRESSION zstd)""")
    n = con.sql(f"SELECT count(*) FROM '{destino}'").fetchone()[0]
    return n, destino.stat().st_size / 1024**2

if __name__ == "__main__":
    con = duckdb.connect(); con.sql("INSTALL excel; LOAD excel;")
    hechos = json.loads(REG.read_text()) if REG.exists() else {}

    for xlsx in sorted(ORIGEN.glob("*.xlsx")):
        p = periodo_de(xlsx.name)
        if p in hechos:
            print(f"  {p} ya cargado"); continue
        t = time.time()
        try:
            n, mb = a_bronze(xlsx, p, con)
            hechos[p] = {"ok": True, "filas": n, "mb": round(mb, 2)}
            print(f"  {p}  {n:,} filas  {mb:.2f} MB  {time.time()-t:.1f}s")
        except Exception as e:
            hechos[p] = {"ok": False, "error": str(e)[:200]}
            print(f"  {p}  FALLÓ: {e}")
        finally:
            REG.write_text(json.dumps(hechos, indent=2))