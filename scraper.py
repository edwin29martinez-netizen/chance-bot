"""Descarga y lee los resultados de chances de 4 cifras desde loteriasdehoy.co."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, asdict
from datetime import date

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

URL = "https://loteriasdehoy.co/chances"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9",
}

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
SIGNOS = [
    "aries", "tauro", "geminis", "cancer", "leo", "virgo", "libra",
    "escorpion", "escorpio", "sagitario", "capricornio", "acuario", "piscis",
]
FECHA_RE = re.compile(r"(\d{1,2})\s+(?:de\s+)?([a-z]+)\s+(?:de\s+)?(\d{4})")
ENCABEZADOS = ("h2", "h3", "h4")


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes (Día -> dia, Caribeña -> caribena)."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c)).strip()


@dataclass
class Resultado:
    sorteo: str
    fecha: str          # ISO yyyy-mm-dd
    numero: str         # 4 cifras
    quinta: str | None = None
    signo: str | None = None

    @property
    def clave(self) -> str:
        return f"{normalizar(self.sorteo)}|{self.fecha}"

    def a_dict(self) -> dict:
        d = asdict(self)
        d["clave"] = self.clave
        return d


def descargar(url: str = URL, timeout: int = 30) -> str:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text


def _texto_del_bloque(encabezado: Tag, limite: int = 40) -> str:
    """Une el texto que sigue a un encabezado hasta el siguiente encabezado."""
    partes: list[str] = []
    for el in encabezado.next_elements:
        if isinstance(el, Tag) and el.name in ENCABEZADOS:
            break
        if isinstance(el, NavigableString):
            s = el.strip()
            if s:
                partes.append(s)
                if len(partes) >= limite:
                    break
    return " ".join(partes)


def parsear(html: str) -> list[Resultado]:
    soup = BeautifulSoup(html, "html.parser")
    resultados: list[Resultado] = []
    vistos: set[str] = set()

    for h in soup.find_all(ENCABEZADOS):
        nombre = " ".join(h.get_text(" ", strip=True).split())
        if not nombre or len(nombre) > 40:
            continue
        bloque = _texto_del_bloque(h)
        bloque_n = normalizar(bloque)
        m = FECHA_RE.search(bloque_n)
        if not m or m.group(2) not in MESES:
            continue
        try:
            fecha = date(int(m.group(3)), MESES[m.group(2)], int(m.group(1)))
        except ValueError:
            continue

        resto = bloque_n[m.end():]
        # Solo los dígitos que vienen justo después de la fecha
        cifras = re.match(r"[\d\s\-–·|,.]*", resto).group()
        digitos = "".join(re.findall(r"\d", cifras))
        if len(digitos) < 4:          # descarta Pick 3, Paisita 3, Cash Three…
            continue

        signo = None
        cola = resto[len(cifras): len(cifras) + 30]
        for s in SIGNOS:
            if re.search(rf"\b{s}\b", cola):
                signo = s.capitalize()
                break

        r = Resultado(
            sorteo=nombre,
            fecha=fecha.isoformat(),
            numero=digitos[:4],
            quinta=digitos[4:5] or None,
            signo=signo,
        )
        if r.clave not in vistos:
            vistos.add(r.clave)
            resultados.append(r)
    return resultados


if __name__ == "__main__":
    for r in parsear(descargar()):
        print(r)
