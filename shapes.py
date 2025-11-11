# shapes.py
# Mini-librería de figuras para displayio (CircuitPython) sin adafruit_display_shapes.
# Devuelve TileGrids listos para agregar a tu Group.

import displayio

# ---------- Utils de paleta y bitmap ----------

def _make_palette(fill=None, outline=None, transparent_bg=True):
    """
    Crea una Palette adecuada según fill/outline.
    Index 0 = fondo (puede ser transparente),
    Index 1 = fill (si existe),
    Index 2 = outline (si existe).
    """
    n = 1
    if fill is not None:
        n = 2
    if outline is not None and fill is not None:
        n = 3
    elif outline is not None and fill is None:
        n = 2

    pal = displayio.Palette(n)
    # Fondo
    pal[0] = 0x000000
    if transparent_bg:
        try:
            pal.make_transparent(0)
        except AttributeError:
            # Algunos puertos no tienen make_transparent; el index 0 seguirá siendo color sólido.
            pass

    idx_fill = None
    idx_outline = None

    if fill is not None and outline is not None:
        pal[1] = fill
        pal[2] = outline
        idx_fill = 1
        idx_outline = 2
    elif fill is not None:
        pal[1] = fill
        idx_fill = 1
    elif outline is not None:
        pal[1] = outline
        idx_outline = 1

    return pal, idx_fill, idx_outline


def _new_bitmap(w, h, colors):
    if w <= 0: w = 1
    if h <= 0: h = 1
    return displayio.Bitmap(w, h, colors)


def _pset(bmp, x, y, color_index):
    if 0 <= x < bmp.width and 0 <= y < bmp.height:
        bmp[x, y] = color_index


# ---------- Figuras básicas ----------

def rect(x, y, w, h, fill=None, outline=None, stroke=1, transparent_bg=True):
    """
    Rectángulo. Si 'fill' es None, no rellena. Si 'outline' es None, no dibuja borde.
    stroke >=1 para grosor de borde.
    """
    pal, idx_fill, idx_outline = _make_palette(fill, outline, transparent_bg)
    colors = len(pal)
    bmp = _new_bitmap(w, h, colors)

    # Relleno
    if idx_fill is not None:
        for yy in range(h):
            for xx in range(w):
                bmp[xx, yy] = idx_fill

    # Borde
    if idx_outline is not None and stroke > 0:
        s = stroke
        # top
        for yy in range(min(s, h)):
            for xx in range(w):
                bmp[xx, yy] = idx_outline
        # bottom
        for yy in range(h - s, h):
            if yy < 0: continue
            for xx in range(w):
                bmp[xx, yy] = idx_outline
        # left
        for xx in range(min(s, w)):
            for yy in range(h):
                bmp[xx, yy] = idx_outline
        # right
        for xx in range(w - s, w):
            if xx < 0: continue
            for yy in range(h):
                bmp[xx, yy] = idx_outline

    return displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)


def hline(x, y, length, color, transparent_bg=True):
    """Línea horizontal de 1 px de grosor."""
    pal, _, idx_outline = _make_palette(None, color, transparent_bg)
    bmp = _new_bitmap(max(1, length), 1, len(pal))
    for xx in range(max(1, length)):
        bmp[xx, 0] = idx_outline
    return displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)


def vline(x, y, length, color, transparent_bg=True):
    """Línea vertical de 1 px de grosor."""
    pal, _, idx_outline = _make_palette(None, color, transparent_bg)
    bmp = _new_bitmap(1, max(1, length), len(pal))
    for yy in range(max(1, length)):
        bmp[0, yy] = idx_outline
    return displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)


