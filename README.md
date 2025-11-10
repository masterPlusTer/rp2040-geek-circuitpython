# RP2040-GEEK-CircuitPython
intento de interface novato friendly para el RP2040-GEEK en Circuit Python



por ahora solo hay esto, pero bueno, finalmente logre integrar la sd y el display en un mismo codigo.
esta porqueria que hay aqui genera un archivo en la sd y lo muestra en el display, todo un logro 

despues voy a hacer un modulo que encapsule toda la complejidad para que se pueda hacer cosas facilmente

IMPORTANTE, debes flashearle el firmware de la pagina oficial de circuit python https://circuitpython.org/board/waveshare_rp2040_geek/ si usas otro no funcionara


IMPORTANTE TAMBIEN, esto depende de las siguientes librerias externas:

- adafruit_display_shapes
- adafruit_display_text


descargate el Adafruit Circuitpython Bundle de la pagina oficial de circuit python, copia estas dos librerias y pegalas en el directorio /lib de tu dispositivo 

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::GESTION DE ARCHIVOS DE LA TARJETA SD:::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

🚀 Inicialización desde REPL

Abre el REPL de Thonny y escribe:

from sd_manager import SDManager
sd = SDManager()


Si todo está bien, deberías ver:

Tarjeta SD montada con éxito en /sd

📁 Operaciones básicas
Ver archivos en la raíz
sd.listar("/")


Resultado:

['archivo 1.txt', 'archivo 2.txt', 'datos.csv']


Listar todo el contenido de forma recursiva:

for ruta, es_dir in sd.listar_recursivo("/"):
    print("DIR" if es_dir else "FILE", ruta)

Crear, escribir y anexar archivos
sd.crear_archivo("test.txt", "Hola mundo desde CircuitPython\n")


Crea el archivo solo si no existe.

sd.escribir_archivo("test.txt", "Texto nuevo que reemplaza el anterior\n")


Sobrescribe el archivo.

sd.anexar_archivo("test.txt", "Línea agregada al final\n")


Agrega texto al final del archivo.

Leer archivos
sd.leer_archivo("test.txt")


Leer por líneas:

lineas = sd.leer_lineas("test.txt")
print(lineas)


Editar una línea específica:

sd.editar_linea("test.txt", 1, "Primera línea modificada\n")


Reemplazar texto en todo el archivo:

sd.reemplazar_texto("test.txt", "mundo", "planeta")

Renombrar, copiar y mover archivos

Renombrar:

sd.renombrar_archivo("test.txt", "nuevo.txt")


Copiar:

sd.copiar_archivo("nuevo.txt", "copia.txt", sobrescribir=True)


Mover (copia y borra el original):

sd.mover_archivo("copia.txt", "backup/copia.txt", sobrescribir=True)

Borrar archivos y carpetas

Borrar un archivo:

sd.borrar_archivo("nuevo.txt")


Crear carpeta:

sd.crear_directorio("logs")


Borrar carpeta vacía:

sd.borrar_directorio("logs")


Borrar carpeta con contenido:

sd.borrar_directorio("logs", recursivo=True)

Comprobar existencia

Verifica si un archivo o carpeta existe:

sd.existe("test.txt")


Verifica si es carpeta:

sd.es_directorio("logs")

💾 Consultar detalles de la tarjeta SD
info = sd.detalles_tarjeta()


Ejemplo de salida:

Detalles SD: {
  'capacidad_total_mb': 15255.1,
  'espacio_libre_mb': 15254.9,
  'espacio_usado_mb': 0.2,
  'raiz': ['archivo 1.txt', 'archivo 2.txt']
}


Puedes acceder a las claves:

Clave	Descripción
capacidad_total_mb / capacidad_total	Capacidad total en MB
espacio_libre_mb / espacio_libre	Espacio libre en MB
espacio_usado_mb / espacio_utilizado	Espacio usado en MB
raiz / archivos	Lista de archivos en la raíz
🔢 Creación automática de archivos numerados

Si usas el script con display, ya tienes incluida esta función:

crear_archivo_incremental()


Cada vez que se ejecuta el código, crea automáticamente:

archivo 1.txt
archivo 2.txt
archivo 3.txt
...


Si borras algunos intermedios, continuará con el siguiente número correcto.

Ejemplo: si tienes archivo 1.txt y archivo 3.txt, el siguiente será archivo 4.txt.

🧹 Desmontar manualmente (opcional)

Si deseas desmontar la SD antes de retirarla físicamente:

import storage
storage.umount("/sd")

📚 Resumen rápido de comandos
Acción		==> Comando

Montar SD		==> sd = SDManager()

Listar archivos		==> sd.listar("/")

Crear archivo		==> sd.crear_archivo("a.txt", "texto")

Escribir (sobrescribir)		==> sd.escribir_archivo("a.txt", "nuevo texto")

Anexar contenido		==> sd.anexar_archivo("a.txt", "línea más\n")

Leer archivo		==> sd.leer_archivo("a.txt")

Renombrar		==> sd.renombrar_archivo("a.txt", "b.txt")

Copiar		==> sd.copiar_archivo("b.txt", "copia.txt")

Mover		==> sd.mover_archivo("copia.txt", "sub/copia.txt")

Borrar archivo		==> sd.borrar_archivo("b.txt")

Crear carpeta		==> sd.crear_directorio("sub")

Borrar carpeta recursiva		==> sd.borrar_directorio("sub", recursivo=True)

Consultar detalles SD	   ==> sd.detalles_tarjeta()
