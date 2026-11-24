"""Revisa resultados nuevos, los guarda y avisa por Telegram.

Uso:
    python main.py            # ciclo normal (lo ejecuta GitHub Actions)
    python main.py --prueba   # envía un mensaje de prueba a Telegram
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

import analisis
import scraper
import telegram_bot

HISTORIAL = Path(__file__).parent / "data" / "historial.json"
ZONA_CO = timezone(timedelta(hours=-5))


def cargar() -> list[dict]:
    if HISTORIAL.exists():
        return json.loads(HISTORIAL.read_text(encoding="utf-8") or "[]")
    return []


def guardar(hist: list[dict]) -> None:
    HISTORIAL.parent.mkdir(parents=True, exist_ok=True)
    hist = sorted(hist, key=lambda r: (r["fecha"], r["sorteo"]))
    HISTORIAL.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def sorteos_permitidos() -> set[str]:
    """Variable SORTEOS = 'Dorado Noche, Chontico Día, ...'. Vacía = todos."""
    valor = os.getenv("SORTEOS", "").strip()
    return {scraper.normalizar(s) for s in valor.split(",") if s.strip()}


def formatear(r: dict, a: dict) -> str:
    fecha = datetime.fromisoformat(r["fecha"]).strftime("%d/%m/%Y")
    extra = ""
    if r.get("quinta"):
        extra += f"   Quinta: <b>{r['quinta']}</b>"
    if r.get("signo"):
        extra += f"   Signo: <b>{escape(r['signo'])}</b>"
    pond = "  ".join(f"<code>{n}</code>" for n in a["ponderadas"])
    return (
        f"🎰 <b>{escape(r['sorteo'])}</b> — {fecha}\n"
        f"Número: <b>{r['numero']}</b>{extra}\n\n"
        f"📊 Análisis ({a['muestra']} sorteos, {a['ambito']})\n"
        f"Dígitos más repetidos (últimos 50): {', '.join(a['calientes'])}\n\n"
        f"🎲 Combinaciones sugeridas\n"
        f"• Más frecuentes por posición: <code>{a['frecuente']}</code>\n"
        f"• Más atrasados por posición: <code>{a['atrasado']}</code>\n"
        f"• Aleatorias ponderadas: {pond}\n\n"
        f"<i>Sorteo aleatorio: ninguna combinación tiene más probabilidad que otra (1 en 10.000).</i>"
    )


def ciclo() -> int:
    html = scraper.descargar()
    encontrados = scraper.parsear(html)
    if not encontrados:
        print("ERROR: no se encontró ningún resultado. Puede que la página cambió de formato.")
        return 1

    filtro = sorteos_permitidos()
    if filtro:
        encontrados = [r for r in encontrados if scraper.normalizar(r.sorteo) in filtro]

    hist = cargar()
    claves = {r["clave"] for r in hist}
    nuevos = [r for r in encontrados if r.clave not in claves]
    print(f"Leídos: {len(encontrados)} | nuevos: {len(nuevos)} | historial: {len(hist)}")

    if not hist:  # primera ejecución: carga sin avisar uno por uno
        hist.extend(r.a_dict() for r in nuevos)
        guardar(hist)
        telegram_bot.enviar(
            f"✅ Bot de chances activado. Cargué {len(nuevos)} resultados recientes.\n"
            f"Desde ahora te aviso cada resultado nuevo."
        )
        return 0

    hoy = datetime.now(ZONA_CO).date()
    try:
        for r in sorted(nuevos, key=lambda x: x.fecha):
            d = r.a_dict()
            hist.append(d)
            # No avisa resultados viejos (p. ej. si se borró el historial)
            if date.fromisoformat(r.fecha) >= hoy - timedelta(days=1):
                a = analisis.combinaciones(hist, r.sorteo, semilla=r.clave)
                telegram_bot.enviar(formatear(d, a))
    finally:
        guardar(hist)  # guarda lo enviado aunque algo falle a mitad
    return 0


if __name__ == "__main__":
    if "--prueba" in sys.argv:
        telegram_bot.enviar("🔔 Mensaje de prueba del bot de chances. ¡Conexión correcta!")
        sys.exit(0)
    sys.exit(ciclo())
