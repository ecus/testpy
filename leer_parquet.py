import pyarrow.parquet as pq

# --- Leer SOLO una columna de Parquet (column pruning) ---
# En CSV tendrías que leer TODO el archivo
tabla_parcial = pq.read_table("pedidos.parquet", columns=["ciudad", "precio"])
print(f"Columnas leídas: {tabla_parcial.column_names}")
print(f"Filas: {len(tabla_parcial)}")

# Convertir a Python para trabajar
ciudades = tabla_parcial.column("ciudad").to_pylist()
precios = tabla_parcial.column("precio").to_pylist()

# Calcular total por ciudad (solo leyendo 2 de 7 columnas)
ventas_ciudad = {}
for ciudad, precio in zip(ciudades, precios):
    ventas_ciudad[ciudad] = ventas_ciudad.get(ciudad, 0) + precio

print("\nVentas por ciudad:")
for ciudad, total in sorted(ventas_ciudad.items(), key=lambda x: -x[1]):
    print(f"  {ciudad:12} → {total:>12,.2f}€")

# --- Ver metadatos del archivo ---
metadata = pq.read_metadata("pedidos.parquet")
print(f"\nMetadatos Parquet:")
print(f"  Filas totales: {metadata.num_rows:,}")
print(f"  Columnas: {metadata.num_columns}")
print(f"  Row groups: {metadata.num_row_groups}")