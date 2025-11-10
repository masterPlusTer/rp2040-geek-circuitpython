import board
import color
import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
from sd_manager import SDManager  # Importar la biblioteca SDManager

# Crear una instancia del administrador de la tarjeta SD
sd_manager = SDManager()

# ---------------------- Utilidad: siguiente nombre incremental ----------------------
def siguiente_nombre_incremental(base="archivo", ext="txt", carpeta="/"):
    """
    Busca en la carpeta dada archivos tipo:
      'archivo 1.txt', 'archivo 2.txt', ...
    y devuelve el siguiente nombre disponible.
    No usa regex para maximizar compatibilidad en CircuitPython.
    """
    if not sd_manager.mounted:
        # No hay SD, no nos hagamos ilusiones
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
        # Extraer la parte numérica entre "base " y ".ext"
        medio = nombre[len(prefijo):-len(sufijo)]
        # Permite espacios accidentales: "archivo   7.txt"
        medio = medio.strip()
        # Intenta convertir a entero
        try:
            n = int(medio)
            if n > max_n:
                max_n = n
        except ValueError:
            # No es un número válido: lo ignoramos
            pass

    siguiente = max_n + 1
    return f"{base} {siguiente}.{ext}"

# Crear un archivo nuevo en la tarjeta SD
def crear_archivo_incremental():
    if sd_manager.mounted:
        try:
            nombre = siguiente_nombre_incremental(base="archivo", ext="txt", carpeta="/")
            contenido = "Hola, este es un archivo creado desde CircuitPython.\n"
            # Usa crear_archivo para fallar si existe (no debería existir)
            sd_manager.crear_archivo(nombre, contenido)
            print(f"Archivo '{nombre}' creado con éxito.")
        except Exception as e:
            print(f"Error al crear el archivo incremental: {e}")
    else:
        print("La tarjeta SD no está montada.")

# Mostrar información en el display
def mostrar_sd_info():
    if hasattr(board, "DISPLAY"):
        display = board.DISPLAY
        splash = displayio.Group()

        # Fondo violeta superior
        color_bitmap = displayio.Bitmap(240, 15, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = color.violet
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette)
        splash.append(bg_sprite)

        # Encabezado
        header = Rect(0, 0, 240, 30, fill=color.red)
        splash.append(header)
        header_text = label.Label(
            terminalio.FONT,
            text="SD Card Info",
            color=color.white,
            scale=2,
        )
        header_text.x = 60
        header_text.y = 10
        splash.append(header_text)

        # Línea separadora
        separator = Rect(0, 30, 240, 2, fill=color.white)
        splash.append(separator)

        # Mostrar detalles de la SD
        if sd_manager.mounted:
            detalles = sd_manager.detalles_tarjeta()

            if detalles:
                # Tu SDManager ya devuelve alias: capacidad_total, espacio_libre, espacio_utilizado, archivos
                capacidad_text = label.Label(
                    terminalio.FONT,
                    text=f"Capacidad: {detalles['capacidad_total']:.2f} MB",
                    color=color.green
                )
                capacidad_text.x = 10
                capacidad_text.y = 40
                splash.append(capacidad_text)

                libre_text = label.Label(
                    terminalio.FONT,
                    text=f"Libre: {detalles['espacio_libre']:.2f} MB",
                    color=color.cyan
                )
                libre_text.x = 10
                libre_text.y = 55
                splash.append(libre_text)

                usado_text = label.Label(
                    terminalio.FONT,
                    text=f"Usado: {detalles['espacio_utilizado']:.2f} MB",
                    color=color.yellow
                )
                usado_text.x = 10
                usado_text.y = 70
                splash.append(usado_text)

                # Archivos en la SD
                archivos_text = label.Label(
                    terminalio.FONT,
                    text="Archivos:",
                    color=color.orange
                )
                archivos_text.x = 10
                archivos_text.y = 90
                splash.append(archivos_text)

                y_offset = 105
                for archivo in detalles["archivos"]:
                    archivo_label = label.Label(
                        terminalio.FONT,
                        text=archivo,
                        color=color.white
                    )
                    archivo_label.x = 15
                    archivo_label.y = y_offset
                    splash.append(archivo_label)
                    y_offset += 10
            else:
                no_sd_text = label.Label(
                    terminalio.FONT,
                    text="No se pudo obtener info.",
                    color=color.red
                )
                no_sd_text.x = 10
                no_sd_text.y = 40
                splash.append(no_sd_text)
        else:
            # SD no montada
            error_text = label.Label(
                terminalio.FONT,
                text="SD no montada.",
                color=color.red
            )
            error_text.x = 10
            error_text.y = 40
            splash.append(error_text)

        # Asignar el grupo al display
        display.root_group = splash
        print("Información mostrada en el display.")
    else:
        print("Objeto DISPLAY no encontrado.")

# Crear un archivo y mostrar información de la SD en el display
crear_archivo_incremental()
mostrar_sd_info()
