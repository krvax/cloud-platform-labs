"""
NIVEL 1: Context Managers (`with`)

Como SRE, manejes conexiones TCP, descriptores de archivos, o sesiones de AWS.
Si el código crashea antes de cerrar el recurso (ej. `file.close()`), generas leaks.

El statement `with` garantiza que un recurso se limpia (teardown)
incluso si ocurre una excepción dentro del bloque.
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ❌ SIN CONTEXT MANAGER (Riesgo de Resource Leak)
def read_config_dangerous(filepath: str):
    f = open(filepath, 'r')
    # Si hay una excepción aquí, la línea f.close() nunca se ejecuta.
    # El archivo se queda "abierto" y bloqueado en memoria/SO.
    # raise Exception("Crash inesperado")
    content = f.read()
    f.close() 
    return content

# ✅ CON CONTEXT MANAGER (Seguro y SRE-ready)
def read_config_safe(filepath: str):
    # La cláusula 'with' asegura que Python llame a __exit__() de la clase file,
    # lo cual cierra el archivo SIEMPRE, incluso si hay excepciones.
    with open(filepath, 'r') as f:
        content = f.read()
    return content

# 🚀 CREANDO TUS PROPIOS CONTEXT MANAGERS
class DatabaseSession:
    """Ejemplo de un Context Manager personalizado."""
    def __init__(self, db_url: str):
        self.db_url = db_url

    def __enter__(self):
        logger.info(f"🔗 Abriendo conexión a {self.db_url}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Esta parte SIEMPRE se ejecuta al salir del bloque 'with'
        if exc_type is not None:
            logger.error(f"🔥 Ocurrió un error dentro de la sesión: {exc_value}")
        logger.info(f"🔒 Cerrando conexión a {self.db_url} de forma segura.")
        # Retornar True "suprimiría" la excepción. Usualmente queremos que suba.

if __name__ == "__main__":
    logger.info("Probando Context Manager propio...")
    
    try:
        with DatabaseSession("postgresql://admin:secret@prod-db:5432/main") as db:
            logger.info("Realizando queries...")
            # Simulamos un crash en la base de datos
            raise RuntimeError("Out of Memory en DB Query")
    except RuntimeError:
        logger.warning("El proceso principal capturó el crash, pero la conexión a DB se cerró correctamente gracias al __exit__.")
