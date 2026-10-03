def mostrar_menu():
    """Muestra las opciones disponibles."""
    print("")
    print("=" * 35)
    print("  GESTOR DE GASTOS PERSONALES")
    print("=" * 35)
    print("  1. Añadir gasto")
    print("  2. Ver todos los gastos")
    print("  3. Resumen por categoría")
    print("  4. Buscar gastos")
    print("  5. Salir")
    print("-" * 35)
    
    while True:
        opcion = input("Seleccione una opción (1-5): ")
        if opcion in ["1", "2", "3", "4", "5"]:
            return opcion
        else:
            print("Opción inválida. Por favor, seleccione una opción válida (1-5).")   

# Estructura: lista de diccionarios
# Cada gasto es un diccionario con 3 campos
gastos = []  # Empieza vacío

# Ejemplo de cómo se verá cuando tenga datos:
# gastos = [
#     {"concepto": "Café", "cantidad": 2.50, "categoria": "comida"},
#     {"concepto": "Metro", "cantidad": 1.50, "categoria": "transporte"},
#     {"concepto": "Netflix", "cantidad": 12.99, "categoria": "ocio"},
# ]

# Acceder a datos de un gasto:
# gastos[0]["concepto"]  → "Café"
# gastos[0]["cantidad"]  → 2.50

def agregar_gasto(gastos):
    """Pide datos al usuario y añade un gasto a la lista."""
    print("")
    concepto = input("  ¿Qué compraste? ")
    cantidad = float(input("  ¿Cuánto costó? (€): "))
    print("  Categorías: comida, transporte, ocio, hogar, otros")
    categoria = input("  Categoría: ").lower()

    gasto = {
        "concepto": concepto,
        "cantidad": cantidad,
        "categoria": categoria
    }
    gastos.append(gasto)  # Añadir a la lista
    print(f"  [OK] Gasto registrado: {concepto} ({cantidad:.2f}€)")


def ver_gastos(gastos):
    """Muestra todos los gastos registrados."""
    if len(gastos) == 0:
        print("  No hay gastos registrados todavía.")
        return

    print("")
    print(f"  {'#':<4}{'Concepto':<20}{'Cantidad':<12}{'Categoría'}")
    print("  " + "-" * 50)

    total = 0
    for i in range(len(gastos)):
        g = gastos[i]
        print(f"  {i+1:<4}{g['concepto']:<20}{g['cantidad']:<12.2f}{g['categoria']}")
        total = total + g["cantidad"]

    print("  " + "-" * 50)
    print(f"  TOTAL: {total:.2f}€ ({len(gastos)} gastos)")


def resumen_categorias(gastos):
    """Muestra el total gastado por categoría."""
    if len(gastos) == 0:
        print("  No hay gastos registrados.")
        return

    # Acumular por categoría
    categorias = {}
    for gasto in gastos:
        cat = gasto["categoria"]
        if cat in categorias:
            categorias[cat] = categorias[cat] + gasto["cantidad"]
        else:
            categorias[cat] = gasto["cantidad"]

    # Mostrar resumen
    print("")
    print("  === RESUMEN POR CATEGORÍA ===")
    total_general = 0
    for cat in categorias:
        total_cat = categorias[cat]
        total_general = total_general + total_cat
        print(f"  {cat:<15} {total_cat:>8.2f}€")

    print(f"  {'TOTAL':<15} {total_general:>8.2f}€")


def buscar_gastos(gastos):
    """Busca gastos por categoría o por importe mínimo."""
    print("  Buscar por: (1) categoría  (2) importe mínimo")
    tipo = input("  Opción: ")

    encontrados = []
    if tipo == "1":
        cat = input("  ¿Qué categoría? ").lower()
        for gasto in gastos:
            if gasto["categoria"] == cat:
                encontrados.append(gasto)
    elif tipo == "2":
        minimo = float(input("  ¿Importe mínimo? (€): "))
        for gasto in gastos:
            if gasto["cantidad"] >= minimo:
                encontrados.append(gasto)

    if len(encontrados) == 0:
        print("  No se encontraron gastos con esos criterios.")
    else:
        print(f"  Encontrados: {len(encontrados)} gastos")
        for g in encontrados:
            print(f"    - {g['concepto']}: {g['cantidad']:.2f}€ ({g['categoria']})")


def menu():
    """Función principal que gestiona el menú y las opciones."""
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            agregar_gasto(gastos)
        elif opcion == "2":
            ver_gastos(gastos)
        elif opcion == "3":
            resumen_categorias(gastos)
        elif opcion == "4":
            buscar_gastos(gastos)
        elif opcion == "5":
            print("  ¡Hasta luego!")
            break

menu()