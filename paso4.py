import duckdb
from pathlib import Path

con = duckdb.connect()

# Igual que en el paso 3: {periodo: set de columnas}
columnas = {}
for archivo in sorted(Path("bronze/base").glob("*.parquet")):
    tabla = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{archivo}')").df()
    columnas[archivo.stem] = set(tabla["column_name"])

periodos = list(columnas)
todas = set().union(*columnas.values())       # todas las columnas que existieron alguna vez

# Cabecera: primer mes a la izquierda, último a la derecha
print(f"{'':<34}{periodos[0]}{' ' * (len(periodos) - 12)}{periodos[-1]}")

for c in sorted(todas):
    presente = [c in columnas[p] for p in periodos]      # [True, True, False, ...]
    if all(presente):
        continue                                         # está siempre: no interesa
    barra = "".join("█" if x else "·" for x in presente)
    meses = [p for p, x in zip(periodos, presente) if x]
    nombre = c.replace("\n", "⏎")                        # que no se parta la línea
    print(f"{nombre:<34}{barra}   {meses[0]}–{meses[-1]} ({len(meses)} meses)")