def line(x0, y0, x1, y1, color, thickness=1, transparent_bg=True):
    """Línea con Bresenham. thickness >=1."""
    # Bounding box del segmento para crear el bitmap pequeño
    minx = min(x0, x1)
    miny = min(y0, y1)
    maxx = max(x0, x1)
    maxy = max(y0, y1)
    w = max(1, maxx - minx + 1 + (thickness - 1))
    h = max(1, maxy - miny + 1 + (thickness - 1))

    pal, _, idx_outline = _make_palette(None, color, transparent_bg)
    bmp = _new_bitmap(w, h, len(pal))

    # Normaliza coords al bitmap local
    x0l = x0 - minx
    y0l = y0 - miny
    x1l = x1 - minx
    y1l = y1 - miny

    # Bresenham
    dx = abs(x1l - x0l)
    dy = -abs(y1l - y0l)
    sx = 1 if x0l < x1l else -1
    sy = 1 if y0l < y1l else -1
    err = dx + dy
    x, y = x0l, y0l

    while True:
        # grosor: pintamos un cuadradito thickness x thickness alrededor
        r = thickness // 2
        for yy in range(y - r, y - r + thickness):
            for xx in range(x - r, x - r + thickness):
                _pset(bmp, xx, yy, idx_outline)
        if x == x1l and y == y1l:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy

    return displayio.TileGrid(bmp, pixel_shader=pal, x=minx, y=miny)


# ---------- Círculo / Elipse ----------

def circle(xc, yc, r, fill=None, outline=None, stroke=1, transparent_bg=True):
    """
    Círculo de radio r. fill/outline como en rect. stroke para el grosor del borde.
    El TileGrid se alinea con el bounding box del círculo.
    """
    d = r * 2 + 1
    pal, idx_fill, idx_outline = _make_palette(fill, outline, transparent_bg)
    bmp = _new_bitmap(d, d, len(pal))

    # Relleno: scanlines
    if idx_fill is not None:
        for y in range(-r, r + 1):
            # x_max = floor(sqrt(r^2 - y^2))
            # Aproximación sin sqrt: iremos marcando con círculo de puntos y luego rellenamos entre extremos.
            pass  # lo hacemos después de dibujar el contorno para conocer límites

    # Algoritmo midpoint para contorno
    if idx_outline is not None:
        x = r
        y = 0
        err = 1 - r
        def plot8(cx, cy, px, py, col):
            _pset(bmp, cx + px, cy + py, col)
            _pset(bmp, cx + py, cy + px, col)
            _pset(bmp, cx - py, cy + px, col)
            _pset(bmp, cx - px, cy + py, col)
            _pset(bmp, cx - px, cy - py, col)
            _pset(bmp, cx - py, cy - px, col)
            _pset(bmp, cx + py, cy - px, col)
            _pset(bmp, cx + px, cy - py, col)

        while x >= y:
            # grosor: dibuja anillos de 0..stroke-1
            for s in range(stroke):
                plot8(r, r, x - s, y, idx_outline)
                plot8(r, r, y, x - s, idx_outline)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x + 1)

    # Relleno: usa scanline entre los puntos extremos del contorno por fila
    if idx_fill is not None:
        for yy in range(d):
            # Busca primer y último píxel "sólido" del círculo en esta fila,
            # si no hay contorno, rellena por ecuación.
            left = None
            right = None
            for xx in range(d):
                if bmp[xx, yy] != 0:  # contorno ya pintado
                    left = xx
                    break
            for xx in range(d - 1, -1, -1):
                if bmp[xx, yy] != 0:
                    right = xx
                    break
            if left is None or right is None:
                # no hay contorno; rellenamos por ecuación del círculo
                dy = yy - r
                # x_max ≈ int((r*r - dy*dy) ** 0.5)
                # Evitar float costoso: igual sirve
                import math
                x_max = int((r * r - dy * dy) ** 0.5) if (r * r - dy * dy) >= 0 else -1
                if x_max >= 0:
                    for xx in range(r - x_max, r + x_max + 1):
                        bmp[xx, yy] = idx_fill
            else:
                for xx in range(left, right + 1):
                    # Solo pisa fondo (0) para no tapar el borde si existe
                    if bmp[xx, yy] == 0:
                        bmp[xx, yy] = idx_fill

    return displayio.TileGrid(bmp, pixel_shader=pal, x=xc - r, y=yc - r)


