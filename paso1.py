import duckdb

con = duckdb.connect()

tabla = con.execute("DESCRIBE SELECT * FROM read_parquet('bronze/base/202407.parquet')").df()

print(tabla[["column_name", "column_type"]])
print("Total de columnas:", len(tabla))
