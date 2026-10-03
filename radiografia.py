"""PASO 2 — Compara el esquema de todos los periodos y marca lo que cambió."""
from difflib import SequenceMatcher
import duckdb
from rutas import BRONZE, sql_ruta

def esquemas(con):
    """{periodo: {columna: tipo}} leyendo solo la cabecera de cada parquet."""
    out = {}
    for pq in sorted(BRONZE.glob("*.parquet")):
        d = con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [sql_ruta(pq)]).df()
        out[pq.stem] = dict(zip(d.column_name, d.column_type))
    return out

def informe(esq):
    periodos = list(esq)
    cols = sorted({c for e in esq.values() for c in e if not c.startswith("_")})
    print(f"{'columna':<22}" + "".join(f"{p[-2:]:>5}" for p in periodos) + "   diagnóstico")
    alertas = []
    for c in cols:
        presente = ["si" if c in esq[p] else " ." for p in periodos]
        diag = ""
        if not all(x == "si" for x in presente):
            primero = next(p for p in periodos if c in esq[p])
            ultimo  = next(p for p in reversed(periodos) if c in esq[p])
            if   periodos.index(primero) > 0:              diag = f"APARECE en {primero}"
            elif periodos.index(ultimo) < len(periodos)-1: diag = f"DESAPARECE tras {ultimo}"
            else:                                          diag = "INTERMITENTE"
            alertas.append((c, diag))
        print(f"{c:<22}" + "".join(f"{x:>5}" for x in presente) + f"   {diag}")
    return alertas

def posibles_renombres(esq, umbral=0.55):
    """Dos columnas que NUNCA coexisten y con nombre parecido = renombre probable."""
    periodos = list(esq)
    pres = {c: [c in esq[p] for p in periodos]
            for c in {c for e in esq.values() for c in e} if not c.startswith("_")}
    parciales = [c for c, v in pres.items() if not all(v)]
    pares = []
    for i, a in enumerate(parciales):
        for b in parciales[i+1:]:
            if any(x and y for x, y in zip(pres[a], pres[b])):
                continue                              # coexisten -> no es renombre
            sim = SequenceMatcher(None, a.lower(), b.lower()).ratio()
            if sim >= umbral:
                cuando = periodos[min(j for j, x in enumerate(pres[b]) if x)]
                pares.append((a, b, cuando, sim))
    return sorted(pares, key=lambda x: -x[3])

def main():
    con = duckdb.connect()
    esq = esquemas(con)
    print("Periodos:", ", ".join(esq), "\n")
    alertas = informe(esq)
    print(f"\n{len(alertas)} alertas de esquema")
    pares = posibles_renombres(esq)
    print("\n=== POSIBLES RENOMBRES ===")
    if not pares: print("  ninguno")
    for a, b, cuando, sim in pares:
        print(f"  '{a}'  <->  '{b}'   parecido {sim:.0%}, divergen en {cuando}")
    con.close()

if __name__ == "__main__":
    main()