import board
import color
import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
from sd_manager import SDManager  # Importar la biblioteca SDManager

# Crear una instancia del administrador de la tarjeta SD
sd_manager = SDManager()

# Crear un archivo nuevo en la tarjeta SD
def crear_archivo():
    if sd_manager.mounted:
        try:
            nuevo_archivo = "nuevo_archivo.txt"
            contenido = "Hola, este es un archivo creado desde CircuitPython.\n"
            sd_manager.escribir_archivo(nuevo_archivo, contenido)
            print(f"Archivo '{nuevo_archivo}' creado con éxito.")
        except Exception as e:
            print(f"Error al crear el archivo '{nuevo_archivo}':", e)
    else:
        print("La tarjeta SD no está montada.")

# Mostrar información en el display
def mostrar_sd_info():
    if hasattr(board, "DISPLAY"):
        display = board.DISPLAY
        splash = displayio.Group()

        # Fondo violeta
        color_bitmap = displayio.Bitmap(240, 135, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = color.violet
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette)
        splash.append(bg_sprite)

        # Encabezado
        header = Rect(0, 0, 240, 30, fill=color.blue)
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

        # Línea separadora (usando un rectángulo delgado)
        separator = Rect(0, 30, 240, 2, fill=color.white)
        splash.append(separator)

        # Mostrar detalles de la SD
        if sd_manager.mounted:
            detalles = sd_manager.detalles_tarjeta()

            if detalles:
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
crear_archivo()
mostrar_sd_info()
