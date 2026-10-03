# pipeline_ventas.py — Tu primer script de limpieza y análisis
import csv
import json
from datetime import datetime
from collections import defaultdict

# Leer CSV de ventas

def extraer_ventas(ruta_csv):
    """Lee el CSV de ventas y devuelve una lista de diccionarios."""

    with open(ruta_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)  # Devuelve todas las filas como lista de diccionarios

# Transformar datos: limpiar y convertir tipos
def transformar_ventas(ventas_raw):
    """Limpia y transforma los datos de ventas."""
    """Limpia datos sucios y calcula totales. Devuelve (limpias, errores)."""
    ventas_limpias = []
    errores = []
    
    for i, venta in enumerate(ventas_raw):
        try:
            #validar cantidad vacia
            if not venta.get("cantidad", "").strip():
                raise ValueError(f"Fila {i+1}: Cantidad vacía")
            
            #validar precio vacio
            if not venta.get("precio_unitario", "").strip():
                raise ValueError(f"Fila {i+1}: Precio unitario vacío")

            #validar producto vacio
            if not venta.get("producto", "").strip():
                raise ValueError(f"Fila {i+1}: Producto vacío")
            
            # Convertir cantidad (default 1 si está vacío)
            cantidad_raw = venta.get("cantidad", "").strip()
            cantidad = int(cantidad_raw) if cantidad_raw else 1

            # Convertir precio
            precio = float(venta.get("precio_unitario", 0)) if venta.get("precio_unitario") else 0.0

            # Calcular total
            total = cantidad * precio

            # Registro Limpio
            
            ventas_limpias.append({
                "fecha": venta.get("fecha", ""),
                "producto": venta.get("producto", "").strip(),
                "categoria": venta.get("categoria", "").strip(),
                "cantidad": cantidad,
                "precio_unitario": precio,
                "cliente": venta.get("cliente", "").strip(),
                "total": total
            })

        except (ValueError, TypeError) as e:
            errores.append({
                "fila": i + 2,  # +2 porque el CSV tiene encabezado y el índice empieza en 0
                "error": str(e),
                "datos": dict(venta)
            })

    return ventas_limpias, errores

# ANALYZE: generar metricas
def generar_resumen(ventas_limpias):
    """Genera el resumen ejecutivo a partir de datos limpios."""
    if not ventas_limpias:
        return {
            "error": "No hay ventas limpias para analizar."
        }

    #Metricas Generales
    total_facturado = sum(v["total"] for v in ventas_limpias)
    num_transacciones = len(ventas_limpias)
    ticket_medio = total_facturado / num_transacciones if num_transacciones > 0 else 0
    
    #Por categoria
    por_categoria = defaultdict(lambda: {"total": 0, "transacciones": 0})
    for v in ventas_limpias:
        cat = v["categoria"]
        por_categoria[cat]["total"] += v["total"]
        por_categoria[cat]["transacciones"] += 1

    #Top Productos
    productos_total = defaultdict(float)
    for v in ventas_limpias:
        productos_total[v["producto"]] += v["total"]

    top_productos = sorted(productos_total.items(), key=lambda x: x[1], reverse=True)[:3]

    #Clientes unicos
    clientes = set(v["cliente"] for v in ventas_limpias if v["cliente"])
    
    return {
        "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_facturado": round(total_facturado, 2),
        "num_transacciones": num_transacciones,
        "ticket_medio": round(ticket_medio, 2),
        "clientes_unicos": len(clientes),
        "por_categoria": dict(por_categoria),
        "top_3_productos": [
            {"producto": prod, "total": round(total, 2)} for prod, total in top_productos
        ],
    }

# LOAD: escribir resultados a JSON
def guardar_resultado(resumen, errores, ruta_salida, ruta_errores):
    """Guarda el resumen y los errores en archivos JSON."""
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=3, ensure_ascii=False)
    
    if errores:
        with open(ruta_errores, "w", encoding="utf-8") as f:
            json.dump(errores, f, indent=3, ensure_ascii=False)

# ═══ MAIN: orquestar el pipeline ══════════════════════════════
def main():
    """Punto de entrada del pipeline."""
    print("=" * 50)
    print("  PIPELINE DE VENTAS DIARIAS")
    print("=" * 50)
    
    #Configuracion
    ruta_entrada = "data/ventas_dia.csv"
    ruta_salida = "data/resumen_dia.json"
    ruta_errores = "data/errores_dia.json"
    
    # 1. EXTRACT
    print("\n[1/4] Extrayendo datos...")
    ventas_raw = extraer_ventas(ruta_entrada)
    print(f"      Leídos: {len(ventas_raw)} registros")
    
    # 2. TRANSFORM
    print("[2/4] Limpiando y transformando...")
    ventas_limpias, errores = transformar_ventas(ventas_raw)
    tasa_exito = len(ventas_limpias) / len(ventas_raw) * 100 if ventas_raw else 0
    print(f"      Limpios: {len(ventas_limpias)} registros ({tasa_exito:.2f}% éxito)")
    print(f"      Errores: {len(errores)} registros")
    
    # 3. ANALYZE
    print("[3/4] Generando resumen ejecutivo...")
    resumen = generar_resumen(ventas_limpias)
    print(f"      Total Facturado: {resumen['total_facturado']:.2f} USD")
    
    # 4. LOAD
    print("[4/4] Guardando resultados...")
    guardar_resultado(resumen, errores, ruta_salida, ruta_errores)
    print(f"      Resumen guardado en: {ruta_salida}")
    if errores:
        print(f"      Errores guardados en: {ruta_errores}")

    #Reporte final
    print("\n" + "=" * 50)
    print("  REPSUMEN EJECUTIVO")
    print("=" * 50)
    print(f"  Facturación total: {resumen['total_facturado']}€")
    print(f"  Ticket medio:      {resumen['ticket_medio']}€")
    print(f"  Transacciones:     {resumen['num_transacciones']}")
    print(f"  Clientes únicos:   {resumen['clientes_unicos']}")
    print(f"\n  Top 3 productos:")
    for item in resumen["top_3_productos"]:
        print(f"    • {item['producto']}: {item['total']}€")
    print("=" * 50)
    
if __name__ == "__main__":
    main()