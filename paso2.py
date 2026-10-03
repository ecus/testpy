import duckdb
from pathlib import Path

con = duckdb.connect()

for archivo in sorted(Path("bronze/base").glob("*.parquet")):
    tabla = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{archivo}')").df()
    print(archivo.stem, len(tabla))
