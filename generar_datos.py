# generar_datos.py — Crea el CSV de ventas con datos sucios
import csv
import os

os.makedirs("data", exist_ok=True)

ventas = [
    ["2024-03-15", "Laptop Pro 15", "electrónica", "2", "1299.99", "Ana García"],
    ["2024-03-15", "Monitor 4K", "electrónica", "1", "449.00", "Luis Pérez"],
    ["2024-03-15", "Camiseta Algodón", "ropa", "5", "24.99", "María López"],
    ["2024-03-15", "Teclado Mecánico", "electrónica", "3", "89.99", "Pedro Ruiz"],
    ["2024-03-15", "Pantalón Slim", "ropa", "2", "59.99", "Sara Torres"],
    ["2024-03-15", "Auriculares BT", "electrónica", "4", "N/A", "Jorge Díaz"],  # precio inválido
    ["2024-03-15", "Zapatillas Run", "calzado", "1", "129.99", "Ana García"],
    ["2024-03-15", "", "ropa", "3", "34.99", "Carlos Ruiz"],  # producto vacío
    ["2024-03-15", "Mochila Pro", "accesorios", "2", "79.99", "Luis Pérez"],
    ["2024-03-15", "Portátil Air", "electrónica", "1", "999.00", "María López"],
    ["2024-03-15", "Jersey Lana", "ropa", "4", "45.50", "Pedro Ruiz"],
    ["2024-03-15", "Ratón Gaming", "electrónica", "", "49.99", "Sara Torres"],  # cantidad vacía
    ["2024-03-15", "Botas Montaña", "calzado", "1", "189.00", "Jorge Díaz"],
    ["2024-03-15", "USB-C Hub", "electrónica", "6", "35.99", "Ana García"],
    ["2024-03-15", "Sudadera Tech", "ropa", "2", "69.99", "Carlos Ruiz"],
]

with open("data/ventas_dia.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fecha", "producto", "categoria", "cantidad", "precio_unitario", "cliente"])
    writer.writerows(ventas)

print(f"[OK] CSV generado: data/ventas_dia.csv ({len(ventas)} filas)")