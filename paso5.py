import duckdb
from pathlib import Path

JUNIO = "bronze/base/202406.parquet"
JULIO = "bronze/base/202407.parquet"
ANTIGUA = "Sector Economico"
NUEVA = "Sector economico 4B2"
DESTINO = Path("equivalencias/sector_4b2.csv")

def reparar(texto):
    """Arregla texto UTF-8 que se leyó mal: 'ConstrucciÃ³n' -> 'Construcción'."""
    try:
        texto = texto.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass                                # no estaba roto: se deja igual
    return texto.replace("¤", "ñ")          # caso raro del Excel antiguo: 'Ense¤anza'

con = duckdb.connect()

# 1) El cruce de siempre: sector antes y ahora de los mismos préstamos
cruce = con.execute(f"""
    SELECT a."{ANTIGUA}" AS antes,
           b."{NUEVA}"   AS ahora,
           count(*)      AS prestamos
    FROM '{JUNIO}' a
    JOIN '{JULIO}' b USING (Expediente)
    GROUP BY 1, 2
""").df()

# 2) Reparar los textos
cruce["antes"] = cruce["antes"].map(reparar)
cruce["ahora"] = cruce["ahora"].map(reparar)

# 3) % de confianza: de los préstamos de cada sector antiguo, cuántos van a cada nuevo
cruce["total"] = cruce.groupby("antes")["prestamos"].transform("sum")
cruce["pct"] = (cruce["prestamos"] / cruce["total"] * 100).round(1)

# 4) Quedarse con el mejor equivalente de cada sector antiguo
mejor = cruce.sort_values("prestamos", ascending=False).drop_duplicates("antes")
mejor = mejor.sort_values("antes")[["antes", "ahora", "prestamos", "pct"]]

# 5) Guardar
DESTINO.parent.mkdir(exist_ok=True)
mejor.to_csv(DESTINO, index=False, encoding="utf-8")
print(mejor.to_string(index=False))
print(f"\nGuardado en {DESTINO}")
