"""Envío de mensajes a Telegram. Sin credenciales, imprime en consola (modo prueba)."""
from __future__ import annotations

import os
import time

import requests


def enviar(texto: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("---- [modo prueba: sin TELEGRAM_TOKEN/TELEGRAM_CHAT_ID] ----")
        print(texto)
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    datos = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    for intento in range(3):
        r = requests.post(url, data=datos, timeout=20)
        if r.status_code == 429:  # límite de Telegram: espera y reintenta
            time.sleep(int(r.json().get("parameters", {}).get("retry_after", 3)))
            continue
        r.raise_for_status()
        return
    r.raise_for_status()
