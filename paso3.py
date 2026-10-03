import duckdb
from pathlib import Path

con = duckdb.connect()

# 1) Guardar las columnas de cada mes en un diccionario: {periodo: set de columnas}
columnas = {}
for archivo in sorted(Path("bronze/base").glob("*.parquet")):
    tabla = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{archivo}')").df()
    columnas[archivo.stem] = set(tabla["column_name"])

# 2) Comparar cada mes con el anterior
anterior = None
for periodo, cols in columnas.items():
    if anterior is not None:                      # el primer mes no tiene con quién compararse
        nuevas   = cols - columnas[anterior]
        perdidas = columnas[anterior] - cols
        if nuevas or perdidas:                    # solo imprimimos si hubo algún cambio
            print(f"\n{anterior} -> {periodo}")
            for c in sorted(nuevas):
                print(f"   + {c}")
            for c in sorted(perdidas):
                print(f"   - {c}")
    anterior = periodo
