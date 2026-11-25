"""Completa el historial con los últimos ~30 resultados de la página de cada chance."""
from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup

import scraper

BASE = "https://loteriasdehoy.co/"
MINIMO = 25  # si un chance tiene menos resultados guardados, se completa


def slug(nombre: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", scraper.normalizar(nombre)).strip("-")


def parsear_tabla(html: str, nombre: str) -> list[scraper.Resultado]:
    soup = BeautifulSoup(html, "html.parser")
    salida = []
    for fila in soup.find_all("tr"):
        celdas = [c.get_text(" ", strip=True) for c in fila.find_all(["td", "th"])]
        texto = scraper.normalizar(" ".join(celdas))
        m = scraper.FECHA_RE.search(texto)
        if not m or m.group(2) not in scraper.MESES:
            continue
        try:
            fecha = date(int(m.group(3)), scraper.MESES[m.group(2)], int(m.group(1)))
        except ValueError:
            continue
        resto = texto[m.end():]
        cifras = re.match(r"[\d\s\-–·|,.]*", resto).group()
        digitos = "".join(re.findall(r"\d", cifras))
        if len(digitos) < 4:
            continue
        signo = next((s.capitalize() for s in scraper.SIGNOS
                      if re.search(rf"\b{s}\b", resto[:40])), None)
        salida.append(scraper.Resultado(nombre, fecha.isoformat(), digitos[:4],
                                        digitos[4:5] or None, signo))
    return salida


def completar(hist: list[dict], nombres: set[str], excluir: set[str]) -> int:
    """Agrega al historial resultados pasados de los chances con pocos datos.
    `excluir`: claves que no se deben agregar aquí (los resultados nuevos por avisar)."""
    claves = {r["clave"] for r in hist} | excluir
    agregados = 0
    for nombre in sorted(nombres):
        n = sum(1 for r in hist if scraper.normalizar(r["sorteo"]) == scraper.normalizar(nombre))
        if n >= MINIMO:
            continue
        try:
            html = scraper.descargar(BASE + slug(nombre))
            for r in parsear_tabla(html, nombre):
                if r.clave not in claves:
                    hist.append(r.a_dict())
                    claves.add(r.clave)
                    agregados += 1
        except Exception as e:  # una página que falle no detiene el bot
            print(f"No se pudo cargar historial de {nombre}: {e}")
    return agregados
