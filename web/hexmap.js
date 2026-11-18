/* Mapa hexagonal de «Muertes documentadas» · Vidas en tránsito
 *
 * Pieza principal de la vista: una malla de hexágonos sobre México,
 * Centroamérica y la frontera sur de EE. UU. Cada celda suma registros de la
 * OIM (Missing Migrants Project) con coordenadas dentro del encuadre. Los modos
 * «Muertes» y «Desapariciones» usan subconjuntos distintos de la misma base y
 * nunca se suman entre sí; el agregado del EAAF se muestra aparte, sin mapa.
 *
 * La geometría de las celdas la produce preparar_hexbin.py; el cliente solo
 * pinta y agrega por periodo. No hay peticiones fuera del sitio.
 */
(function () {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const RAD = Math.PI / 180;
  const ENC = { lon0: -118.5, lon1: -76.5, lat0: 6.5, lat1: 33.5 };
  const VISTA = { ancho: 1200, alto: 820, margen: 24 };

  const merc = (lat) => Math.log(Math.tan(Math.PI / 4 + (Math.max(-85, Math.min(85, lat)) * RAD) / 2));
  const k = Math.min(
    (VISTA.ancho - VISTA.margen * 2) / ((ENC.lon1 - ENC.lon0) * RAD),
    (VISTA.alto - VISTA.margen * 2) / (merc(ENC.lat1) - merc(ENC.lat0)),
  );
  const x0 = VISTA.margen + ((VISTA.ancho - VISTA.margen * 2) - (ENC.lon1 - ENC.lon0) * RAD * k) / 2;
  const y0 = VISTA.margen + ((VISTA.alto - VISTA.margen * 2) - (merc(ENC.lat1) - merc(ENC.lat0)) * k) / 2;
  const px = (lon) => x0 + (lon - ENC.lon0) * RAD * k;
  const py = (lat) => y0 + (merc(ENC.lat1) - merc(lat)) * k;

  const fmt = new Intl.NumberFormat('es-MX');
  const ENLACE_ICIJ = 'https://www.icij.org/inside-icij/2024/04/from-chiapas-to-tamaulipas-new-database-maps-thousands-of-migrants-dangerous-journeys-through-mexico-in-trailer-trucks/';
  const plural = (n, uno, varios) => `${fmt.format(n)} ${n === 1 ? uno : varios}`;

  function unidadDe() {
    if (estado.fuente === 'icij') {
      return { uno: 'fila de incidentes documentados', varios: 'filas de incidentes documentados', corto: 'filas' };
    }
    if (estado.modo === 'muertes') {
      return estado.medida === 'incidentes'
        ? { uno: 'incidente documentado', varios: 'incidentes documentados', corto: 'incidentes' }
        : { uno: 'muerte reportada', varios: 'muertes reportadas', corto: 'muertes' };
    }
    return estado.medida === 'incidentes'
      ? { uno: 'incidente con personas desaparecidas', varios: 'incidentes con personas desaparecidas', corto: 'incidentes' }
      : { uno: 'persona desaparecida reportada', varios: 'personas desaparecidas reportadas', corto: 'desaparecidas' };
  }
  const conUnidad = (n) => {
    const u = unidadDe();
    return `${fmt.format(n)} ${n === 1 ? u.uno : u.varios}`;
  };
  const RAMPA_MMP = ['#f8d7e0', '#f2b0c1', '#e47f9a', '#cc4f6c', '#a92b45', '#7c1b31'];
  const RAMPA_ICIJ = ['#fde7d6', '#f9c79f', '#f2a05f', '#e97b36', '#d45f1f', '#a84312'];
  const rampaActual = () => (estado.fuente === 'icij' ? RAMPA_ICIJ : RAMPA_MMP);
  const MEDIDAS = {
    muertes: [
      { id: 'incidentes', etiqueta: 'Incidentes documentados', unidad: 'incidentes' },
      { id: 'personas', etiqueta: 'Muertes reportadas', unidad: 'muertes' },
    ],
    desapariciones: [
      { id: 'incidentes', etiqueta: 'Incidentes con personas desaparecidas', unidad: 'incidentes' },
      { id: 'personas', etiqueta: 'Personas desaparecidas reportadas', unidad: 'personas' },
    ],
  };

  const $ = (id) => document.getElementById(id);
  const el = (tag, attrs) => {
    const nodo = document.createElementNS(NS, tag);
    for (const [clave, valor] of Object.entries(attrs || {})) nodo.setAttribute(clave, valor);
    return nodo;
  };

  let svg;
  let medidaSel, periodoSel, fuenteSel, fuenteCampo, zoomNivel, tip, vacio, fichaTitulo, ficha, cerrar, resumen, leyenda, capasCaja, eaafPanel, eaafCaja, tablaCaja, tablaPuntos, nota, titulo, subtitulo;
  let datos = null;
  const estado = {
    modo: 'muertes',
    medida: 'incidentes',
    anio: '',
    fuente: 'mmp',
    zoom: 1,
    seleccion: null,
    capas: { corredor: true, icij: true, ferro: true, inm: true, limites: true },
  };
  const grupos = {};
  let celdasGeo = null;
  let icijCeldas = new Map();
  let maxActual = 1;
  let cortes = [];
  let pan = { x: 0, y: 0 };
  let arrastre = null;
  let suprimirClick = false;

  const cargar = (ruta) => fetch(ruta, { cache: 'no-store' }).then((r) => {
    if (!r.ok) throw new Error(`${r.status} ${ruta}`);
    return r.json();
  });

  /* ---------------------------------------------------------- valores */
  const enCelda = (p) => (estado.modo === 'muertes' ? p.m : p.d) || [0, 0];
  const enAnio = (p, anio) => (p.y && p.y[anio]) || null;

  function valorDe(p) {
    if (!p) return 0;
    if (estado.fuente === 'icij') {
      const celda = icijCeldas.get(p.i);
      if (!celda) return 0;
      return estado.anio ? (celda.porAnio[estado.anio] || 0) : celda.filas;
    }
    const [n, personas] = enCelda(p);
    const campo = estado.medida === 'incidentes' ? 0 : 1;
    if (!estado.anio) return campo === 0 ? n : personas;
    const anio = enAnio(p, estado.anio);
    if (!anio) return 0;
    if (estado.modo === 'muertes') return campo === 0 ? anio[0] : anio[1];
    return campo === 0 ? anio[2] : anio[3];
  }

  function totalesVisibles() {
    let celdas = 0, incidentes = 0, personas = 0, filas = 0;
    if (!datos) return { celdas, incidentes, personas, filas };
    if (estado.fuente === 'icij') {
      for (const [, celda] of icijCeldas) {
        const valor = estado.anio ? (celda.porAnio[estado.anio] || 0) : celda.filas;
        if (valor) celdas += 1;
        filas += valor;
      }
      return { celdas, incidentes: 0, personas: 0, filas };
    }
    for (const f of datos.celdas.features) {
      const p = f.properties;
      const [n, per] = enCelda(p);
      let nv = n, pv = per;
      if (estado.anio) {
        const anio = enAnio(p, estado.anio);
        if (estado.modo === 'muertes') {
          nv = anio ? anio[0] : 0;
          pv = anio ? anio[1] : 0;
        } else {
          nv = anio ? anio[2] : 0;
          pv = anio ? anio[3] : 0;
        }
      }
      if (nv || pv) celdas += 1;
      incidentes += nv;
      personas += pv;
    }
    return { celdas, incidentes, personas, filas };
  }

  function colorDe(valor) {
    if (!valor) return '#ffffff';
    let indice = 0;
    while (indice < cortes.length && valor > cortes[indice]) indice += 1;
    return rampaActual()[Math.min(rampaActual().length - 1, indice)];
  }

  /* ---------------------------------------------------------- pintura */
  function textoPais(nombre) {
    const etiquetas = { 'Estados Unidos': 'ESTADOS UNIDOS', 'México': 'MÉXICO', 'Guatemala': 'GUATEMALA', 'Belice': 'BELICE', 'Honduras': 'HONDURAS', 'El Salvador': 'EL SALVADOR', 'Nicaragua': 'NICARAGUA', 'Costa Rica': 'COSTA RICA', 'Panamá': 'PANAMÁ', 'Cuba': 'CUBA', 'Jamaica': 'JAMAICA', 'Bahamas': 'BAHAMAS' };
    return etiquetas[nombre] || nombre.toUpperCase();
  }

  const ETIQUETAS = [
    ['ESTADOS UNIDOS', -101.5, 31.6], ['MÉXICO', -102.5, 24.2], ['CUBA', -79, 21.7],
    ['GUATEMALA', -90.4, 15.9], ['HONDURAS', -86.15, 15.45], ['EL SALVADOR', -89.3, 13.05],
    ['NICARAGUA', -84.95, 13.25], ['COSTA RICA', -84.85, 9.8], ['PANAMÁ', -80.35, 7.95],
  ];

  function centroCelda(f) {
    const anillo = f.geometry.coordinates[0];
    let sx = 0, sy = 0;
    for (const [x, y] of anillo) { sx += x; sy += y; }
    return [sx / anillo.length, sy / anillo.length];
  }

  function indexarICIJ(puntos, meta) {
    const mapa = new Map();
    const W = meta.ancho_centros || Math.sqrt(3) * meta.radio;
    const PASO = meta.paso_vertical || 1.5 * meta.radio;
    const margen = meta.vista ? meta.vista.margen : VISTA.margen;
    const centroDe = new Map(datos.celdas.features.map((f) => [f.properties.i, centroCelda(f)]));
    for (const p of puntos || []) {
      if (typeof p.lat !== 'number' || typeof p.lon !== 'number') continue;
      const x = px(p.lon), y = py(p.lat);
      let fila = Math.round((y - margen) / PASO);
      let col = Math.round((x - margen - (fila % 2) * W / 2) / W);
      let id = `h${fila}-${col}`;
      if (!centroDe.has(id)) {
        let mejor = null, distancia = Infinity;
        for (const [clave, [cx, cy]] of centroDe) {
          const d = (cx - x) ** 2 + (cy - y) ** 2;
          if (d < distancia) { distancia = d; mejor = clave; }
        }
        id = mejor || id;
      }
      let celda = mapa.get(id);
      if (!celda) {
        celda = { filas: 0, porAnio: {}, estados: new Set(), precisiones: new Set(), fechas: [] };
        mapa.set(id, celda);
      }
      celda.filas += 1;
      const anio = String(p.year || (p.date || '').slice(0, 4));
      if (anio) celda.porAnio[anio] = (celda.porAnio[anio] || 0) + 1;
      if (p.state) celda.estados.add(p.state);
      if (p.precision) celda.precisiones.add(p.precision);
      if (p.date) celda.fechas.push(p.date);
    }
    return mapa;
  }

  function rutaDe(coleccion) {
    const partes = coleccion.type === 'Polygon' ? [coleccion.coordinates] : coleccion.coordinates;
    return partes
      .map((poligono) => poligono.map((anillo) => anillo.map((r, i) => `${i ? 'L' : 'M'}${px(r[0]).toFixed(1)},${py(r[1]).toFixed(1)}`).join(' ')).join(' '))
      .join(' ');
  }

  function pintar() {
    if (!svg || !datos) return;
    svg.innerHTML = '';
    const zoom = el('g', { class: 'hx-lienzo' });
    svg.appendChild(zoom);
    grupos.zoom = zoom;

    /* fondo de tierra: blanco, subordinado a todo lo demás */
    const base = el('g', { class: 'hx-base' });
    zoom.appendChild(base);
    for (const f of datos.paises.features) {
      base.appendChild(el('path', { d: rutaDe(f.geometry), class: 'hx-pais' }));
    }

    /* zonas INM debajo de los registros */
    const gInm = el('g', { class: 'hx-inm-g' });
    zoom.appendChild(gInm);
    grupos.inm = gInm;

    const gHex = el('g', { class: 'hx-hex-g' });
    zoom.appendChild(gHex);
    grupos.hex = gHex;

    /* fronteras y divisiones por encima del relleno, finas y subordinadas */
    const gBordes = el('g', { class: 'hx-bordes' });
    zoom.appendChild(gBordes);
    grupos.limites = gBordes;
    for (const f of datos.paises.features) {
      gBordes.appendChild(el('path', { d: rutaDe(f.geometry), class: 'hx-frontera' }));
    }
    const estadosG = el('g', { class: 'hx-estados' });
    gBordes.appendChild(estadosG);
    for (const f of datos.estados.features) {
      estadosG.appendChild(el('path', { d: rutaDe(f.geometry), class: 'hx-estado' }));
    }

    const gCorredor = el('g', { class: 'hx-corredor-g' });
    zoom.appendChild(gCorredor);
    grupos.corredor = gCorredor;
    const gFerro = el('g', { class: 'hx-ferro-g' });
    zoom.appendChild(gFerro);
    grupos.ferro = gFerro;
    const gTexto = el('g', { class: 'hx-texto' });
    zoom.appendChild(gTexto);

    /* hexágonos */
    const valores = datos.celdas.features.map((f) => valorDe(f.properties)).filter((v) => v > 0).sort((a, b) => a - b);
    maxActual = valores.length ? valores[valores.length - 1] : 1;
    const cuantil = (p) => (valores.length ? valores[Math.min(valores.length - 1, Math.floor(p * valores.length))] : 0);
    cortes = [cuantil(0.2), cuantil(0.4), cuantil(0.6), cuantil(0.8)];
    for (const f of datos.celdas.features) {
      const p = f.properties;
      const valor = valorDe(p);
      const nodo = el('path', {
        d: f.geometry.coordinates[0].map((r, i) => `${i ? 'L' : 'M'}${r[0]},${r[1]}`).join(' ') + ' Z',
        class: 'hx-hex' + (valor ? ' hx-hex-dato' : ''),
        fill: colorDe(valor),
        'data-celda': p.i,
        'data-valor': valor,
      });
      if (valor) {
        nodo.setAttribute('tabindex', '0');
        nodo.setAttribute('role', 'button');
        nodo.setAttribute('aria-pressed', 'false');
        nodo.setAttribute('aria-label', `${conUnidad(valor)} en la celda ${p.i}. Abre la ficha.`);
        nodo.addEventListener('pointerenter', (ev) => mostrarTip(ev, p, valor));
        nodo.addEventListener('pointermove', (ev) => moverTip(ev));
        nodo.addEventListener('pointerleave', ocultarTip);
        nodo.addEventListener('focus', () => {
          const caja = nodo.getBoundingClientRect();
          mostrarTip({ clientX: caja.left + caja.width / 2, clientY: caja.top }, p, valor);
        });
        nodo.addEventListener('blur', ocultarTip);
        nodo.addEventListener('click', () => { if (!suprimirClick) seleccionar(p, valor); });
        nodo.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter' || ev.key === ' ') {
            ev.preventDefault();
            seleccionar(p, valor);
          }
        });
      } else {
        nodo.addEventListener('pointerenter', (ev) => mostrarTipVacio(ev, p));
        nodo.addEventListener('pointermove', (ev) => moverTip(ev));
        nodo.addEventListener('pointerleave', ocultarTip);
        nodo.addEventListener('focus', () => {
          const caja = nodo.getBoundingClientRect();
          mostrarTipVacio({ clientX: caja.left + caja.width / 2, clientY: caja.top }, p);
        });
        nodo.addEventListener('blur', ocultarTip);
        nodo.addEventListener('click', () => { if (!suprimirClick) seleccionarVacio(p); });
      }
      gHex.appendChild(nodo);
    }

    /* zonas INM */
    if (datos.inm) {
      for (const f of datos.inm.features) {
        const nodo = el('path', { d: rutaDe(f.geometry), class: 'hx-inm' });
        nodo.appendChild(el('title')).textContent = `${f.properties.estado} · entidad mencionada por el INM en 2023`;
        gInm.appendChild(nodo);
      }
    }

    /* corredor OIM (arcos como en la vista Panorama) */
    if (datos.corredor) {
      for (const f of datos.corredor.features) {
        const [a, b] = f.geometry.coordinates;
        const x1 = px(a[0]), y1 = py(a[1]), x2 = px(b[0]), y2 = py(b[1]);
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - 26;
        gCorredor.appendChild(el('path', {
          d: `M${x1.toFixed(1)},${y1.toFixed(1)} Q${mx.toFixed(1)},${my.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)}`,
          class: 'hx-corredor',
        }));
      }
      for (const c of datos.corredor.centros || []) {
        const cx = px(c.lon), cy = py(c.lat);
        gCorredor.appendChild(el('circle', { cx: cx.toFixed(1), cy: cy.toFixed(1), r: 3.4, class: 'hx-corredor-nodo' }));
      }
    }

    /* red ferroviaria */
    if (datos.ferro) {
      datos.ferro.features.forEach((f, indice) => {
        const lineas = f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates;
        const d = lineas.map((l) => l.map((r, i) => `${i ? 'L' : 'M'}${px(r[0]).toFixed(1)},${py(r[1]).toFixed(1)}`).join(' ')).join(' ');
        const p = f.properties || {};
        const ferromex = p.operador === 'Ferromex';
        const sinUso = p.condicion === 'Sin uso';
        const nodo = el('path', {
          d,
          class: 'hx-ferro' + (ferromex ? ' hx-ferromex' : '') + (sinUso ? ' hx-sin-uso' : ''),
          'data-ferro': String(indice),
        });
        nodo.appendChild(el('title')).textContent = `${p.via || p.linea || 'Tramo'} · ${p.operador || 'operador no declarado'} · ARTF`;
        nodo.addEventListener('click', (ev) => {
          ev.stopPropagation();
          if (!suprimirClick) seleccionarFerro(indice);
        });
        gFerro.appendChild(nodo);
      });
    }

    /* etiquetas */
    for (const [nombre, lon, lat] of ETIQUETAS) {
      if (lon < ENC.lon0 || lon > ENC.lon1) continue;
      gTexto.appendChild(Object.assign(el('text', {
        x: px(lon).toFixed(1), y: py(lat).toFixed(1), class: 'hx-etiqueta',
      }), { textContent: nombre }));
    }

    aplicarCapas();
    aplicarZoom();
    pintarLeyenda();
    pintarResumen();
    actualizarTitulo();
  }

  function aplicarCapas() {
    if (!grupos.hex) return;
    grupos.hex.style.display = estado.fuente === 'eaaf' ? 'none' : '';
    grupos.inm.style.display = estado.capas.inm ? '' : 'none';
    grupos.corredor.style.display = estado.capas.corredor ? '' : 'none';
    grupos.ferro.style.display = estado.capas.ferro ? '' : 'none';
    grupos.limites.style.display = estado.capas.limites ? '' : 'none';
  }

  function limitesPan() {
    const extra = Math.max(0, (VISTA.ancho * estado.zoom - VISTA.ancho) / 2) + VISTA.ancho * 0.22;
    return { x: extra, y: extra * 0.7 };
  }

  function aplicarZoom() {
    if (!grupos.zoom) return;
    const escala = estado.zoom;
    const limite = limitesPan();
    pan.x = Math.max(-limite.x, Math.min(limite.x, pan.x));
    pan.y = Math.max(-limite.y, Math.min(limite.y, pan.y));
    const tx = VISTA.ancho / 2 - (VISTA.ancho / 2) * escala + pan.x;
    const ty = VISTA.alto / 2 - (VISTA.alto / 2) * escala + pan.y;
    grupos.zoom.setAttribute('transform', `translate(${tx.toFixed(2)} ${ty.toFixed(2)}) scale(${escala.toFixed(3)})`);
    if (zoomNivel) zoomNivel.textContent = `${Math.round(escala * 100)} %`;
    $('hxZoomOut').disabled = escala <= 1;
    $('hxZoomIn').disabled = escala >= 3.2;
  }

  /* -------------------------------------------------------------- tip */
  function rangoFechas(fechas) {
    if (!fechas.length) return 'Sin dato';
    const orden = [...fechas].sort();
    return orden[0] === orden[orden.length - 1] ? orden[0] : `${orden[0]} — ${orden[orden.length - 1]}`;
  }

  const fechasCelda = (celda) => (estado.anio ? celda.fechas.filter((f) => String(f).startsWith(estado.anio)) : celda.fechas);

  function mostrarTipICIJ(ev, p) {
    if (!tip) return;
    const celda = icijCeldas.get(p.i);
    if (!celda) { mostrarTipVacio(ev, p); return; }
    const valor = estado.anio ? (celda.porAnio[estado.anio] || 0) : celda.filas;
    tip.innerHTML = `<b>${plural(valor, 'fila de incidentes documentados', 'filas de incidentes documentados')}</b> en esta celda`
      + `<span class="hx-tip-fila">ICIJ/CLIP · ${estado.anio ? `año ${estado.anio}` : '2018–2023'}</span>`
      + `<span class="hx-tip-fila">Fechas: ${rangoFechas(fechasCelda(celda))} · Entidades: ${[...celda.estados].join(', ') || 'Sin dato'}</span>`
      + `<span class="hx-tip-fila hx-tip-limite">Una celda agrega filas geolocalizadas; no es la ubicación exacta de cada caso ni una ruta, y no se suma con MMP.</span>`;
    tip.hidden = false;
    moverTip(ev);
  }

  function mostrarTip(ev, p, valor) {
    if (!tip) return;
    if (estado.fuente === 'icij') { mostrarTipICIJ(ev, p); return; }
    const [n, personas] = enCelda(p);
    const valorMedida = estado.medida === 'incidentes' ? n : personas;
    const anio = estado.anio ? enAnio(p, estado.anio) : null;
    const enPeriodo = estado.anio
      ? (estado.modo === 'muertes' ? (anio ? (estado.medida === 'incidentes' ? anio[0] : anio[1]) : 0) : (anio ? (estado.medida === 'incidentes' ? anio[2] : anio[3]) : 0))
      : valorMedida;
    const rango = p.f ? `${p.f[0]} — ${p.f[1]}` : 'sin fecha declarada';
    tip.innerHTML = `<b>${conUnidad(enPeriodo)}</b> en esta celda`
      + `<span class="hx-tip-fila">${estado.modo === 'muertes' ? 'Muertes documentadas' : 'Desapariciones documentadas'} · ${estado.anio ? `año ${estado.anio}` : 'todos los años'}</span>`
      + `<span class="hx-tip-fila">OIM MMP · fechas reportadas ${rango}</span>`
      + `<span class="hx-tip-fila">${plural(n, 'incidente', 'incidentes')} · ${estado.modo === 'muertes' ? plural(personas, 'muerte reportada', 'muertes reportadas') : plural(personas, 'persona desaparecida reportada', 'personas desaparecidas reportadas')} en la celda (todos los años)</span>`
      + `<span class="hx-tip-fila hx-tip-limite">Una celda agrupa registros georreferenciados; no es la ubicación exacta de cada incidente ni una ruta.</span>`;
    tip.hidden = false;
    moverTip(ev);
  }

  function mostrarTipVacio(ev, p) {
    if (!tip) return;
    tip.innerHTML = `<b>Sin registros en esta celda</b>`
      + `<span class="hx-tip-fila">La fuente no registra filas geolocalizadas aquí${estado.anio ? ` en ${estado.anio}` : ''}.</span>`
      + `<span class="hx-tip-fila hx-tip-limite">No significa que no haya habido muertes o desapariciones.</span>`;
    tip.hidden = false;
    moverTip(ev);
  }

  function moverTip(ev) {
    if (!tip || tip.hidden) return;
    const caja = svg.parentElement.getBoundingClientRect();
    const ancho = tip.offsetWidth || 230;
    const x = Math.min(ev.clientX - caja.left + 14, caja.width - ancho - 8);
    const y = Math.max(8, ev.clientY - caja.top - 18);
    tip.style.left = `${Math.max(8, x)}px`;
    tip.style.top = `${y}px`;
  }

  function ocultarTip() {
    if (tip) tip.hidden = true;
  }

  /* --------------------------------------------------------- selección */
  function seleccionarICIJ(p) {
    const celda = icijCeldas.get(p.i);
    if (!celda) { seleccionarVacio(p); return; }
    estado.seleccion = p.i;
    svg.querySelectorAll('.hx-hex').forEach((n) => {
      const activo = n.getAttribute('data-celda') === p.i;
      n.classList.toggle('hx-hex-activo', activo);
      if (n.hasAttribute('aria-pressed')) n.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
    svg.querySelectorAll('.hx-ferro-activo').forEach((n) => n.classList.remove('hx-ferro-activo'));
    const valor = estado.anio ? (celda.porAnio[estado.anio] || 0) : celda.filas;
    fichaTitulo.textContent = 'Celda ICIJ/CLIP';
    ficha.innerHTML = `
      <p class="hx-ficha-cifra">${fmt.format(valor)} <span>${valor === 1 ? 'fila de incidentes documentados' : 'filas de incidentes documentados'}</span></p>
      <dl class="hx-datos">
        <dt>Fuente</dt><dd><a href="${ENLACE_ICIJ}" target="_blank" rel="noopener noreferrer">ICIJ/CLIP · base sobre transporte en camiones ↗</a> · 2018–2023.</dd>
        <dt>Período</dt><dd>${estado.anio ? `Año ${estado.anio} (fecha de reporte)` : 'Todos los años con registros (2018–2023)'}</dd>
        <dt>Fechas de las filas</dt><dd>${rangoFechas(fechasCelda(celda))}</dd>
        <dt>Entidades</dt><dd>${[...celda.estados].join(', ') || 'Sin dato'}</dd>
        <dt>Precisión declarada</dt><dd>${[...celda.precisiones].join(', ') || 'Sin dato'}</dd>
        <dt>Unidad</dt><dd>Filas de incidentes documentados; no son personas.</dd>
      </dl>
      <p class="hx-limite">Una celda agrupa filas geolocalizadas: no es la ubicación exacta de cada caso ni una ruta. Es una fuente separada de OIM/MMP y sus cifras no se suman.</p>`;
    cerrar.hidden = false;
  }

  function seleccionar(p, valor) {
    if (!p) return;
    if (estado.fuente === 'icij') { seleccionarICIJ(p); return; }
    estado.seleccion = p.i;
    svg.querySelectorAll('.hx-ferro-activo').forEach((n) => n.classList.remove('hx-ferro-activo'));
    const nodos = svg.querySelectorAll('.hx-hex');
    nodos.forEach((n) => {
      const activo = n.getAttribute('data-celda') === p.i;
      n.classList.toggle('hx-hex-activo', activo);
      n.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
    const u = unidadDe();
    const [n, personas] = enCelda(p);
    const anio = estado.anio ? enAnio(p, estado.anio) : null;
    const enPeriodo = estado.anio
      ? (estado.modo === 'muertes' ? (anio ? (estado.medida === 'incidentes' ? anio[0] : anio[1]) : 0) : (anio ? (estado.medida === 'incidentes' ? anio[2] : anio[3]) : 0))
      : valor;
    const paises = (p.p || []).join(', ') || 'no declarado';
    const rutas = (p.r || []).join(', ') || 'no declarada';
    const calidad = (p.q || []).join(', ') || 'no declarada';
    fichaTitulo.textContent = `Celda ${p.i}`;
    ficha.innerHTML = `
      <p class="hx-ficha-cifra">${fmt.format(enPeriodo)} <span>${enPeriodo === 1 ? u.uno : u.varios}</span></p>
      <dl class="hx-datos">
        <dt>Modo</dt><dd>${estado.modo === 'muertes' ? 'Muertes documentadas' : 'Desapariciones documentadas'}${estado.anio ? ` · año ${estado.anio}` : ' · todos los años'}</dd>
        <dt>Incidentes (todos los años)</dt><dd>${fmt.format(n)}</dd>
        <dt>${estado.modo === 'muertes' ? 'Muertes reportadas' : 'Personas desaparecidas'} (todos los años)</dt><dd>${fmt.format(personas)}</dd>
        <dt>Fechas de reporte</dt><dd>${p.f ? `${p.f[0]} — ${p.f[1]}` : 'sin fecha declarada'}</dd>
        <dt>Países</dt><dd>${paises}</dd>
        <dt>Rutas MMP</dt><dd>${rutas}</dd>
        <dt>Calidad de fuente</dt><dd>${calidad} (código MMP)</dd>
        <dt>Fuente</dt><dd>OIM Missing Migrants Project · CC BY-IGO · descarga ${datos.meta.fuente.descargado}</dd>
        <dt>Precisión</dt><dd>La fuente publica coordenadas por incidente, no una precisión declarada por fila; la celda agrupa registros.</dd>
      </dl>
      <p class="hx-limite">${estado.modo === 'muertes' ? 'Un incidente puede corresponder a varias muertes reportadas: el conteo de incidentes no es el de personas.' : 'Son personas reportadas como desaparecidas en MMP; no es el total de desapariciones ni se suma con el agregado del EAAF.'} Una celda no prueba una ruta ni una causalidad.</p>`;
    cerrar.hidden = false;
  }

  function seleccionarVacio(p) {
    estado.seleccion = p.i;
    svg.querySelectorAll('.hx-hex').forEach((n) => {
      const activo = n.getAttribute('data-celda') === p.i;
      n.classList.toggle('hx-hex-activo', activo);
      if (n.hasAttribute('aria-pressed')) n.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
    fichaTitulo.textContent = 'Celda sin registros';
    ficha.innerHTML = `<p class="hx-vacio-ficha">Esta celda no tiene ${estado.fuente === 'icij' ? 'filas ICIJ/CLIP' : 'registros MMP'} geolocalizados${estado.anio ? ` en ${estado.anio}` : ''}. La ausencia de registros no significa que no haya habido muertes o desapariciones: la fuente solo documenta lo que registra.</p>`;
    cerrar.hidden = false;
  }

  const campo = (v) => (v === null || v === undefined || v === '' ? 'Sin dato' : v);

  function seleccionarFerro(indice) {
    const f = datos.ferro && datos.ferro.features[indice];
    if (!f) return;
    estado.seleccion = `ferro:${indice}`;
    svg.querySelectorAll('.hx-hex').forEach((n) => {
      n.classList.remove('hx-hex-activo');
      if (n.hasAttribute('aria-pressed')) n.setAttribute('aria-pressed', 'false');
    });
    svg.querySelectorAll('.hx-ferro-activo').forEach((n) => n.classList.remove('hx-ferro-activo'));
    const nodo = svg.querySelector(`.hx-ferro[data-ferro="${indice}"]`);
    if (nodo) nodo.classList.add('hx-ferro-activo');
    const p = f.properties || {};
    const ferromex = p.operador === 'Ferromex';
    fichaTitulo.textContent = 'Tramo ferroviario';
    ficha.innerHTML = `
      <p><b>${p.via || p.linea || 'Tramo sin nombre'}</b>${p.entidad ? ` · ${p.entidad}` : ''}</p>
      <dl class="hx-datos">
        <dt>Operador</dt><dd>${p.operador || 'no declarado'}</dd>
        <dt>Color en el mapa</dt><dd>${ferromex ? 'Morado oscuro (Ferromex)' : 'Morado claro (otra red)'}</dd>
        <dt>Tipo de vía</dt><dd>${p.tipo || 'no declarado'}</dd>
        <dt>Estado operativo</dt><dd>${p.condicion || 'no declarado'}</dd>
        <dt>Servicio</dt><dd>${p.servicio || 'no declarado'}</dd>
        <dt>Longitud declarada</dt><dd>${p.long_km ? `${fmt.format(p.long_km)} km` : 'Sin dato'}</dd>
        <dt>Actualización</dt><dd>${p.fecha || 'Sin dato'}</dd>
        <dt>Precisión</dt><dd>${p.precision || 'Sin dato'}</dd>
        <dt>Fuente</dt><dd><a href="https://services6.arcgis.com/ZP95JslokqLi5f3i/arcgis/rest/services/V%C3%ADas_ferroviarias/FeatureServer/0" target="_blank" rel="noopener noreferrer">ARTF · IDE · Vías ferroviarias ↗</a></dd>
        <dt>Licencia</dt><dd>CC BY 4.0</dd>
      </dl>
      <p class="hx-limite">Infraestructura física: no demuestra uso migrante ni relación con los registros MMP o los incidentes ICIJ/CLIP.</p>`;
    cerrar.hidden = false;
  }

  function pintarTablaPuntos() {
    if (!tablaPuntos || !datos) return;
    const filas = datos.icij.points.map((p) => `<tr><th scope="row">${p.date}</th><td>${p.state || '—'}</td><td>${p.precision || '—'}</td><td>${p.migrants === null || p.migrants === undefined ? '—' : fmt.format(p.migrants)}</td><td>${p.deaths === null || p.deaths === undefined ? '—' : fmt.format(p.deaths)}</td><td>${typeof p.lat === 'number' ? `${p.lat.toFixed(3)}, ${p.lon.toFixed(3)}` : '—'}</td></tr>`);
    tablaPuntos.innerHTML = `<table class="hx-tabla"><caption>${fmt.format(datos.icij.points.length)} filas ICIJ/CLIP con coordenadas · 2018–2023 · unidad: fila de incidente, no persona</caption>`
      + '<thead><tr><th scope="col">Fecha</th><th scope="col">Entidad</th><th scope="col">Precisión</th><th scope="col">Migrantes</th><th scope="col">Muertes</th><th scope="col">Coordenada</th></tr></thead>'
      + `<tbody>${filas.join('')}</tbody></table>`;
  }

  function cerrarFicha() {
    estado.seleccion = null;
    svg.querySelectorAll('.hx-hex').forEach((n) => {
      n.classList.remove('hx-hex-activo');
      if (n.hasAttribute('aria-pressed')) n.setAttribute('aria-pressed', 'false');
    });
    svg.querySelectorAll('.hx-ferro-activo').forEach((n) => n.classList.remove('hx-ferro-activo'));
    fichaTitulo.textContent = 'Selección';
    ficha.innerHTML = '<p class="hx-vacio-ficha">Selecciona una celda del hexbin o un tramo ferroviario para ver su ficha.</p>';
    cerrar.hidden = true;
  }
  /* ----------------------------------------------------------- resumen */
  function pintarResumen() {
    if (!datos || !resumen) return;
    if (estado.fuente === 'icij') {
      const t = totalesVisibles();
      resumen.innerHTML = `
        <p class="hx-resumen-titulo">ICIJ/CLIP · filas de incidentes documentados</p>
        <p class="hx-resumen-cifra">${fmt.format(t.filas)} <span>${t.filas === 1 ? 'fila' : 'filas'}</span> · ${fmt.format(t.celdas)} celdas</p>
        <p class="hx-resumen-linea">${estado.anio ? `Año ${estado.anio}` : 'Años 2018–2023'} · ${fmt.format(datos.celdas.features.length)} celdas terrestres en el encuadre.</p>
        <p class="hx-resumen-linea">Fuente: ICIJ/CLIP, base sobre transporte en camiones (filas con coordenadas). Unidad: fila de incidente documentado; no equivale a una persona ni a un incidente MMP.</p>
        <p class="hx-resumen-alerta">Las cifras ICIJ/CLIP no se suman ni se comparan como un total común con OIM/MMP: son fuentes distintas, con unidades y metodologías distintas.</p>`;
      if (eaafPanel) eaafPanel.hidden = true;
      return;
    }
    if (estado.fuente === 'eaaf') {
      resumen.innerHTML = `
        <p class="hx-resumen-titulo">EAAF · agregado publicado, sin geometría</p>
        <p class="hx-resumen-cifra">${fmt.format(datos.eaaf.length)} <span>conceptos agregados</span></p>
        <p class="hx-resumen-linea">El EAAF publica agregados por corredor, sin coordenadas por caso: no se dibuja en el mapa ni se desglosa por celda.</p>
        <p class="hx-resumen-alerta">Otra fuente, otro corte y otra unidad. Sus cifras no se suman con OIM/MMP; están en el panel lateral, separadas del mapa.</p>`;
      if (eaafPanel) eaafPanel.hidden = estado.modo !== 'desapariciones';
      if (estado.modo === 'desapariciones') pintarEaaf();
      return;
    }
    const t = totalesVisibles();
    const u = unidadDe();
    const filas = [];
    filas.push(`<p class="hx-resumen-titulo">${estado.modo === 'muertes' ? 'Muertes documentadas' : 'Desapariciones documentadas'} · ${u.varios}</p>`);
    const cifraInc = `${fmt.format(t.incidentes)} <span>${t.incidentes === 1 ? 'incidente' : 'incidentes'}</span>`;
    const cifraPer = `${fmt.format(t.personas)} <span>${estado.modo === 'muertes' ? 'muertes reportadas' : 'desaparecidas'}</span>`;
    filas.push(`<p class="hx-resumen-cifra">${estado.medida === 'incidentes' ? `${cifraInc} · ${cifraPer}` : `${cifraPer} · ${cifraInc}`}</p>`);
    filas.push(`<p class="hx-resumen-linea">${fmt.format(t.celdas)} celdas con registro${estado.anio ? ` en ${estado.anio}` : ' en 2014–2026'} · ${fmt.format(datos.celdas.features.length)} celdas terrestres.</p>`);
    filas.push(`<p class="hx-resumen-linea">Fuente: OIM Missing Migrants Project (${datos.meta.fuente.licencia}). Filas del corredor con coordenadas en el encuadre: ${fmt.format(datos.meta.exclusiones.seleccionadas)}; sin celda terrestre cercana: ${fmt.format(datos.meta.resumen.registros_sin_celda)}.</p>`);
    if (estado.modo === 'desapariciones') {
      filas.push(`<p class="hx-resumen-alerta">El agregado del EAAF se muestra aparte: otra fuente, otro corte y otra unidad; no se suma con el mapa.</p>`);
    }
    resumen.innerHTML = filas.join('');
    if (eaafPanel) eaafPanel.hidden = estado.modo !== 'desapariciones';
    if (estado.modo === 'desapariciones') pintarEaaf();
  }

  function pintarEaaf() {
    if (!eaafCaja || !datos.eaaf) return;
    const filas = datos.eaaf.map((a) => `<li><span>${a.concepto}</span><b>${fmt.format(Number(a.valor))}</b> <small>${a.unidad || ''}</small><em>corte ${a.corte}</em></li>`).join('');
    eaafCaja.innerHTML = `<p class="hx-resumen-linea">EAAF · Proyecto Frontera, agregado publicado. Sin coordenadas por caso: no se dibuja ni se desglosa por celda.</p><ul class="hx-eaaf">${filas}</ul>`;
  }

  function pintarLeyenda() {
    if (!leyenda) return;
    if (estado.fuente === 'eaaf') {
      leyenda.innerHTML = `
        <div class="hx-leyenda-titulo">EAAF · agregado publicado, sin mapa</div>
        <p class="hx-leyenda-nota">El EAAF publica agregados por corredor, sin coordenadas por caso. No hay celdas que colorear: sus cifras están en el panel lateral y no se suman con OIM/MMP.</p>`;
      return;
    }
    const u = unidadDe();
    const rampa = rampaActual();
    const pasos = rampa.map((c, i) => {
      const desde = (i / rampa.length) * 100;
      const hasta = ((i + 1) / rampa.length) * 100;
      return `${c} ${desde}% ${hasta}%`;
    }).join(', ');
    const esICIJ = estado.fuente === 'icij';
    const notaDato = esICIJ
      ? 'Celdas con filas ICIJ/CLIP: el tono indica el número de filas'
      : 'Celdas con registros MMP: el tono indica la cifra (' + u.corto + ')';
    const notaVacia = esICIJ
      ? 'Celda sin filas ICIJ/CLIP geolocalizadas: no equivale a ausencia'
      : 'Celda MMP sin registros de la fuente: no equivale a ausencia';
    const claves = [
      `<li><i class="hx-muestra hx-muestra-dato" style="background:${rampa[4]}"></i>${notaDato}</li>`,
      `<li><i class="hx-muestra hx-muestra-vacia"></i>${notaVacia}</li>`,
      '<li><i class="hx-muestra hx-muestra-corredor"></i>Corredor OIM · generalizado, no GPS ni recorrido individual</li>',
      '<li><i class="hx-muestra hx-muestra-ferro"></i>Tramos ferroviarios · Ferromex en morado oscuro</li>',
      '<li><i class="hx-muestra hx-muestra-ferro-claro"></i>Tramos ferroviarios · otras redes en morado claro</li>',
      '<li><i class="hx-muestra hx-muestra-inm"></i>Zonas INM 2023 · cobertura estatal reportada, no ubicación precisa</li>',
      '<li><i class="hx-muestra hx-muestra-estado"></i>División estatal</li>',
    ];
    leyenda.innerHTML = `
      <div class="hx-leyenda-titulo">${esICIJ ? 'Filas de incidentes documentados ICIJ/CLIP' : (estado.modo === 'muertes' ? 'Muertes documentadas' : 'Desapariciones documentadas')} · ${esICIJ ? 'filas por celda' : `${u.corto} por celda`}</div>
      <div class="hx-gradiente" style="background:linear-gradient(90deg, ${pasos})"></div>
      <div class="hx-ticks"><span>1</span><span>${fmt.format(cortes[2] || 1)}</span><span>${fmt.format(maxActual)}</span></div>
      <ul class="hx-claves">${claves.join('')}</ul>
      ${esICIJ ? '<p class="hx-leyenda-nota">Fuente ICIJ/CLIP activa: los hexágonos muestran solo filas de esta fuente. No se suman con OIM/MMP.</p>' : '<p class="hx-leyenda-nota">Fuente OIM/MMP activa: los hexágonos muestran solo registros MMP. ICIJ/CLIP se consulta cambiando la fuente.</p>'}`;
  }

  function actualizarTitulo() {
    if (!datos) return;
    if (estado.fuente === 'eaaf') {
      titulo.textContent = 'EAAF · agregado publicado, sin geometría';
      subtitulo.textContent = 'El EAAF publica agregados por corredor, sin coordenadas por caso: no se dibuja en el mapa. Es otra fuente, con otro corte y otra unidad; sus cifras no se suman con OIM/MMP.';
      svg.setAttribute('aria-label', `Mapa hexagonal. ${subtitulo.textContent}`);
      return;
    }
    const t = totalesVisibles();
    if (estado.fuente === 'icij') {
      const periodo = estado.anio || '2018–2023';
      titulo.textContent = `${plural(t.filas, 'fila de incidentes documentados', 'filas de incidentes documentados')} en ${fmt.format(t.celdas)} celdas`;
      subtitulo.textContent = `ICIJ/CLIP · base sobre transporte en camiones, ${periodo}. Cada hexágono agrupa filas geolocalizadas de esta fuente; no es la ubicación exacta de cada caso ni una ruta. Unidad: fila de incidente documentado, no persona. No se suma con OIM/MMP.`;
      svg.setAttribute('aria-label', `Mapa hexagonal. ${subtitulo.textContent}`);
      return;
    }
    const periodo = estado.anio || '2014–2026';
    const cifra = estado.medida === 'incidentes' ? t.incidentes : t.personas;
    titulo.textContent = `${conUnidad(cifra)} en ${fmt.format(t.celdas)} celdas del corredor`;
    subtitulo.textContent = `Filas de ${estado.modo === 'muertes' ? 'muertes documentadas' : 'desapariciones documentadas'} con fecha de reporte entre ${periodo}. Cada hexágono suma registros de la OIM (MMP) con coordenadas dentro del encuadre; no es la ubicación exacta de cada caso ni una ruta.`;
    svg.setAttribute('aria-label', `Mapa hexagonal. ${subtitulo.textContent}`);
  }

  /* ------------------------------------------------------------ tabla */
  function pintarTabla() {
    if (!tablaCaja || !datos) return;
    if (estado.fuente === 'eaaf') {
      tablaCaja.innerHTML = '<p class="hx-vacio-ficha">El EAAF publica agregados por corredor, sin coordenadas por caso: no hay tabla por celda. Sus cifras están en el panel lateral, separadas del mapa y de OIM/MMP.</p>';
      return;
    }
    if (estado.fuente === 'icij') { pintarTablaICIJ(); return; }
    const filas = [];
    let sumaInc = 0, sumaPer = 0;
    const u = unidadDe();
    for (const f of datos.celdas.features) {
      const p = f.properties;
      const valor = valorDe(p);
      if (!valor) continue;
      const [n, per] = enCelda(p);
      const anio = estado.anio ? enAnio(p, estado.anio) : null;
      const nv = estado.anio ? (anio ? (estado.modo === 'muertes' ? anio[0] : anio[2]) : 0) : n;
      const pv = estado.anio ? (anio ? (estado.modo === 'muertes' ? anio[1] : anio[3]) : 0) : per;
      sumaInc += nv;
      sumaPer += pv;
      filas.push({ valor, html: `<tr><th scope="row">${p.i}</th><td>${fmt.format(valor)}</td><td>${u.corto}</td><td>${fmt.format(nv)} inc. · ${fmt.format(pv)} pers.</td><td>${p.f ? `${p.f[0]} — ${p.f[1]}` : '—'}</td><td>${(p.p || []).slice(0, 2).join(', ') || '—'}</td></tr>` });
    }
    filas.sort((a, b) => b.valor - a.valor);
    tablaCaja.innerHTML = `<table class="hx-tabla"><caption>${fmt.format(filas.length)} celdas con dato · suma ${fmt.format(sumaInc)} incidentes · ${fmt.format(sumaPer)} ${estado.modo === 'muertes' ? 'muertes reportadas' : 'personas desaparecidas reportadas'} · ${estado.anio ? `año ${estado.anio}` : 'todos los años'} · medida: ${u.corto}</caption>`
      + '<thead><tr><th scope="col">Celda</th><th scope="col">Valor</th><th scope="col">Unidad</th><th scope="col">Incidentes · personas</th><th scope="col">Fechas de reporte</th><th scope="col">Países</th></tr></thead>'
      + `<tbody>${filas.map((f) => f.html).join('')}</tbody></table>`;
  }

  function pintarTablaICIJ() {
    const filas = [];
    let suma = 0;
    for (const [id, celda] of icijCeldas) {
      const valor = estado.anio ? (celda.porAnio[estado.anio] || 0) : celda.filas;
      if (!valor) continue;
      suma += valor;
      filas.push({ valor, html: `<tr><th scope="row">${id}</th><td>${fmt.format(valor)}</td><td>filas</td><td>${rangoFechas(fechasCelda(celda))}</td><td>${[...celda.estados].join(', ') || '—'}</td></tr>` });
    }
    filas.sort((a, b) => b.valor - a.valor);
    tablaCaja.innerHTML = `<table class="hx-tabla"><caption>${fmt.format(filas.length)} celdas con filas ICIJ/CLIP · suma ${fmt.format(suma)} filas de incidentes documentados · ${estado.anio ? `año ${estado.anio}` : 'todos los años'} · unidad: fila de incidente, no persona · no se suma con MMP</caption>`
      + '<thead><tr><th scope="col">Celda</th><th scope="col">Filas</th><th scope="col">Unidad</th><th scope="col">Fechas</th><th scope="col">Entidades</th></tr></thead>'
      + `<tbody>${filas.map((f) => f.html).join('')}</tbody></table>`;
  }

  /* --------------------------------------------------------- controles */
  function construirControles() {
    const esICIJ = estado.fuente === 'icij';
    const esEAAF = estado.fuente === 'eaaf';
    if (esICIJ) {
      estado.medida = 'filas';
      medidaSel.innerHTML = '<option value="filas">Filas de incidentes documentados</option>';
      medidaSel.value = 'filas';
      medidaSel.disabled = true;
    } else {
      const medidas = MEDIDAS[estado.modo];
      if (!medidas.some((m) => m.id === estado.medida)) estado.medida = 'incidentes';
      medidaSel.innerHTML = medidas.map((m) => `<option value="${m.id}">${m.etiqueta}</option>`).join('');
      medidaSel.value = estado.medida;
      medidaSel.disabled = false;
    }
    const anios = esICIJ ? aniosICIJ() : (datos.meta.resumen.anios || []);
    if (estado.anio && !anios.includes(estado.anio)) estado.anio = '';
    periodoSel.innerHTML = `<option value="">Todos los años (${anios[0]}–${anios[anios.length - 1]})</option>`
      + anios.map((a) => `<option value="${a}">${a}</option>`).join('');
    periodoSel.value = estado.anio;
    fuenteCampo.hidden = false;
    fuenteSel.innerHTML = '<option value="mmp">OIM MMP</option><option value="icij">ICIJ/CLIP · filas de incidentes</option>'
      + (estado.modo === 'desapariciones' ? '<option value="eaaf">EAAF · agregado (sin mapa)</option>' : '');
    fuenteSel.value = estado.fuente;
    for (const [id, activo] of [['hxModoMuertes', estado.modo === 'muertes'], ['hxModoDesapariciones', estado.modo === 'desapariciones']]) {
      const boton = $(id);
      if (!boton) continue;
      boton.setAttribute('aria-selected', activo ? 'true' : 'false');
      boton.disabled = esICIJ;
      boton.setAttribute('aria-disabled', esICIJ ? 'true' : 'false');
    }
    construirCapas();
  }

  function aniosICIJ() {
    const anios = new Set();
    for (const p of (datos.icij && datos.icij.points) || []) {
      const a = String(p.year || (p.date || '').slice(0, 4));
      if (/^\d{4}$/.test(a)) anios.add(a);
    }
    return [...anios].sort();
  }

  const CAPAS = [
    ['corredor', 'Corredor OIM · generalizado'],
    ['ferro', 'Red ferroviaria ARTF'],
    ['inm', 'Zonas INM 2023'],
    ['limites', 'Límites y estados'],
  ];

  function construirCapas() {
    capasCaja.innerHTML = CAPAS.map(([id, texto]) => `<label class="hx-capa"><input type="checkbox" data-capa="${id}" ${estado.capas[id] ? 'checked' : ''}> ${texto}</label>`).join('');
  }

  function ajustarEncuadre() {
    if (!svg) return;
    svg.setAttribute('preserveAspectRatio', window.innerWidth < 640 ? 'xMidYMid slice' : 'xMidYMid meet');
  }

  function reiniciarVista() {
    estado.zoom = 1;
    pan = { x: 0, y: 0 };
    aplicarZoom();
  }

  function conectarArrastre() {
    const factor = () => VISTA.ancho / (svg.getBoundingClientRect().width || VISTA.ancho);
    const punteros = new Map();
    let pinza = null;
    let pinzaActiva = false;

    const distanciaYMedio = () => {
      const [a, b] = [...punteros.values()];
      return {
        distancia: Math.hypot(a.x - b.x, a.y - b.y),
        medio: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 },
      };
    };

    svg.addEventListener('pointerdown', (ev) => {
      if (ev.button !== undefined && ev.button !== 0) return;
      punteros.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
      if (punteros.size === 2) {
        arrastre = null;
        pinzaActiva = true;
        const { distancia, medio } = distanciaYMedio();
        if (distancia > 0) pinza = { distancia, zoom: estado.zoom, medio };
        return;
      }
      if (punteros.size > 2) return;
      arrastre = { x: ev.clientX, y: ev.clientY, activo: false, id: ev.pointerId };
    });

    svg.addEventListener('pointermove', (ev) => {
      if (!punteros.has(ev.pointerId)) return;
      punteros.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });

      if (pinza && punteros.size >= 2) {
        const { distancia, medio } = distanciaYMedio();
        if (!distancia || !pinza.distancia) return;
        const nueva = Math.max(1, Math.min(3.2, pinza.zoom * (distancia / pinza.distancia)));
        if (nueva === estado.zoom) return;
        const centro = { x: VISTA.ancho / 2, y: VISTA.alto / 2 };
        const p = puntoSVG(medio);
        const cx = (p.x - centro.x - pan.x) / estado.zoom + centro.x;
        const cy = (p.y - centro.y - pan.y) / estado.zoom + centro.y;
        estado.zoom = nueva;
        pan.x = p.x - centro.x - (cx - centro.x) * nueva;
        pan.y = p.y - centro.y - (cy - centro.y) * nueva;
        aplicarZoom();
        ocultarTip();
        return;
      }

      if (!arrastre) return;
      const dx = ev.clientX - arrastre.x;
      const dy = ev.clientY - arrastre.y;
      if (!arrastre.activo && Math.hypot(dx, dy) > 7) {
        arrastre.activo = true;
        svg.setPointerCapture?.(arrastre.id);
      }
      if (!arrastre.activo) return;
      pan.x += dx * factor();
      pan.y += dy * factor();
      arrastre.x = ev.clientX;
      arrastre.y = ev.clientY;
      aplicarZoom();
      ocultarTip();
    });

    const soltar = (ev) => {
      punteros.delete(ev.pointerId);
      if (punteros.size < 2) pinza = null;
      const actual = arrastre;
      arrastre = null;
      if (pinzaActiva && punteros.size === 0) {
        pinzaActiva = false;
        suprimirClick = true;
        setTimeout(() => { suprimirClick = false; }, 120);
      } else if (actual && actual.activo) {
        suprimirClick = true;
        setTimeout(() => { suprimirClick = false; }, 80);
      }
      if (punteros.size === 1) {
        const [id, p] = [...punteros.entries()][0];
        arrastre = { x: p.x, y: p.y, activo: false, id };
      }
    };
    svg.addEventListener('pointerup', soltar);
    svg.addEventListener('pointercancel', (ev) => {
      punteros.delete(ev.pointerId);
      pinza = null;
      if (punteros.size === 0) pinzaActiva = false;
      arrastre = null;
    });
  }

  function puntoSVG(ev) {
    const sx = ev.clientX !== undefined ? ev.clientX : ev.x;
    const sy = ev.clientY !== undefined ? ev.clientY : ev.y;
    const ctm = svg.getScreenCTM && svg.getScreenCTM();
    if (ctm && svg.createSVGPoint) {
      const p = svg.createSVGPoint();
      p.x = sx;
      p.y = sy;
      const q = p.matrixTransform(ctm.inverse());
      return { x: q.x, y: q.y };
    }
    const caja = svg.getBoundingClientRect();
    return {
      x: ((sx - caja.left) / (caja.width || 1)) * VISTA.ancho,
      y: ((sy - caja.top) / (caja.height || 1)) * VISTA.alto,
    };
  }

  function conectarRueda() {
    const marco = svg.parentElement;
    if (!marco) return;
    marco.addEventListener('wheel', (ev) => {
      ev.preventDefault();
      ocultarTip();
      const delta = ev.deltaMode === 1 ? ev.deltaY * 16 : ev.deltaMode === 2 ? ev.deltaY * 400 : ev.deltaY;
      if (!delta) return;
      const factor = Math.max(0.8, Math.min(1.25, Math.exp(-delta * 0.0015)));
      const nueva = Math.max(1, Math.min(3.2, estado.zoom * factor));
      if (Math.abs(nueva - estado.zoom) < 0.0001) return;
      const centro = { x: VISTA.ancho / 2, y: VISTA.alto / 2 };
      const p = puntoSVG(ev);
      const cx = (p.x - centro.x - pan.x) / estado.zoom + centro.x;
      const cy = (p.y - centro.y - pan.y) / estado.zoom + centro.y;
      estado.zoom = nueva;
      pan.x = p.x - centro.x - (cx - centro.x) * nueva;
      pan.y = p.y - centro.y - (cy - centro.y) * nueva;
      aplicarZoom();
    }, { passive: false });
  }

  /* ------------------------------------------------------------- arranque */
  async function iniciar() {
    svg = $('hxMap');
    if (!svg) return;
    titulo = $('hxTitle');
    subtitulo = $('hxSubtitle');
    medidaSel = $('hxMedida');
    periodoSel = $('hxPeriodo');
    fuenteSel = $('hxFuente');
    fuenteCampo = $('hxFuenteCampo');
    zoomNivel = $('hxZoomNivel');
    tip = $('hxTip');
    vacio = $('hxVacio');
    fichaTitulo = $('hxFichaTitulo');
    ficha = $('hxFicha');
    cerrar = $('hxCerrar');
    resumen = $('hxResumen');
    leyenda = $('hxLeyenda');
    capasCaja = $('hxCapas');
    eaafPanel = $('hxEaafPanel');
    eaafCaja = $('hxEaaf');
    tablaCaja = $('hxTabla');
    tablaPuntos = $('hxTablaPuntos');
    nota = $('hxNota');

    try {
      const [celdas, meta, paises, estados, corredor, ferro, inm, fuentes, datosBase] = await Promise.all([
        cargar('geografia/hexbin_muertes.geojson'),
        cargar('geografia/hexbin_muertes.json'),
        cargar('geografia/paises_hex.geojson'),
        cargar('geografia/estados_mexico.geojson'),
        cargar('geografia/corredor.geojson'),
        cargar('geografia/ferroviaria.geojson'),
        cargar('geografia/evidencia_transito.geojson'),
        cargar('fuentes_ampliadas.json'),
        cargar('data.json'),
      ]);
      const eaaf = (datosBase.missing_search_aggregates || []).map((a) => ({
        concepto: a.concept, valor: a.value, unidad: a.unit, corte: a.cutoff_date, nota: a.methodology_note,
      })).filter((a) => a.concepto && a.valor);
      datos = { celdas, meta, paises, estados, corredor, ferro, inm, icij: fuentes.icij_clip, eaaf };
      icijCeldas = indexarICIJ(datos.icij && datos.icij.points, meta);
    } catch (error) {
      console.error('No se pudo cargar la malla hexagonal', error);
      if (vacio) {
        vacio.hidden = false;
        vacio.textContent = 'No se pudo cargar la malla hexagonal local.';
      }
      return;
    }

    ajustarEncuadre();
    window.addEventListener('resize', ajustarEncuadre);
    conectarArrastre();
    conectarRueda();
    construirControles();
    pintar();
    pintarTabla();
    pintarTablaPuntos();
    cerrarFicha();

    medidaSel.addEventListener('change', () => {
      estado.medida = medidaSel.value;
      estado.seleccion = null;
      pintar();
      pintarTabla();
      cerrarFicha();
    });
    periodoSel.addEventListener('change', () => {
      estado.anio = periodoSel.value;
      estado.seleccion = null;
      pintar();
      pintarTabla();
      cerrarFicha();
    });
    fuenteSel.addEventListener('change', () => {
      estado.fuente = fuenteSel.value;
      estado.anio = '';
      estado.seleccion = null;
      const esEAAF = estado.fuente === 'eaaf';
      if (vacio) {
        vacio.hidden = !esEAAF;
        if (esEAAF) vacio.textContent = 'EAAF publica agregados por corredor, sin coordenadas por caso: no se dibuja en el mapa. Las cifras están en el panel lateral, separadas del mapa.';
      }
      construirControles();
      aplicarCapas();
      pintar();
      pintarTabla();
      cerrarFicha();
    });
    capasCaja.addEventListener('change', (ev) => {
      const capa = ev.target.getAttribute('data-capa');
      if (capa) {
        estado.capas[capa] = ev.target.checked;
        aplicarCapas();
      }
    });
    cerrar.addEventListener('click', cerrarFicha);
    $('hxZoomIn').addEventListener('click', () => { estado.zoom = Math.min(3.2, estado.zoom * 1.3); aplicarZoom(); });
    $('hxZoomOut').addEventListener('click', () => { estado.zoom = Math.max(1, estado.zoom / 1.3); aplicarZoom(); });
    $('hxReset').addEventListener('click', reiniciarVista);
    svg.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape') cerrarFicha();
    });
    svg.addEventListener('pointerleave', ocultarTip);
    svg.addEventListener('pointerdown', ocultarTip);
    window.addEventListener('scroll', ocultarTip, { passive: true });
    window.addEventListener('resize', ocultarTip);
    $('hxModoMuertes').addEventListener('click', () => cambiarModo('muertes'));
    $('hxModoDesapariciones').addEventListener('click', () => cambiarModo('desapariciones'));
  }

  function cambiarModo(modo) {
    if (estado.modo === modo || estado.fuente === 'icij') return;
    estado.modo = modo;
    estado.medida = 'incidentes';
    estado.anio = '';
    estado.fuente = 'mmp';
    estado.seleccion = null;
    if (vacio) vacio.hidden = true;
    construirControles();
    pintar();
    pintarTabla();
    cerrarFicha();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