def ellipse(xc, yc, rx, ry, fill=None, outline=None, stroke=1, transparent_bg=True):
    """
    Elipse centrada en (xc,yc) con radios rx, ry. Similar a circle().
    """
    w = rx * 2 + 1
    h = ry * 2 + 1
    pal, idx_fill, idx_outline = _make_palette(fill, outline, transparent_bg)
    bmp = _new_bitmap(w, h, len(pal))

    # Contorno por punto-por-punto con ecuación (x^2/rx^2 + y^2/ry^2 ~ 1)
    # No es el algoritmo más rápido, pero es simple y suficiente en micro.
    import math
    def on_edge(x, y):
        # Cerca de la frontera
        val = ((x * x) / (rx * rx + 1e-9)) + ((y * y) / (ry * ry + 1e-9))
        return 0.98 <= val <= 1.02  # banda fina de tolerancia

    if idx_outline is not None:
        for yy in range(-ry, ry + 1):
            for xx in range(-rx, rx + 1):
                if on_edge(xx, yy):
                    # stroke: ensancha unos píxeles radiales
                    for s in range(stroke):
                        _pset(bmp, rx + xx, ry + yy, idx_outline)

    if idx_fill is not None:
        for yy in range(-ry, ry + 1):
            # Calcula span horizontal
            # x_max ~ rx * sqrt(1 - (yy^2/ry^2))
            frac = 1.0 - (yy * yy) / float(ry * ry + 1e-9)
            if frac < 0:
                continue
            x_max = int(rx * (frac ** 0.5))
            for xx in range(-x_max, x_max + 1):
                if bmp[rx + xx, ry + yy] == 0:
                    bmp[rx + xx, ry + yy] = idx_fill

    return displayio.TileGrid(bmp, pixel_shader=pal, x=xc - rx, y=yc - ry)


# ---------- Triángulo ----------

def triangle(x0, y0, x1, y1, x2, y2, fill=None, outline=None, transparent_bg=True):
    """
    Triángulo lleno por scanline. Outline simple sobre el mismo bitmap.
    """
    # Bounding box
    minx = min(x0, x1, x2)
    miny = min(y0, y1, y2)
    maxx = max(x0, x1, x2)
    maxy = max(y0, y1, y2)

    pal, idx_fill, idx_outline = _make_palette(fill, outline, transparent_bg)
    bmp = _new_bitmap(max(1, maxx - minx + 1), max(1, maxy - miny + 1), len(pal))

    # Normaliza a coords locales
    x0 -= minx; y0 -= miny
    x1 -= minx; y1 -= miny
    x2 -= minx; y2 -= miny

    # Relleno con scanline
    if idx_fill is not None:
        # Ordena por y
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts

        def edge_interpolate(y, xa, ya, xb, yb):
            if ya == yb:
                return xa
            t = (y - ya) / float(yb - ya)
            return int(xa + t * (xb - xa))

        for y in range(y0, y2 + 1):
            if y < y1:
                xl = edge_interpolate(y, x0, y0, x1, y1)
                xr = edge_interpolate(y, x0, y0, x2, y2)
            else:
                xl = edge_interpolate(y, x1, y1, x2, y2)
                xr = edge_interpolate(y, x0, y0, x2, y2)
            if xl > xr:
                xl, xr = xr, xl
            for x in range(xl, xr + 1):
                bmp[x, y] = idx_fill

    # Outline (Bresenham sobre el mismo bmp)
    if idx_outline is not None:
        def draw_line(xx0, yy0, xx1, yy1):
            dx = abs(xx1 - xx0)
            dy = -abs(yy1 - yy0)
            sx = 1 if xx0 < xx1 else -1
            sy = 1 if yy0 < yy1 else -1
            err = dx + dy
            x, y = xx0, yy0
            while True:
                _pset(bmp, x, y, idx_outline)
                if x == xx1 and y == yy1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x += sx
                if e2 <= dx:
                    err += dx
                    y += sy

        draw_line(x0, y0, x1, y1)
        draw_line(x1, y1, x2, y2)
        draw_line(x2, y2, x0, y0)

    return displayio.TileGrid(bmp, pixel_shader=pal, x=minx, y=miny)


