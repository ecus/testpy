import duckdb

con = duckdb.connect()

JUNIO = "bronze/base/202406.parquet"
JULIO = "bronze/base/202407.parquet"
ANTIGUA = "Sector Economico"
#NUEVA = "Sector economico 4B2"        # prueba luego con "Sector Economico\nAnexo03"
NUEVA = "Sector Economico\nAnexo03"
# 1) Tabla cruzada: para cada préstamo, su sector en junio y en julio
cruce = con.execute(f"""
    SELECT a."{ANTIGUA}" AS antes,
           b."{NUEVA}"   AS ahora,
           count(*)      AS prestamos
    FROM '{JUNIO}' a
    JOIN '{JULIO}' b USING (Expediente)     -- mismos préstamos en los dos meses
    GROUP BY 1, 2
""").df()

# 2) Para cada valor antiguo, quedarnos con el valor nuevo más frecuente
mejor = cruce.sort_values("prestamos", ascending=False).drop_duplicates("antes")
print(mejor.sort_values("antes").to_string(index=False))

# 3) Fidelidad: qué % de préstamos cae en su "mejor" equivalente
fidelidad = mejor["prestamos"].sum() / cruce["prestamos"].sum()
print(f"\nFidelidad: {fidelidad:.1%}")
