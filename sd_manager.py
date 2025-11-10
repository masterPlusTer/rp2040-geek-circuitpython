import board
import busio
import sdcardio
import storage
import os

class SDManager:
    def __init__(self, mount_point="/sd"):
        """Inicializa y monta la tarjeta SD en el RP2040."""
        self.mount_point = mount_point
        self.spi = busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO)
        self.cs = board.SD_CS
        self.mounted = False
        try:
            self.sd = sdcardio.SDCard(self.spi, self.cs)
            self.vfs = storage.VfsFat(self.sd)
            storage.mount(self.vfs, self.mount_point)
            self.mounted = True
            print("Tarjeta SD montada con éxito en", self.mount_point)
        except Exception as e:
            print("Error al inicializar la tarjeta SD:", e)

    # ---------------------- Helpers ----------------------

    def _path(self, ruta):
        if ruta.startswith(self.mount_point):
            return ruta
        if ruta.startswith("/"):
            return f"{self.mount_point}{ruta}"
        return f"{self.mount_point}/{ruta}"

    def existe(self, ruta):
        """Devuelve True si existe archivo o carpeta."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return False
        try:
            os.stat(self._path(ruta))
            return True
        except OSError:
            return False

    def es_directorio(self, ruta):
        """True si la ruta es un directorio."""
        try:
            s = os.stat(self._path(ruta))
            # 0x4000 suele indicar directorio en CircuitPython
            return (s[0] & 0x4000) != 0
        except OSError:
            return False

    # ---------------------- Listado ----------------------

    def listar(self, ruta="/"):
        """Lista nombres en una ruta (no recursivo)."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return []
        try:
            return os.listdir(self._path(ruta))
        except Exception as e:
            print("Error al listar:", e)
            return []

    def listar_recursivo(self, ruta="/"):
        """Genera tuplas (ruta_relativa, es_directorio) de forma recursiva."""
        base = self._path(ruta)
        try:
            for nombre in os.listdir(base):
                full = base + ("" if base.endswith("/") else "/") + nombre
                rel = full[len(self.mount_point):]
                isdir = self.es_directorio(rel)
                yield rel, isdir
                if isdir:
                    for sub in self.listar_recursivo(rel):
                        yield sub
        except Exception as e:
            print("Error en listado recursivo:", e)

    # ---------------------- Archivos ----------------------

    def crear_archivo(self, nombre, contenido=""):
        """Crea un archivo nuevo. Falla si ya existe."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            with open(self._path(nombre), "x") as f:
                if contenido:
                    f.write(contenido)
            print(f"Archivo '{nombre}' creado.")
        except Exception as e:
            print(f"Error al crear '{nombre}':", e)

    def escribir_archivo(self, nombre, contenido):
        """Sobrescribe un archivo con contenido."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            with open(self._path(nombre), "w") as f:
                f.write(contenido)
            print(f"Archivo '{nombre}' escrito con éxito.")
        except Exception as e:
            print(f"Error al escribir '{nombre}':", e)

    def anexar_archivo(self, nombre, contenido):
        """Añade contenido al final del archivo."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            with open(self._path(nombre), "a") as f:
                f.write(contenido)
            print(f"Contenido anexado a '{nombre}'.")
        except Exception as e:
            print(f"Error al anexar en '{nombre}':", e)

    def leer_archivo(self, nombre):
        """Lee todo el archivo como texto."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return None
        try:
            with open(self._path(nombre), "r") as f:
                data = f.read()
            print(f"Contenido de '{nombre}':\n{data}")
            return data
        except Exception as e:
            print(f"Error al leer '{nombre}':", e)
            return None

    def leer_lineas(self, nombre):
        """Devuelve lista de líneas."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return []
        try:
            with open(self._path(nombre), "r") as f:
                return f.readlines()
        except Exception as e:
            print(f"Error al leer líneas de '{nombre}':", e)
            return []

    def editar_linea(self, nombre, numero_linea, nuevo_texto, mantener_salto=True):
        """
        Reemplaza la línea N (1-based) por nuevo_texto.
        Por defecto conserva el salto de línea.
        """
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            lineas = self.leer_lineas(nombre)
            idx = numero_linea - 1
            if idx < 0 or idx >= len(lineas):
                print("Número de línea fuera de rango.")
                return
            if mantener_salto and not nuevo_texto.endswith("\n"):
                nuevo_texto = nuevo_texto + "\n"
            lineas[idx] = nuevo_texto if mantener_salto else nuevo_texto.rstrip("\n")
            with open(self._path(nombre), "w") as f:
                f.writelines(lineas)
            print(f"Línea {numero_linea} editada en '{nombre}'.")
        except Exception as e:
            print(f"Error al editar línea en '{nombre}':", e)

    def reemplazar_texto(self, nombre, buscar, reemplazar, max_reemplazos=-1):
        """Reemplaza texto en todo el archivo. max_reemplazos=-1 para todos."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return 0
        try:
            data = self.leer_archivo(nombre)
            if data is None:
                return 0
            total = data.count(buscar)
            if max_reemplazos == -1:
                nuevo = data.replace(buscar, reemplazar)
                hechos = total
            else:
                nuevo = data.replace(buscar, reemplazar, max_reemplazos)
                hechos = min(total, max_reemplazos)
            self.escribir_archivo(nombre, nuevo)
            print(f"Reemplazos realizados: {hechos}")
            return hechos
        except Exception as e:
            print(f"Error al reemplazar texto en '{nombre}':", e)
            return 0

    # ---------------------- Gestión de archivos ----------------------

    def renombrar_archivo(self, nombre_actual, nuevo_nombre):
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            os.rename(self._path(nombre_actual), self._path(nuevo_nombre))
            print(f"'{nombre_actual}' renombrado a '{nuevo_nombre}'.")
        except Exception as e:
            print(f"Error al renombrar '{nombre_actual}':", e)

    def copiar_archivo(self, origen, destino, sobrescribir=False, tam_bloque=4096):
        """Copia un archivo. No sobrescribe salvo que se indique."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        src = self._path(origen)
        dst = self._path(destino)
        if self.existe(destino) and not sobrescribir:
            print(f"Destino '{destino}' ya existe. Usa sobrescribir=True.")
            return
        try:
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                while True:
                    bloque = fsrc.read(tam_bloque)
                    if not bloque:
                        break
                    fdst.write(bloque)
            print(f"Copiado '{origen}' -> '{destino}'.")
        except Exception as e:
            print(f"Error al copiar '{origen}':", e)

    def mover_archivo(self, origen, destino, sobrescribir=False):
        """Mueve un archivo (copia y borra)."""
        if self.existe(destino) and not sobrescribir:
            print(f"Destino '{destino}' ya existe. Usa sobrescribir=True.")
            return
        self.copiar_archivo(origen, destino, sobrescribir=sobrescribir)
        if self.existe(destino):
            self.borrar_archivo(origen)

    def borrar_archivo(self, nombre):
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            os.remove(self._path(nombre))
            print(f"Archivo '{nombre}' eliminado.")
        except Exception as e:
            print(f"Error al eliminar '{nombre}':", e)

    # ---------------------- Directorios ----------------------

    def crear_directorio(self, ruta):
        """Crea un directorio (no recursivo)."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        try:
            os.mkdir(self._path(ruta))
            print(f"Directorio '{ruta}' creado.")
        except Exception as e:
            print(f"Error al crear directorio '{ruta}':", e)

    def borrar_directorio(self, ruta, recursivo=False):
        """Elimina directorio. Si recursivo=True, borra su contenido."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return
        pr = self._path(ruta)
        try:
            if recursivo:
                # Borrar archivos
                for item, isdir in list(self.listar_recursivo(ruta)):
                    if not isdir:
                        try:
                            os.remove(self._path(item))
                        except Exception as e:
                            print(f"Error al borrar '{item}':", e)
                # Borrar directorios de abajo hacia arriba
                dirs = [p for p, isd in self.listar_recursivo(ruta) if isd]
                for d in sorted(dirs, key=lambda s: len(s), reverse=True):
                    try:
                        os.rmdir(self._path(d))
                    except Exception as e:
                        print(f"Error al borrar dir '{d}':", e)
            os.rmdir(pr)
            print(f"Directorio '{ruta}' eliminado.")
        except Exception as e:
            print(f"Error al borrar directorio '{ruta}':", e)

    # ---------------------- Detalles de la tarjeta ----------------------

    def detalles_tarjeta(self):
        """Capacidad total, libre y usada en MB, y listado raíz.
           Devuelve claves modernas y alias para compatibilidad."""
        if not self.mounted:
            print("La tarjeta SD no está montada.")
            return None
        try:
            statvfs = os.statvfs(self.mount_point)
            tam_bloque = statvfs[0]
            bloques_totales = statvfs[2]
            bloques_libres = statvfs[3]
            total_mb = tam_bloque * bloques_totales / 1024 / 1024
            libre_mb = tam_bloque * bloques_libres / 1024 / 1024
            usado_mb = total_mb - libre_mb
            archivos = self.listar("/")
            info = {
                "capacidad_total_mb": round(total_mb, 2),
                "espacio_libre_mb": round(libre_mb, 2),
                "espacio_usado_mb": round(usado_mb, 2),
                "raiz": archivos
            }
            # Aliases para código viejo
            info.update({
                "capacidad_total": info["capacidad_total_mb"],
                "espacio_libre": info["espacio_libre_mb"],
                "espacio_utilizado": info["espacio_usado_mb"],
                "archivos": info["raiz"],
            })
            print("Detalles SD:", info)
            return info
        except Exception as e:
            print("Error al obtener detalles:", e)
            return None


# ---------------------- Ejemplo de uso en REPL ----------------------

def mostrar_sd_info(sd):
    info = sd.detalles_tarjeta()
    if not info:
        return
    # Puedes usar las claves nuevas o las alias indistintamente
    print("Capacidad total:", info["capacidad_total_mb"], "MB")
    print("Espacio libre:", info["espacio_libre_mb"], "MB")
    print("Espacio usado:", info["espacio_usado_mb"], "MB")
    print("Archivos en raíz:", info["raiz"])

if __name__ == "__main__":
    sd = SDManager()
    if sd.mounted:
        # Demostración mínima sin pisarnos los dedos:
        if not sd.existe("nuevo_archivo.txt"):
            sd.crear_archivo("nuevo_archivo.txt", "Hola desde CircuitPython\n")
        else:
            sd.anexar_archivo("nuevo_archivo.txt", "Otra línea\n")
        mostrar_sd_info(sd)
