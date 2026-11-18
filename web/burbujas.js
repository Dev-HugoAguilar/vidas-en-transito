/**
 * Burbujas empaquetadas · componente compartido de «Vidas en tránsito».
 *
 * Es el port a JavaScript sin React del componente «BurbujasEdadSexo» del Atlas
 * vial (dashboards/atlas-vial/src/ui/BurbujasEdadSexo.tsx), que es la referencia
 * visual de este tablero:
 *
 *  · empaquetado circular real con `packSiblings`/`packEnclose` de d3-hierarchy
 *    —el mismo algoritmo que usa el Atlas vial—, sin rejillas ni filas;
 *  · radio proporcional a √valor: el ÁREA, no el diámetro, es proporcional al
 *    conteo, con una sola constante k para toda la vista (búsqueda binaria hasta
 *    que el empaquetado cabe entero en la región);
 *  · círculos limpios con borde propio y la etiqueta y el valor dentro cuando
 *    caben; si no caben, el dato sigue en el tooltip y en la tabla accesible;
 *  · tooltip al pasar el cursor, al enfocar con teclado o al tocar en móvil;
 *  · selección con clic, Enter o Espacio, con `aria-pressed`, anillo de foco y un
 *    estado seleccionado explícito (el resto de burbujas se atenúa);
 *  · leyenda de tamaño (0,25 · 0,5 · 1 del máximo) y leyenda de color;
 *  · en pantallas estrechas la región baja de alto antes que recortar círculos.
 *
 * La tabla accesible NO la dibuja este archivo: el tablero la compone con su
 * helper `chartTable` a partir de las filas que `render` devuelve, de modo que
 * tooltip, burbujas y tabla no pueden discrepar.
 *
 * Empaquetado: d3-hierarchy (ISC, © Mike Bostock). Ver el aviso al final.
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------------------
   * Empaquetado circular · d3-hierarchy (packSiblings + packEnclose)
   * ---------------------------------------------------------------------- */

  var LCG_A = 1664525;
  var LCG_C = 1013904223;
  var LCG_M = 4294967296;

  function lcg() {
    var semilla = 1;
    return function () {
      semilla = (LCG_A * semilla + LCG_C) % LCG_M;
      return semilla / LCG_M;
    };
  }

  function shuffle(lista, random) {
    var m = lista.length;
    var t;
    var i;
    while (m) {
      i = (random() * m--) | 0;
      t = lista[m];
      lista[m] = lista[i];
      lista[i] = t;
    }
    return lista;
  }

  function Node(circulo) {
    this._ = circulo;
    this.next = null;
    this.previous = null;
  }

  function place(b, a, c) {
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    var d2 = dx * dx + dy * dy;
    var a2;
    var b2;
    var x;
    var y;
    if (d2) {
      a2 = a.r + c.r;
      a2 *= a2;
      b2 = b.r + c.r;
      b2 *= b2;
      if (a2 > b2) {
        x = (d2 + b2 - a2) / (2 * d2);
        y = Math.sqrt(Math.max(0, (b2 / d2) - x * x));
        c.x = b.x - x * dx - y * dy;
        c.y = b.y - x * dy + y * dx;
      } else {
        x = (d2 + a2 - b2) / (2 * d2);
        y = Math.sqrt(Math.max(0, (a2 / d2) - x * x));
        c.x = a.x + x * dx - y * dy;
        c.y = a.y + x * dy + y * dx;
      }
    } else {
      c.x = a.x + c.r;
      c.y = a.y;
    }
  }

  function intersects(a, b) {
    var dr = a.r + b.r - 1e-6;
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    return dr > 0 && dr * dr > dx * dx + dy * dy;
  }

  function score(nodo) {
    var a = nodo._;
    var b = nodo.next._;
    var ab = a.r + b.r;
    var dx = (a.x * b.r + b.x * a.r) / ab;
    var dy = (a.y * b.r + b.y * a.r) / ab;
    return dx * dx + dy * dy;
  }

  function enclosesNot(a, b) {
    var dr = a.r - b.r;
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    return dr < 0 || dr * dr < dx * dx + dy * dy;
  }

  function enclosesWeak(a, b) {
    var dr = a.r - b.r + Math.max(a.r, b.r, 1) * 1e-9;
    var dx = b.x - a.x;
    var dy = b.y - a.y;
    return dr > 0 && dr * dr > dx * dx + dy * dy;
  }

  function enclosesWeakAll(a, B) {
    for (var i = 0; i < B.length; ++i) {
      if (!enclosesWeak(a, B[i])) return false;
    }
    return true;
  }

  function encloseBasis(B) {
    switch (B.length) {
      case 1:
        return encloseBasis1(B[0]);
      case 2:
        return encloseBasis2(B[0], B[1]);
      case 3:
        return encloseBasis3(B[0], B[1], B[2]);
      default:
        return null;
    }
  }

  function encloseBasis1(a) {
    return { x: a.x, y: a.y, r: a.r };
  }

  function encloseBasis2(a, b) {
    var x21 = b.x - a.x;
    var y21 = b.y - a.y;
    var r21 = b.r - a.r;
    var l = Math.sqrt(x21 * x21 + y21 * y21);
    return {
      x: (a.x + b.x + (x21 / l) * r21) / 2,
      y: (a.y + b.y + (y21 / l) * r21) / 2,
      r: (l + a.r + b.r) / 2
    };
  }

  function encloseBasis3(a, b, c) {
    var x1 = a.x;
    var y1 = a.y;
    var r1 = a.r;
    var x2 = b.x;
    var y2 = b.y;
    var r2 = b.r;
    var x3 = c.x;
    var y3 = c.y;
    var r3 = c.r;
    var a2 = x1 - x2;
    var a3 = x1 - x3;
    var b2 = y1 - y2;
    var b3 = y1 - y3;
    var c2 = r2 - r1;
    var c3 = r3 - r1;
    var d1 = x1 * x1 + y1 * y1 - r1 * r1;
    var d2 = d1 - x2 * x2 - y2 * y2 + r2 * r2;
    var d3 = d1 - x3 * x3 - y3 * y3 + r3 * r3;
    var ab = a3 * b2 - a2 * b3;
    var xa = (b2 * d3 - b3 * d2) / (ab * 2) - x1;
    var xb = (b3 * c2 - b2 * c3) / ab;
    var ya = (a3 * d2 - a2 * d3) / (ab * 2) - y1;
    var yb = (a2 * c3 - a3 * c2) / ab;
    var A = xb * xb + yb * yb - 1;
    var B = 2 * (r1 + xa * xb + ya * yb);
    var Cc = xa * xa + ya * ya - r1 * r1;
    var r = -(Math.abs(A) > 1e-6 ? (B + Math.sqrt(B * B - 4 * A * Cc)) / (2 * A) : Cc / B);
    return { x: x1 + xa + xb * r, y: y1 + ya + yb * r, r: r };
  }

  function packEncloseRandom(circulos, random) {
    var i = 0;
    var n = (circulos = shuffle(Array.from(circulos), random)).length;
    var B = [];
    var p;
    var e;
    while (i < n) {
      p = circulos[i];
      if (e && enclosesWeak(e, p)) {
        ++i;
      } else {
        e = encloseBasis((B = extendBasis(B, p)));
        i = 0;
      }
    }
    return e;
  }

  function extendBasis(B, p) {
    var i;
    var j;
    if (enclosesWeakAll(p, B)) return [p];
    for (i = 0; i < B.length; ++i) {
      if (enclosesNot(p, B[i]) && enclosesWeakAll(encloseBasis2(B[i], p), B)) {
        return [B[i], p];
      }
    }
    for (i = 0; i < B.length - 1; ++i) {
      for (j = i + 1; j < B.length; ++j) {
        if (
          enclosesNot(encloseBasis2(B[i], B[j]), p) &&
          enclosesNot(encloseBasis2(B[i], p), B[j]) &&
          enclosesNot(encloseBasis2(B[j], p), B[i]) &&
          enclosesWeakAll(encloseBasis3(B[i], B[j], p), B)
        ) {
          return [B[i], B[j], p];
        }
      }
    }
    throw new Error('empaquetado imposible');
  }

  function packSiblingsRandom(circulos, random) {
    var n = circulos.length;
    if (!n) return 0;
    var a;
    var b;
    var c;
    var aa;
    var ca;
    var i;
    var j;
    var k;
    var sj;
    var sk;

    a = circulos[0];
    a.x = 0;
    a.y = 0;
    if (!(n > 1)) return a.r;

    b = circulos[1];
    a.x = -b.r;
    b.x = a.r;
    b.y = 0;
    if (!(n > 2)) return a.r + b.r;

    place(b, a, (c = circulos[2]));

    a = new Node(a);
    b = new Node(b);
    c = new Node(c);
    a.next = c.previous = b;
    b.next = a.previous = c;
    c.next = b.previous = a;

    pack: for (i = 3; i < n; ++i) {
      place(a._, b._, (c = circulos[i]));
      c = new Node(c);
      j = b.next;
      k = a.previous;
      sj = b._.r;
      sk = a._.r;
      do {
        if (sj <= sk) {
          if (intersects(j._, c._)) {
            b = j;
            a.next = b;
            b.previous = a;
            --i;
            continue pack;
          }
          sj += j._.r;
          j = j.next;
        } else {
          if (intersects(k._, c._)) {
            a = k;
            a.next = b;
            b.previous = a;
            --i;
            continue pack;
          }
          sk += k._.r;
          k = k.previous;
        }
      } while (j !== k.next);

      c.previous = a;
      c.next = b;
      a.next = b.previous = b = c;

      aa = score(a);
      while ((c = c.next) !== b) {
        if ((ca = score(c)) < aa) {
          a = c;
          aa = ca;
        }
      }
      b = a.next;
    }

    a = [b._];
    c = b;
    while ((c = c.next) !== b) a.push(c._);
    c = packEncloseRandom(a, random);

    for (i = 0; i < n; ++i) {
      a = circulos[i];
      a.x -= c.x;
      a.y -= c.y;
    }

    return c.r;
  }

  function packSiblings(circulos) {
    packSiblingsRandom(circulos, lcg());
    return circulos;
  }

  /* ------------------------------------------------------------------------
   * Tokens visuales · sistema del Atlas vial
   * ---------------------------------------------------------------------- */

  var COLORES = {
    /* Índigo del corredor y acento del mapa; blanco para el texto interior. */
    azul: { relleno: '#4B55FF', borde: '#2F3ECF', texto: '#FFFFFF' },
    /* Lavanda del sistema cartográfico; texto oscuro para conservar contraste AA. */
    lavanda: { relleno: '#C9C1DE', borde: '#8993A2', texto: '#28344A' },
    gris: { relleno: '#DFE3EA', borde: '#8993A2', texto: '#28344A' }
  };
  var TINTA = '#111318';
  /** Separación entre bordes de círculos (px), reservada con el radio de colisión. */
  var SEPARACION = 6;
  var ALTO_REGION = 372;
  var ALTO_REGION_ESTRECHA = 296;
  var ANCHO_ESTRECHO = 340;

  var numero = new Intl.NumberFormat('es-MX');
  var medidor = null;

  function esc(texto) {
    return String(texto == null ? '' : texto).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function porcentaje(valor, total) {
    if (!total) return null;
    return (100 * valor / total).toFixed(1).replace('.', ',') + ' %';
  }

  function anchoTexto(texto, tamano, peso) {
    if (!medidor) medidor = document.createElement('canvas').getContext('2d');
    if (!medidor) return texto.length * tamano * 0.56;
    medidor.font = (peso || 400) + ' ' + tamano + 'px Inter, system-ui, sans-serif';
    return medidor.measureText(texto).width;
  }

  /** Parte la etiqueta en como mucho `maximo` líneas; `null` si no cabe entera. */
  function partirEtiqueta(texto, maxAncho, tamano, maximo, peso) {
    var palabras = String(texto).split(/\s+/);
    var lineas = [];
    var actual = '';
    for (var i = 0; i < palabras.length; i += 1) {
      var prueba = actual ? actual + ' ' + palabras[i] : palabras[i];
      if (anchoTexto(prueba, tamano, peso) <= maxAncho || !actual) {
        actual = prueba;
      } else {
        lineas.push(actual);
        actual = palabras[i];
        if (lineas.length === maximo) break;
      }
    }
    if (lineas.length < maximo && actual) lineas.push(actual);
    if (lineas.join(' ').replace(/\s+/g, ' ').length < String(texto).replace(/\s+/g, ' ').length) {
      return null;
    }
    for (var j = 0; j < lineas.length; j += 1) {
      if (anchoTexto(lineas[j], tamano, peso) > maxAncho) return null;
    }
    return lineas;
  }

  /** Empaqueta con radio + separación/2 y devuelve los círculos visibles. */
  function empaquetar(items) {
    if (!items.length) return { circulos: [], minX: 0, minY: 0, ancho: 0, alto: 0 };
    var colision = items
      .map(function (item) {
        return { clave: item.clave, r: item.r + SEPARACION / 2 };
      })
      .sort(function (a, b) {
        return b.r - a.r || a.clave.localeCompare(b.clave);
      });
    var salida = packSiblings(colision);
    var circulos = salida.map(function (c) {
      return {
        clave: c.clave,
        x: c.x,
        y: c.y,
        r: Math.max(1, c.r - SEPARACION / 2)
      };
    });
    var minX = Math.min.apply(null, circulos.map(function (c) { return c.x - c.r; }));
    var maxX = Math.max.apply(null, circulos.map(function (c) { return c.x + c.r; }));
    var minY = Math.min.apply(null, circulos.map(function (c) { return c.y - c.r; }));
    var maxY = Math.max.apply(null, circulos.map(function (c) { return c.y + c.r; }));
    return { circulos: circulos, minX: minX, minY: minY, ancho: maxX - minX, alto: maxY - minY };
  }

  /* ------------------------------------------------------------------------
   * Componente
   * ---------------------------------------------------------------------- */

  var UNIDADES = {
    filas: { singular: 'fila', plural: 'filas', area: 'filas registradas' },
    menciones: { singular: 'mención', plural: 'menciones', area: 'menciones registradas' }
  };

  function render(contenedor, opciones) {
    if (!contenedor) return { filas: [] };
    var op = opciones || {};
    var unidad = UNIDADES[op.unidad] ? op.unidad : 'filas';
    var etiquetaUnidad = UNIDADES[unidad];
    var categorias = (op.categorias || []).filter(function (c) {
      return Number(c.valor) > 0;
    });
    if (!categorias.length) {
      contenedor.innerHTML = '<p class="bv-vacio">Sin categorías con valores para este campo.</p>';
      return { filas: [] };
    }

    var altoFijo = Number(op.altoFijo) > 0 ? Number(op.altoFijo) : 0;
    var maximo = Math.max.apply(
      null,
      categorias.map(function (c) { return Number(c.valor); })
    );
    var denominador = Number(op.denominador) > 0 ? Number(op.denominador) : null;
    var denominadorTexto = op.denominadorTexto || etiquetaUnidad.plural + ' del campo';
    var suma = categorias.reduce(function (total, c) { return total + Number(c.valor); }, 0);

    var compartir = function (valor) {
      return denominador ? porcentaje(valor, denominador) : null;
    };

    function notaDe(categoria) {
      if (categoria.agrupacion) {
        return 'Agrupa ' + (categoria.categorias || '') + ' categorías del campo: no es un valor del archivo.';
      }
      if (unidad === 'menciones') return 'Una fila puede registrar varias categorías.';
      return null;
    }

    var leyendaColor = op.colores || [{ tipo: 'azul', texto: 'Categoría del campo' }];

    /* --- estructura ---------------------------------------------------- */
    contenedor.innerHTML =
      '<div class="bv">' +
      '<div class="bv-cuerpo">' +
      '<aside class="bv-guia">' +
      '<h4>Cómo leer la gráfica</h4>' +
      '<p><strong>Área:</strong> ' + esc(etiquetaUnidad.area) + ' por categoría. El radio crece con la raíz del conteo, así que el área es proporcional al valor.</p>' +
      '<p><strong>Color:</strong> ' + esc(op.colorTexto || 'categoría del campo') + '.</p>' +
      '<p class="bv-pista">Pasa el cursor, toca o llega con Tab a una burbuja para ver el conteo exacto. Enter o Espacio la selecciona.</p>' +
      '</aside>' +
      '<div class="bv-region">' +
      '<div class="bv-lienzo">' +
      '<svg class="bv-svg" role="img" aria-label="' + esc(op.ariaLabel || ('Burbujas de ' + (op.titulo || 'categorías'))) + '"></svg>' +
      '<div class="bv-tooltip" role="status" aria-live="polite" hidden></div>' +
      '</div>' +
      '<div class="bv-leyendas">' +
      '<div class="bv-leyenda"><span class="bv-leyenda-titulo">Área = ' + esc(etiquetaUnidad.area) + '</span>' +
      [0.25, 0.5, 1]
        .map(function (fraccion) {
          var radio = Math.max(2, Math.sqrt(fraccion) * 9);
          return (
            '<span class="bv-leyenda-item"><svg width="22" height="22" aria-hidden="true" focusable="false">' +
            '<circle cx="11" cy="11" r="' + radio.toFixed(1) + '" fill="#9AA3B2"></circle></svg>' +
            '<span>' + esc(numero.format(Math.round(maximo * fraccion))) + '</span></span>'
          );
        })
        .join('') +
      '</div>' +
      '<div class="bv-leyenda"><span class="bv-leyenda-titulo">Color</span>' +
      leyendaColor
        .map(function (item) {
          var tono = COLORES[item.tipo] || COLORES.azul;
          return (
            '<span class="bv-leyenda-item"><span class="bv-punto" style="background:' + tono.relleno + '"></span>' +
            '<span>' + esc(item.texto) + '</span></span>'
          );
        })
        .join('') +
      '</div>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<p class="bv-seleccion" role="status" hidden></p>' +
      (op.faltante ? bandaFaltante(op.faltante) : '') +
      (op.nota ? '<p class="bv-nota">' + esc(op.nota) + '</p>' : '') +
      (unidad === 'menciones' && op.notaMenciones
        ? '<p class="bv-nota">' + esc(op.notaMenciones) + '</p>'
        : '') +
      '</div>';

    function bandaFaltante(faltante) {
      var valor = Number(faltante.valor) || 0;
      var total = Number(faltante.total) || 0;
      var parte = porcentaje(valor, total);
      return (
        '<div class="bv-faltante">' +
        '<span class="bv-faltante-marca" aria-hidden="true"></span>' +
        '<span class="bv-faltante-texto"><strong>' + esc(faltante.etiqueta) + ' · ' +
        esc(numero.format(valor)) + ' ' + esc(etiquetaUnidad.plural) + '</strong>' +
        '<span>' + esc(numero.format(valor)) + ' de ' + esc(numero.format(total)) + ' ' +
        esc(faltante.totalTexto || 'filas') + (parte ? ' · ' + esc(parte) : '') +
        (faltante.nota ? ' · ' + esc(faltante.nota) : '') + '</span></span>' +
        '</div>'
      );
    }

    var lienzo = contenedor.querySelector('.bv-lienzo');
    var svg = contenedor.querySelector('.bv-svg');
    var tooltip = contenedor.querySelector('.bv-tooltip');
    var avisoSeleccion = contenedor.querySelector('.bv-seleccion');

    var estado = { sel: null, foco: null, ancho: 0, altoRegion: 0, altoLienzo: 0, nodos: {}, posiciones: {} };

    function nodo(categoria) {
      return estado.nodos[categoria.etiqueta];
    }

    function pintarEstado() {
      Object.keys(estado.nodos).forEach(function (clave) {
        var grupo = estado.nodos[clave];
        grupo.classList.toggle('is-sel', estado.sel === clave);
        grupo.classList.toggle('is-foco', estado.foco === clave && estado.sel !== clave);
        grupo.classList.toggle('is-tenue', Boolean(estado.sel) && estado.sel !== clave);
      });
      var circulos = svg.querySelectorAll('.bv-circulo');
      for (var i = 0; i < circulos.length; i += 1) {
        circulos[i].setAttribute('aria-pressed', String(circulos[i].dataset.cat === estado.sel));
      }
      var elegida = null;
      for (var j = 0; j < categorias.length; j += 1) {
        if (categorias[j].etiqueta === estado.sel) elegida = categorias[j];
      }
      if (!elegida) {
        avisoSeleccion.hidden = true;
        avisoSeleccion.textContent = '';
        return;
      }
      var parte = compartir(elegida.valor);
      avisoSeleccion.hidden = false;
      avisoSeleccion.textContent =
        'Seleccionado: ' + elegida.etiqueta + ' · ' + numero.format(elegida.valor) + ' ' +
        (Number(elegida.valor) === 1 ? etiquetaUnidad.singular : etiquetaUnidad.plural) +
        (parte ? ' · ' + parte + ' de ' + numero.format(denominador) + ' ' + denominadorTexto : '') +
        '. Enter o Espacio lo quita.';
    }

    function mostrarDetalle(categoria) {
      var posicion = estado.posiciones[categoria.etiqueta];
      if (!posicion) return;
      var parte = compartir(categoria.valor);
      var nota = notaDe(categoria);
      tooltip.innerHTML =
        '<p class="bv-tooltip-titulo">' + esc(categoria.etiqueta) + '</p>' +
        '<p class="bv-tooltip-valor">' + esc(numero.format(Number(categoria.valor) || 0)) + ' ' +
        esc(etiquetaUnidad.plural) + '</p>' +
        (parte
          ? '<p class="bv-tooltip-nota">' + esc(parte) + ' de ' + esc(numero.format(denominador)) + ' ' +
            esc(denominadorTexto) + '</p>'
          : '') +
        (nota ? '<p class="bv-tooltip-nota">' + esc(nota) + '</p>' : '');
      tooltip.hidden = false;
      var anchoCaja = 224;
      var altoCaja = 84;
      var izquierda = posicion.x + posicion.r + 10;
      if (izquierda + anchoCaja > estado.ancho - 4) izquierda = posicion.x - posicion.r - 10 - anchoCaja;
      izquierda = Math.max(4, Math.min(estado.ancho - anchoCaja - 4, izquierda));
      var arriba = Math.max(4, Math.min(estado.altoLienzo - altoCaja - 4, posicion.y - posicion.r - 6));
      tooltip.style.left = izquierda + 'px';
      tooltip.style.top = arriba + 'px';
    }

    function ocultarDetalle(categoria) {
      tooltip.hidden = true;
      tooltip.textContent = '';
      if (categoria) {
        var grupo = nodo(categoria);
        if (grupo) grupo.classList.remove('is-foco');
      }
    }

    function alternar(categoria) {
      estado.sel = estado.sel === categoria.etiqueta ? null : categoria.etiqueta;
      pintarEstado();
    }

    function dibujar() {
      var ancho = Math.round(lienzo.clientWidth || 0);
      if (!ancho) return; /* la sección está oculta: se dibuja cuando se muestre */
      var alto = altoFijo || (ancho < ANCHO_ESTRECHO ? ALTO_REGION_ESTRECHA : ALTO_REGION);
      if (estado.ancho === ancho && estado.altoRegion === alto && svg.childNodes.length) return;
      estado.ancho = ancho;
      estado.altoRegion = alto;

      /* Una sola k: la mayor con la que el empaquetado cabe entero. */
      function cabe(k) {
        var prueba = empaquetar(
          categorias.map(function (c) {
            return { clave: c.etiqueta, r: Math.sqrt(Number(c.valor)) * k };
          })
        );
        return prueba.ancho <= ancho - 16 && prueba.alto <= alto - 16;
      }
      var bajo = 0.02;
      var sube = 12;
      for (var intento = 0; intento < 30; intento += 1) {
        var medio = (bajo + sube) / 2;
        if (cabe(medio)) bajo = medio;
        else sube = medio;
      }
      var paquete = empaquetar(
        categorias.map(function (c) {
          return { clave: c.etiqueta, r: Math.sqrt(Number(c.valor)) * bajo };
        })
      );
      /* El lienzo no reserva alto de más: se ajusta al empaquetado, sin pasar del
         máximo de la región. Así los paneles con pocas categorías no dejan un
         hueco vacío debajo de las burbujas. */
      var altoUsado = altoFijo || Math.min(alto, Math.max(150, Math.round(paquete.alto + 30)));
      estado.altoLienzo = altoUsado;
      var dx = (ancho - paquete.ancho) / 2 - paquete.minX;
      var dy = (altoUsado - paquete.alto) / 2 - paquete.minY;

      svg.setAttribute('width', String(ancho));
      svg.setAttribute('height', String(altoUsado));
      svg.setAttribute('viewBox', '0 0 ' + ancho + ' ' + altoUsado);
      while (svg.firstChild) svg.removeChild(svg.firstChild);

      var porClave = {};
      var orden = paquete.circulos.slice().sort(function (a, b) {
        return a.r - b.r;
      });
      estado.nodos = {};
      estado.posiciones = {};

      orden.forEach(function (circulo) {
        var categoria = null;
        for (var i = 0; i < categorias.length; i += 1) {
          if (categorias[i].etiqueta === circulo.clave) categoria = categorias[i];
        }
        if (!categoria) return;
        var x = circulo.x + dx;
        var y = circulo.y + dy;
        var r = circulo.r;
        estado.posiciones[categoria.etiqueta] = { x: x, y: y, r: r };
        porClave[categoria.etiqueta] = categoria;

        var tono = categoria.agrupacion ? COLORES.lavanda : COLORES.azul;
        if (categoria.color && COLORES[categoria.color]) tono = COLORES[categoria.color];

        var colorTexto = tono.texto || '#ffffff';
        var NS = 'http://www.w3.org/2000/svg';
        var grupo = document.createElementNS(NS, 'g');
        grupo.setAttribute('class', 'bv-nodo');
        grupo.setAttribute('transform', 'translate(' + x.toFixed(2) + ' ' + y.toFixed(2) + ')');

        var halo = document.createElementNS(NS, 'circle');
        halo.setAttribute('class', 'bv-halo');
        halo.setAttribute('r', (r + 3.5).toFixed(2));
        grupo.appendChild(halo);

        var visual = document.createElementNS(NS, 'circle');
        visual.setAttribute('class', 'bv-circulo');
        visual.setAttribute('r', r.toFixed(2));
        visual.setAttribute('fill', tono.relleno);
        visual.setAttribute('stroke', tono.borde);
        visual.setAttribute('stroke-width', '1');
        visual.setAttribute('tabindex', '0');
        visual.setAttribute('role', 'button');
        visual.setAttribute('aria-pressed', 'false');
        visual.dataset.cat = categoria.etiqueta;
        visual.dataset.valor = String(Number(categoria.valor) || 0);
        var parte = compartir(categoria.valor);
        visual.setAttribute(
          'aria-label',
          categoria.etiqueta + ': ' + numero.format(Number(categoria.valor) || 0) + ' ' +
            etiquetaUnidad.plural + (parte ? ', ' + parte + ' de ' + numero.format(denominador) + ' ' + denominadorTexto : '')
        );
        grupo.appendChild(visual);

        /* Texto dentro del círculo: solo si cabe completo; si no, tooltip y tabla. */
        var tamanoValor = Math.max(10, Math.min(17, r * 0.4));
        var tamanoEtiqueta = Math.max(8.5, Math.min(12.5, r * 0.26));
        var valorTexto = numero.format(Number(categoria.valor) || 0);
        var cabeValor = r >= 9.5 && anchoTexto(valorTexto, tamanoValor, 600) <= r * 1.55;
        var lineas = r >= 17 ? partirEtiqueta(categoria.etiqueta, r * 1.6, tamanoEtiqueta, 2, 400) : null;
        var interlineado = tamanoEtiqueta * 1.16;
        var alturaTexto = (lineas ? lineas.length * interlineado : 0) + (cabeValor ? tamanoValor * 1.2 : 0);
        var cabeTodo = alturaTexto <= r * 1.7;
        if (!cabeTodo) {
          lineas = null;
          if (!cabeValor) {
            lineas = r >= 15 ? partirEtiqueta(categoria.etiqueta, r * 1.5, tamanoEtiqueta, 2, 400) : null;
            cabeValor = false;
          }
        }

        var desplazamiento = 0;
        if (lineas && cabeValor) desplazamiento = -tamanoValor * 0.6;
        else if (lineas) desplazamiento = 0;

        if (lineas) {
          var primero = lineas.length === 1 ? 0 : -(lineas.length - 1) / 2;
          var textoEtiqueta = document.createElementNS(NS, 'text');
          textoEtiqueta.setAttribute('class', 'bv-texto');
          textoEtiqueta.setAttribute('text-anchor', 'middle');
          textoEtiqueta.setAttribute('font-size', tamanoEtiqueta.toFixed(1));
          textoEtiqueta.setAttribute('fill', colorTexto);
          lineas.forEach(function (linea, indice) {
            var tspan = document.createElementNS(NS, 'tspan');
            tspan.setAttribute('x', '0');
            tspan.setAttribute(
              'y',
              (desplazamiento + (primero + indice) * interlineado + (cabeValor ? -tamanoValor * 0.1 : 0)).toFixed(2)
            );
            tspan.textContent = linea;
            textoEtiqueta.appendChild(tspan);
          });
          grupo.appendChild(textoEtiqueta);
        }

        if (cabeValor) {
          var textoValor = document.createElementNS(NS, 'text');
          textoValor.setAttribute('class', 'bv-texto bv-texto--valor');
          textoValor.setAttribute('text-anchor', 'middle');
          textoValor.setAttribute('font-size', tamanoValor.toFixed(1));
          textoValor.setAttribute('font-weight', '600');
          textoValor.setAttribute('fill', colorTexto);
          textoValor.setAttribute('y', (lineas ? tamanoValor * 0.85 : tamanoValor * 0.36).toFixed(2));
          textoValor.textContent = valorTexto;
          grupo.appendChild(textoValor);
        }

        visual.addEventListener('pointerenter', function () {
          estado.foco = categoria.etiqueta;
          pintarEstado();
          mostrarDetalle(categoria);
        });
        visual.addEventListener('pointerleave', function () {
          if (estado.foco === categoria.etiqueta) estado.foco = null;
          pintarEstado();
          ocultarDetalle();
        });
        visual.addEventListener('focus', function () {
          estado.foco = categoria.etiqueta;
          pintarEstado();
          mostrarDetalle(categoria);
        });
        visual.addEventListener('blur', function () {
          if (estado.foco === categoria.etiqueta) estado.foco = null;
          pintarEstado();
          ocultarDetalle();
        });
        visual.addEventListener('click', function () {
          alternar(categoria);
          if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) {
            mostrarDetalle(categoria);
            window.setTimeout(function () {
              if (!estado.foco) ocultarDetalle();
            }, 3200);
          }
        });
        visual.addEventListener('keydown', function (evento) {
          if (evento.key === 'Enter' || evento.key === ' ' || evento.key === 'Spacebar') {
            evento.preventDefault();
            alternar(categoria);
          }
        });

        estado.nodos[categoria.etiqueta] = grupo;
        svg.appendChild(grupo);
      });
    }

    svg.addEventListener('keydown', function (evento) {
      if (evento.key === 'Escape' && estado.sel) {
        estado.sel = null;
        pintarEstado();
      }
    });

    var observador = null;
    if (typeof ResizeObserver === 'function') {
      observador = new ResizeObserver(function () {
        dibujar();
      });
      observador.observe(lienzo);
    }
    /* La sección puede estar oculta al montar (display:none): el ancho es 0 y el
       dibujo espera. Al mostrarse, el ResizeObserver trae el tamaño real; este
       segundo aviso cubre el caso de navegadores sin ResizeObserver. */
    window.addEventListener('resize', dibujar);
    dibujar();

    return {
      filas: categorias.map(function (c) {
        return {
          etiqueta: c.etiqueta,
          valor: Number(c.valor),
          agrupacion: Boolean(c.agrupacion),
          categorias: c.categorias || null,
          parte: compartir(c.valor)
        };
      }),
      suma: suma,
      denominador: denominador,
      actualizar: dibujar
    };
  }

  window.BurbujasAtlas = { render: render };
})();

/* ---------------------------------------------------------------------------
 * Aviso de atribución del empaquetado
 *
 * Las funciones de empaquetado circular (`packSiblingsRandom`, `packEncloseRandom`,
 * `extendBasis`, `encloseBasis1..3`, `enclosesNot`, `enclosesWeak`, `enclosesWeakAll`,
 * `place`, `intersects`, `score`, `Node` y el generador `lcg`) son una copia literal
 * de d3-hierarchy v3 (https://github.com/d3/d3-hierarchy), © Mike Bostock,
 * publicada bajo licencia ISC:
 *
 *   Permission to use, copy, modify, and/or distribute this software for any
 *   purpose with or without fee is hereby granted, provided that the above
 *   copyright notice and this permission notice appear in all copies.
 *
 *   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 *   REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 *   AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 *   INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 *   LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 *   OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 *   PERFORMANCE OF THIS SOFTWARE.
 *
 * Se copia aquí para que el tablero siga sin dependencias externas en tiempo de
 * ejecución: el Atlas vial lo importa de `d3-hierarchy`, que es una dependencia
 * de su módulo React.
 * ------------------------------------------------------------------------- */





