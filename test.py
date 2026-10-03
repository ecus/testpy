from functools import reduce

clientes = [
    {"nombre": "Ana", "gasto": 1200},
    {"nombre": "Luis", "gasto": 89},
    {"nombre": "Maria", "gasto": 750},
    {"nombre": "Pedro", "gasto": 320},
    {"nombre": "Sara", "gasto": 2100},
    {"nombre": "Nuria", "gasto": 500},
]

IVA = 1.21
UMBRAL_VIP = 500

nuevo = list(
    map(
        lambda cliente: cliente["nombre"],
        filter(
            lambda cliente: cliente["gasto"] > UMBRAL_VIP,
            clientes,
        )
    )
)

nuevo