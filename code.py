import board
import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
from sd_manager import SDManager  # Importar la biblioteca SDManager

# Crear una instancia del administrador de la tarjeta SD
sd_manager = SDManager()

# Crear un archivo nuevo en la tarjeta SD
def crear_y_mostrar_archivo():
    if sd_manager.mounted:
        try:
            # Nombre único para el archivo
            nuevo_archivo = "nuevo_archivo.txt"
            contenido = "Hola, este es un archivo creado desde CircuitPython.\n"
            sd_manager.escribir_archivo(nuevo_archivo, contenido)
            print(f"Archivo '{nuevo_archivo}' creado con éxito.")
        except Exception as e:
            print(f"Error al crear el archivo '{nuevo_archivo}':", e)
    else:
        print("La tarjeta SD no está montada.")

# Mostrar los archivos en el display
def mostrar_archivos_en_display():
    # Verificar si DISPLAY está disponible
    if hasattr(board, "DISPLAY"):
        display = board.DISPLAY

        # Crear un grupo de display
        splash = displayio.Group()

        # Dibujar un rectángulo azul como fondo
        color_bitmap = displayio.Bitmap(240, 135, 1)  # Tamaño y colores (1-bit)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0b000000000000000011111111  # azul
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette)
        splash.append(bg_sprite)

        # Añadir un rectángulo rojo decorativo
        rect = Rect(10, 10, 220, 50, fill=0b111111110000000000000000)
        splash.append(rect)

        # Verificar si la tarjeta SD está montada
        if sd_manager.mounted:
            archivos = sd_manager.listar_archivos()  # Listar archivos de la tarjeta SD
            if archivos:
                # Mostrar los nombres de los archivos en la pantalla
                y_offset = 60  # Coordenada Y inicial para el texto
                for archivo in archivos:
                    text_area = label.Label(
                        terminalio.FONT,
                        text=archivo,
                        color=0xFFFFFF
                    )
                    text_area.x = 10
                    text_area.y = y_offset
                    splash.append(text_area)
                    y_offset += 15  # Incrementar para el siguiente archivo
            else:
                # Mostrar mensaje si no hay archivos
                no_files_text = label.Label(
                    terminalio.FONT,
                    text="No hay archivos en la SD.",
                    color=0xFFFFFF
                )
                no_files_text.x = 10
                no_files_text.y = 60
                splash.append(no_files_text)
        else:
            # Mostrar mensaje si la SD no está montada
            error_text = label.Label(
                terminalio.FONT,
                text="SD no montada.",
                color=0xFFFF00
            )
            error_text.x = 10
            error_text.y = 60
            splash.append(error_text)

        # Asignar el grupo al display usando root_group
        display.root_group = splash
        print("Archivos de la SD mostrados en el display.")
    else:
        print("Objeto DISPLAY no encontrado.")

# Crear el archivo y mostrar los archivos en el display
crear_y_mostrar_archivo()
mostrar_archivos_en_display()
