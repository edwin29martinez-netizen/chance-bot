"""Estadística descriptiva del historial y combinaciones sugeridas.

IMPORTANTE: cada sorteo es independiente y aleatorio. Estas cifras describen
el pasado; no aumentan la probabilidad de acertar (1 en 10.000 para 4 cifras).
"""
from __future__ import annotations

import random
from collections import Counter

from scraper import normalizar


def numeros(historial: list[dict], sorteo: str | None = None, ultimos: int = 300) -> list[str]:
    datos = sorted(historial, key=lambda r: r["fecha"])
    if sorteo:
        s = normalizar(sorteo)
        datos = [r for r in datos if normalizar(r["sorteo"]) == s]
    return [r["numero"] for r in datos][-ultimos:]


def frecuencia_posicional(nums: list[str]) -> list[Counter]:
    pos = [Counter({str(d): 0 for d in range(10)}) for _ in range(4)]
    for n in nums:
        for i, c in enumerate(n[:4]):
            pos[i][c] += 1
    return pos


def atraso_posicional(nums: list[str]) -> list[dict[str, int]]:
    """Sorteos transcurridos desde la última vez que salió cada dígito en cada posición."""
    total = len(nums)
    atraso = [{str(d): total for d in range(10)} for _ in range(4)]
    for idx, n in enumerate(nums):
        for i, c in enumerate(n[:4]):
            atraso[i][c] = total - 1 - idx
    return atraso


def calientes(nums: list[str], top: int = 3) -> list[str]:
    c = Counter("".join(nums))
    return [d for d, _ in c.most_common(top)]


def combinaciones(historial: list[dict], sorteo: str, semilla: str, n_aleatorias: int = 3) -> dict:
    """Devuelve combinaciones de 4 cifras con su criterio."""
    propios = numeros(historial, sorteo)
    base = propios if len(propios) >= 25 else numeros(historial)  # poco historial -> usa todos
    freq = frecuencia_posicional(base)
    atr = atraso_posicional(base)

    frecuente = "".join(max(f, key=lambda d: (f[d], -int(d))) for f in freq)
    atrasado = "".join(max(a, key=lambda d: (a[d], -int(d))) for a in atr)

    rnd = random.Random(semilla)
    ponderadas: list[str] = []
    while len(ponderadas) < n_aleatorias:
        num = "".join(
            rnd.choices(list(f.keys()), weights=[v + 1 for v in f.values()])[0] for f in freq
        )
        if num not in ponderadas and num not in (frecuente, atrasado):
            ponderadas.append(num)

    return {
        "muestra": len(base),
        "ambito": "este sorteo" if base is propios else "todos los sorteos",
        "calientes": calientes(base[-50:]),
        "frecuente": frecuente,
        "atrasado": atrasado,
        "ponderadas": ponderadas,
    }
