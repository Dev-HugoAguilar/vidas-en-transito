from pathlib import Path
ruta = Path("index.html")
h = ruta.read_text(encoding="utf-8")

viejo = "  const W = 1080, H = 780, PAD = 36;"
nuevo = "  const W = 1080;\n  let H = 780;\n  const PAD = 36;"
assert viejo in h
h = h.replace(viejo, nuevo)

viejo2 = """    if (!medir()) return;
    preparar(pais, (svg.clientWidth || W) < 560);"""
nuevo2 = """    if (!medir()) return;
    /* En pantallas estrechas el lienzo es más alto: el mapa gana altura en vez
       de quedar reducido a una franja. */
    const angosta = (svg.clientWidth || W) < 560;
    H = angosta ? 1040 : 780;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    preparar(pais, angosta);"""
assert viejo2 in h
h = h.replace(viejo2, nuevo2)

ruta.write_text(h, encoding="utf-8")
print("alto adaptativo añadido")
