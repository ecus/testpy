import csv
import json
import os
import pyarrow as pa
import pyarrow.parquet as pq
import time

# Generar datos de ejemplo: 100.000 pedidos
import random
random.seed(42)

pedidos = []
ciudades = ["Madrid", "Barcelona", "Sevilla", "Valencia", "Bilbao"]
productos = ["Camiseta", "Pantalón", "Zapatos", "Chaqueta", "Bufanda"]

for i in range(100_000):
    pedidos.append({
        "id": i + 1,
        "fecha": f"2026-01-{random.randint(1,28):02d}",
        "cliente_id": random.randint(1, 10000),
        "producto": random.choice(productos),
        "precio": round(random.uniform(10, 200), 2),
        "cantidad": random.randint(1, 5),
        "ciudad": random.choice(ciudades),
    })

# --- Guardar como CSV ---
with open("pedidos.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=pedidos[0].keys())
    writer.writeheader()
    writer.writerows(pedidos)

# --- Guardar como Parquet ---
tabla = pa.table({
    "id": [p["id"] for p in pedidos],
    "fecha": [p["fecha"] for p in pedidos],
    "cliente_id": [p["cliente_id"] for p in pedidos],
    "producto": [p["producto"] for p in pedidos],
    "precio": [p["precio"] for p in pedidos],
    "cantidad": [p["cantidad"] for p in pedidos],
    "ciudad": [p["ciudad"] for p in pedidos],
})
pq.write_table(tabla, "pedidos.parquet")

# --- Comparar tamaños ---
tam_csv = os.path.getsize("pedidos.csv") / (1024 * 1024)
tam_parquet = os.path.getsize("pedidos.parquet") / (1024 * 1024)
print(f"CSV:     {tam_csv:.2f} MB")
print(f"Parquet: {tam_parquet:.2f} MB")
print(f"Ratio:   {tam_csv/tam_parquet:.1f}x más pequeño")