import board
import displayio
import shapes
import terminalio
import color
from sd_manager import SDManager 

sd_manager = SDManager()

# ---------------------- new file with an incremental name----------------------
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

# ---------------------- text with terminalio.FONT ----------------------
FONT = terminalio.FONT
CELL_W, CELL_H = FONT.get_bounding_box()

def make_palette(fg=color.white, bg=color.black):
    pal = displayio.Palette(2)
    pal[0] = bg
    pal[1] = fg
    return pal

def make_line(display, y_px, fg=color.white, bg=color.black, text="", x_px=0, max_width_px=None):
    """
    Crea un TileGrid (1 fila) a y_px con color fg/bg. Escribe 'text' desde x_px.
    No usa cursor_position; el posicionamiento se hace en píxeles con x_px.
    """
    cols = (display.width // CELL_W) if max_width_px is None else (max_width_px // CELL_W)
    palette = make_palette(fg, bg)
    grid = displayio.TileGrid(
        FONT.bitmap,
        pixel_shader=palette,
        tile_width=CELL_W,
        tile_height=CELL_H,
        width=cols,
        height=1,
        x=x_px,
        y=y_px,
    )
    term = terminalio.Terminal(grid, FONT)
    # write clean line
    if text:
        term.write(text[:cols])
    return grid, term

# ---------------------- main screen ----------------------
def mostrar_sd_info():
    if not hasattr(board, "DISPLAY"):
        print("Objeto DISPLAY no encontrado.")
        return

    display = board.DISPLAY
    splash = displayio.Group()

    # backround color
    top = shapes.rect(0, 0, display.width, 15, fill=color.violet)
    splash.append(top)

    # Header
    header = shapes.rect(0, 0, display.width, 30, fill=color.red)
    splash.append(header)

    # Title
    title = "SD Card Info"
    total_cols = display.width // CELL_W
    x_title = max(0, ((total_cols - len(title)) // 2) * CELL_W)
    line, _ = make_line(display, y_px=8, fg=color.white, bg=color.red, text=title, x_px=x_title)
    splash.append(line)

    # spacer
    separator = shapes.rect(0, 30, display.width, 2, fill=color.white)
    splash.append(separator)

    y = 40
    if sd_manager.mounted:
        detalles = sd_manager.detalles_tarjeta()
        if detalles:
            g, _ = make_line(display, y_px=y,   fg=color.green,  text=f"Capacidad: {detalles['capacidad_total']:.2f} MB"); splash.append(g); y += 15
            g, _ = make_line(display, y_px=y,   fg=color.cyan,   text=f"Libre:     {detalles['espacio_libre']:.2f} MB");   splash.append(g); y += 15
            g, _ = make_line(display, y_px=y,   fg=color.yellow, text=f"Usado:     {detalles['espacio_utilizado']:.2f} MB"); splash.append(g); y += 20
            g, _ = make_line(display, y_px=y,   fg=color.orange, text="Archivos:"); splash.append(g); y += 15

            for nombre in detalles.get("archivos", []):
                if y + CELL_H > display.height:
                    break
                g, _ = make_line(display, y_px=y, fg=color.white, text=f"  {nombre}")
                splash.append(g); y += 12
        else:
            g, _ = make_line(display, y_px=y, fg=color.red, text="No se pudo obtener info.")
            splash.append(g)
    else:
        g, _ = make_line(display, y_px=y, fg=color.red, text="SD no montada.")
        splash.append(g)

    display.root_group = splash
    print("Información mostrada en el display.")

# ---------------------- run ----------------------
crear_archivo_incremental()
mostrar_sd_info()
