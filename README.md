# Bot de chances (4 cifras) → Telegram

Revisa cada 15 minutos (10:00 a 00:59, hora Colombia) los resultados de los chances en
https://loteriasdehoy.co/chances, guarda el historial en `data/historial.json` y te envía por
Telegram cada resultado nuevo con un análisis estadístico y combinaciones sugeridas.

> Los chances son sorteos aleatorios e independientes: toda combinación tiene la misma
> probabilidad (1 en 10.000). El análisis describe el pasado; no predice el próximo número.

## Archivos
| Archivo | Qué hace |
|---|---|
| `main.py` | Ciclo principal: lee, detecta nuevos, avisa y guarda |
| `scraper.py` | Descarga y lee la página de resultados |
| `analisis.py` | Frecuencias, atrasos y combinaciones sugeridas |
| `telegram_bot.py` | Envía los mensajes |
| `.github/workflows/monitor.yml` | Programa la ejecución automática en GitHub |
| `data/historial.json` | Historial (lo actualiza el bot solo) |
| `tests/test_bot.py` | Pruebas sin internet |

## Puesta en marcha

1. **Crear el bot de Telegram.** En Telegram abre **@BotFather** → `/newbot` → copia el *token*.
2. **Obtener tu chat ID.** Escríbele cualquier cosa a tu bot nuevo y abre en el navegador
   `https://api.telegram.org/bot<TOKEN>/getUpdates`; copia el número de `"chat":{"id": ...}`.
3. **Crear el repositorio** en GitHub (recomendado **público**: minutos de Actions ilimitados;
   en privado el horario actual usa ~1.800 de los 2.000 min/mes gratis) y subir todo el
   contenido de esta carpeta, incluida la carpeta oculta `.github`.
4. **Guardar las claves.** En el repo: *Settings → Secrets and variables → Actions →
   New repository secret*:
   - `TELEGRAM_TOKEN` = token del paso 1
   - `TELEGRAM_CHAT_ID` = número del paso 2
5. **(Opcional) Elegir sorteos.** En la misma pantalla, pestaña *Variables*, crea `SORTEOS` con
   los nombres separados por coma, p. ej. `Dorado Noche, Chontico Día, Sinuano Noche, Astro Luna`.
   Sin esa variable, monitorea todos los de 4 cifras.
6. **Permitir que guarde el historial.** *Settings → Actions → General → Workflow permissions →*
   **Read and write permissions** → *Save*.
7. **Primera ejecución.** Pestaña *Actions* → **Monitor de chances** → *Run workflow*.
   Te llega “✅ Bot de chances activado”. Desde ahí corre solo.

## Probar en tu PC
```bash
pip install -r requirements.txt
python tests/test_bot.py        # pruebas sin internet
python scraper.py               # muestra lo que lee de la página
set TELEGRAM_TOKEN=...  &  set TELEGRAM_CHAT_ID=...   (Windows)
python main.py --prueba         # mensaje de prueba a Telegram
```

## Notas
- GitHub puede retrasar las ejecuciones programadas entre 5 y 20 min en horas pico.
- Si la página cambia de formato, `main.py` termina con error y GitHub te avisa por correo;
  el ajuste se hace en `scraper.py` (función `parsear`).
- Para cambiar el horario, edita las líneas `cron` de `.github/workflows/monitor.yml`
  (están en hora UTC = Colombia + 5 h).