# ---------- Rounded Rect ----------

def rounded_rect(x, y, w, h, r, fill=None, outline=None, stroke=1, transparent_bg=True):
    """
    Rectángulo con esquinas redondeadas. r = radio de la esquina.
    """
    if r < 1:
        return rect(x, y, w, h, fill=fill, outline=outline, stroke=stroke, transparent_bg=transparent_bg)

    pal, idx_fill, idx_outline = _make_palette(fill, outline, transparent_bg)
    bmp = _new_bitmap(w, h, len(pal))

    # Centro (rectángulo sin las esquinas)
    if idx_fill is not None:
        # zona central horizontal
        for yy in range(r, h - r):
            for xx in range(w):
                bmp[xx, yy] = idx_fill
        # tapas superior e inferior (rectas)
        for yy in range(r):
            for xx in range(r, w - r):
                bmp[xx, yy] = idx_fill
        for yy in range(h - r, h):
            for xx in range(r, w - r):
                bmp[xx, yy] = idx_fill

    # Esquinas redondeadas: cuadrantes de un círculo
    def paint_corner(cx, cy, rr, fill_idx):
        import math
        for yy in range(-rr, rr + 1):
            for xx in range(-rr, rr + 1):
                if xx * xx + yy * yy <= rr * rr:
                    X = cx + xx
                    Y = cy + yy
                    if 0 <= X < w and 0 <= Y < h and fill_idx is not None:
                        # Solo pisa fondo
                        if bmp[X, Y] == 0:
                            bmp[X, Y] = fill_idx

    if idx_fill is not None:
        # top-left
        paint_corner(r, r, r, idx_fill)
        # top-right
        paint_corner(w - r - 1, r, r, idx_fill)
        # bottom-left
        paint_corner(r, h - r - 1, r, idx_fill)
        # bottom-right
        paint_corner(w - r - 1, h - r - 1, r, idx_fill)

    # Outline: usa rect + círculos huecos
    if idx_outline is not None and stroke > 0:
        # bordes rectos
        s = stroke
        # top horizontal
        for yy in range(min(s, h)):
            for xx in range(r, w - r):
                bmp[xx, yy] = idx_outline
        # bottom horizontal
        for yy in range(h - s, h):
            for xx in range(r, w - r):
                bmp[xx, yy] = idx_outline
        # left vertical
        for xx in range(min(s, w)):
            for yy in range(r, h - r):
                bmp[xx, yy] = idx_outline
        # right vertical
        for xx in range(w - s, w):
            for yy in range(r, h - r):
                bmp[xx, yy] = idx_outline

        # esquinas: dibuja circunferencia de radio r en los cuatro cuadrantes
        def plot_ring(cx, cy):
            # midpoint simple
            rr = r
            x = rr
            y = 0
            err = 1 - rr
            def plot8(px, py):
                _pset(bmp, cx + px, cy + py, idx_outline)
                _pset(bmp, cx + py, cy + px, idx_outline)
                _pset(bmp, cx - py, cy + px, idx_outline)
                _pset(bmp, cx - px, cy + py, idx_outline)
                _pset(bmp, cx - px, cy - py, idx_outline)
                _pset(bmp, cx - py, cy - px, idx_outline)
                _pset(bmp, cx + py, cy - px, idx_outline)
                _pset(bmp, cx + px, cy - py, idx_outline)

            while x >= y:
                for st in range(stroke):
                    plot8(x - st, y)
                    plot8(y, x - st)
                y += 1
                if err < 0:
                    err += 2 * y + 1
                else:
                    x -= 1
                    err += 2 * (y - x + 1)

        # top-left
        plot_ring(r, r)
        # top-right
        plot_ring(w - r - 1, r)
        # bottom-left
        plot_ring(r, h - r - 1)
        # bottom-right
        plot_ring(w - r - 1, h - r - 1)

    return displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)

