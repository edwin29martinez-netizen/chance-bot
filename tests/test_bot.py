"""Pruebas sin internet: python -m pytest tests  (o python tests/test_bot.py)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import scraper, analisis, main

HTML = """
<html><body>
<h3>Chances</h3><p>Resultados de hoy</p>
<div class="r"><h3><a href="/cafeterito-tarde">Cafeterito Tarde</a></h3>
 <p>24 Noviembre 2026</p><div><span>4</span><span>4</span><span>2</span><span>8</span><span class="q">5</span></div></div>
<div class="r"><h3><a href="/culona-noche">Culona Noche</a></h3>
 <p>23 Noviembre 2026</p><div><span>7</span> <span>2</span> <span>7</span> <span>9</span></div><a>Ver más</a></div>
<div class="r"><h3><a href="/astro-luna">Astro Luna</a></h3>
 <p>23 de noviembre de 2026</p><div><span>5</span><span>7</span><span>1</span><span>0</span> <span>(Libra)</span></div></div>
<div class="r"><h3><a href="/pick-3-noche">Pick 3 Noche</a></h3>
 <p>23 Noviembre 2026</p><div><span>3</span><span>6</span><span>6</span></div></div>
<div class="r"><h3><a href="/caribena-dia">Caribeña Día</a></h3>
 <p>23 Noviembre 2026</p><div><span>9</span><span>5</span><span>5</span><span>6</span><span>1</span></div></div>
<h3>Loterías</h3><p>Boyacá</p>
</body></html>"""

def test_parser():
    rs = {r.sorteo: r for r in scraper.parsear(HTML)}
    assert set(rs) == {"Cafeterito Tarde", "Culona Noche", "Astro Luna", "Caribeña Día"}, rs
    assert rs["Cafeterito Tarde"].numero == "4428" and rs["Cafeterito Tarde"].quinta == "5"
    assert rs["Culona Noche"].numero == "7279" and rs["Culona Noche"].quinta is None
    assert rs["Astro Luna"].numero == "5710" and rs["Astro Luna"].signo == "Libra"
    assert rs["Caribeña Día"].fecha == "2026-11-23"

def test_analisis_y_mensaje():
    import random
    rnd = random.Random(1)
    hist = [{"sorteo": "Dorado Noche", "fecha": f"2026-10-{(i%28)+1:02d}",
             "numero": f"{rnd.randint(0,9999):04d}"} for i in range(60)]
    a = analisis.combinaciones(hist, "Dorado Noche", semilla="x")
    assert len(a["frecuente"]) == 4 and len(a["ponderadas"]) == 3
    msg = main.formatear({"sorteo": "Dorado Noche", "fecha": "2026-11-23",
                          "numero": "2952", "quinta": "6"}, a)
    print(msg)
    assert "2952" in msg

if __name__ == "__main__":
    test_parser(); test_analisis_y_mensaje(); print("OK")
