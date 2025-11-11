import board
import displayio
import shapes
import terminalio
import color
from sd_manager import SDManager

sd_manager = SDManager()

# ---------------------- new file with an incremental name ----------------------
def siguiente_nombre_incremental(base="archivo", ext="txt", carpeta="/"):
    if not sd_manager.mounted:
        return f"{base} 1.{ext}"
    try:
        existentes = sd_manager.listar(carpeta)
    except Exception:
        existentes = []
    prefijo = f"{base} "
    sufijo = f".{ext}"
    max_n = 0
    for nombre in existentes:
        if not nombre.endswith(sufijo):
            continue
        if not nombre.startswith(prefijo):
            continue
        medio = nombre[len(prefijo):-len(sufijo)].strip()
        try:
            n = int(medio)
            if n > max_n:
                max_n = n
        except ValueError:
            pass
    return f"{base} {max_n + 1}.{ext}"

def crear_archivo_incremental():
    if sd_manager.mounted:
        try:
            nombre = siguiente_nombre_incremental(base="archivo", ext="txt", carpeta="/")
            contenido = "Hola, este es un archivo creado desde CircuitPython.\n"
            sd_manager.crear_archivo(nombre, contenido)
            print(f"Archivo '{nombre}' creado con éxito.")
        except Exception as e:
            print(f"Error al crear el archivo incremental: {e}")
    else:
        print("La tarjeta SD no está montada.")

# ---------------------- text with terminalio.FONT (scaled) ----------------------
FONT = terminalio.FONT
CELL_W, CELL_H = FONT.get_bounding_box()

# Cambiá esto para ajustar el tamaño del texto (1 = normal, 2 = x2, etc.)
SCALE = 2
LINE_SP = 2  # espacio extra entre líneas en píxeles (post-escala)

def make_palette(fg=color.white, bg=color.black):
    pal = displayio.Palette(2)
    pal[0] = bg
    pal[1] = fg
    return pal

def make_line(display, y_px, fg=color.white, bg=color.black, text="", x_px=0, max_width_px=None, scale=SCALE):
    """
    Crea un Group escalado con un TileGrid (1 fila) a y_px.
    Posiciona el Group con (x_px, y_px) y respeta el ancho visible según la escala.
    """
    palette = make_palette(fg, bg)

    # Ancho en píxeles disponible (restando x_px); si dan max_width_px, usarlo.
    pixels_available = (display.width - x_px) if max_width_px is None else max_width_px
    # Cada celda ocupa CELL_W * scale en pantalla al final
    visible_cols = max(1, pixels_available // (CELL_W * max(1, scale)))

    # El TileGrid trabaja en celdas, no escaladas
    grid = displayio.TileGrid(
        FONT.bitmap,
        pixel_shader=palette,
        tile_width=CELL_W,
        tile_height=CELL_H,
        width=visible_cols,
        height=1,
        x=0,
        y=0,
    )

    term = terminalio.Terminal(grid, FONT)
    if text:
        term.write(text[:visible_cols])

    # Envolvemos en un Group con escala y posición en píxeles
    g = displayio.Group(scale=max(1, scale), x=x_px, y=y_px)
    g.append(grid)
    return g, term

# ---------------------- main screen ----------------------
def mostrar_sd_info():
    if not hasattr(board, "DISPLAY"):
        print("Objeto DISPLAY no encontrado.")
        return

    display = board.DISPLAY
    splash = displayio.Group()

    # background color
    top = shapes.rect(0, 0, display.width, 15, fill=color.violet)
    splash.append(top)

    # Header
    header = shapes.rect(0, 0, display.width, 30, fill=color.red)
    splash.append(header)

    # Title (centrado a ojo en píxeles, pero ajustando por cols visibles con la escala)
    title = "SD Card Info"
    # cols en pantalla teniendo en cuenta la escala
    total_cols_scaled = display.width // (CELL_W * max(1, SCALE))
    x_title_cols = max(0, (total_cols_scaled - len(title)) // 2)
    x_title = x_title_cols * CELL_W * max(1, SCALE)
    title_group, _ = make_line(display, y_px=8, fg=color.white, bg=color.red, text=title, x_px=x_title, scale=SCALE)
    splash.append(title_group)

    # spacer
    separator = shapes.rect(0, 30, display.width, 2, fill=color.white)
    splash.append(separator)

    # Cálculo de salto vertical por línea según escala
    line_step = CELL_H * max(1, SCALE) + LINE_SP

    y = 40
    if sd_manager.mounted:
        detalles = sd_manager.detalles_tarjeta()
        if detalles:
            g, _ = make_line(display, y_px=y,   fg=color.green,  text=f"Capacidad: {detalles['capacidad_total']:.2f} MB", scale=SCALE); splash.append(g); y += line_step
            g, _ = make_line(display, y_px=y,   fg=color.cyan,   text=f"Libre:     {detalles['espacio_libre']:.2f} MB",   scale=SCALE); splash.append(g); y += line_step
            g, _ = make_line(display, y_px=y,   fg=color.yellow, text=f"Usado:     {detalles['espacio_utilizado']:.2f} MB", scale=SCALE); splash.append(g); y += line_step + (LINE_SP * 2)

            g, _ = make_line(display, y_px=y,   fg=color.orange, text="Archivos:", scale=SCALE); splash.append(g); y += line_step

            # Listado de archivos (controlando el borde inferior con la altura escalada)
            for nombre in detalles.get("archivos", []):
                if y + (CELL_H * max(1, SCALE)) > display.height:
                    break
                g, _ = make_line(display, y_px=y, fg=color.white, text=f"  {nombre}", scale=SCALE)
                splash.append(g); y += line_step
        else:
            g, _ = make_line(display, y_px=y, fg=color.red, text="No se pudo obtener info.", scale=SCALE)
            splash.append(g)
    else:
        g, _ = make_line(display, y_px=y, fg=color.red, text="SD no montada.", scale=SCALE)
        splash.append(g)

    display.root_group = splash
    print("Información mostrada en el display.")

# ---------------------- run ----------------------
crear_archivo_incremental()
mostrar_sd_info()
