#!/usr/bin/env python3
"""
YIELD EXPLICADO SIMPLE - Para SREs que no programan Python diario
=================================================================

La analogía de la pizzería es perfecta. Aquí te muestro ejemplos
REALES que vas a usar en tu trabajo.
"""

# =============================================================================
# EJEMPLO 1: Leer un archivo de logs GIGANTE
# =============================================================================

print("=" * 70)
print("EJEMPLO 1: Leer logs de 1GB sin romper tu laptop")
print("=" * 70)

# ❌ FORMA MALA (sin yield) - Se come toda tu RAM
def leer_logs_malo(archivo):
    """Lee TODO el archivo a memoria. Si es de 1GB, usa 1GB de RAM"""
    todas_las_lineas = []  # Lista vacía = tu cocina
    
    with open(archivo, 'r') as f:
        for linea in f:
            todas_las_lineas.append(linea)  # Guardas TODAS las pizzas
    
    return todas_las_lineas  # Entregas todo de golpe
    # Problema: Si el archivo tiene 10 millones de líneas, 
    # tu RAM tiene que guardar 10 millones de strings

# ✅ FORMA BUENA (con yield) - Usa poquísima RAM
def leer_logs_bueno(archivo):
    """Lee UNA línea a la vez. Archivo de 1GB = usa solo bytes de RAM"""
    with open(archivo, 'r') as f:
        for linea in f:
            yield linea  # Entregas UNA pizza, te pausas
    
    # Magia: Python mantiene la función "viva" pero pausada
    # Solo procesa la siguiente línea cuando se la pides

# Ejemplo de uso:
print("\n📝 Creando archivo de ejemplo...")
with open('ejemplo.log', 'w') as f:
    for i in range(10):
        f.write(f"[ERROR] Línea {i+1} del log\n")

print("\n❌ Forma MALA (carga todo a memoria):")
todas = leer_logs_malo('ejemplo.log')
print(f"   Tipo: {type(todas)}")  # Es una lista
print(f"   Tamaño en memoria: {len(todas)} líneas cargadas")
print(f"   Primera línea: {todas[0].strip()}")

print("\n✅ Forma BUENA (yield - una a la vez):")
generador = leer_logs_bueno('ejemplo.log')
print(f"   Tipo: {type(generador)}")  # Es un generador
print(f"   Memoria usada: CASI NADA (solo 1 línea a la vez)")
print(f"   Primera línea: {next(generador).strip()}")  # Pide la primera
print(f"   Segunda línea: {next(generador).strip()}")  # Pide la segunda

# =============================================================================
# EJEMPLO 2: Buscar errores en logs (caso real de SRE)
# =============================================================================

print("\n" + "=" * 70)
print("EJEMPLO 2: Buscar errores en logs (tu trabajo diario)")
print("=" * 70)

# ❌ Sin yield - carga TODO el archivo
def buscar_errores_malo(archivo):
    """Lee todo el archivo, luego filtra. Lento y come RAM."""
    todas_las_lineas = []
    with open(archivo, 'r') as f:
        todas_las_lineas = f.readlines()  # Lee TODO
    
    errores = []
    for linea in todas_las_lineas:
        if 'ERROR' in linea:
            errores.append(linea)
    
    return errores

# ✅ Con yield - procesa línea por línea
def buscar_errores_bueno(archivo):
    """Lee y filtra al mismo tiempo. Rápido y eficiente."""
    with open(archivo, 'r') as f:
        for linea in f:
            if 'ERROR' in linea:
                yield linea  # Solo entrega las líneas con ERROR

print("\n📝 Creando log con 1000 líneas (solo 10 tienen ERROR)...")
with open('app.log', 'w') as f:
    for i in range(1000):
        if i % 100 == 0:  # Solo cada 100 líneas es ERROR
            f.write(f"[ERROR] Fallo en línea {i}\n")
        else:
            f.write(f"[INFO] Todo bien en línea {i}\n")

print("\n❌ Forma MALA:")
errores_malos = buscar_errores_malo('app.log')
print(f"   Cargó 1000 líneas a memoria")
print(f"   Encontró {len(errores_malos)} errores")
print(f"   Primer error: {errores_malos[0].strip()}")

print("\n✅ Forma BUENA (yield):")
errores_buenos = buscar_errores_bueno('app.log')
print(f"   Tipo: {type(errores_buenos)}")
print(f"   No cargó nada todavía - está esperando que le pidas líneas")

# Ahora SÍ procesamos (una a la vez)
contador = 0
for error in errores_buenos:
    contador += 1
    if contador == 1:
        print(f"   Primer error: {error.strip()}")
    if contador == 3:
        print(f"   Tercer error: {error.strip()}")
        break  # Paramos aquí - no procesó las otras 997 líneas

print(f"   Solo procesó {contador} líneas (no las 1000)")

# =============================================================================
# EJEMPLO 3: La diferencia VISUAL
# =============================================================================

print("\n" + "=" * 70)
print("EJEMPLO 3: ¿Qué pasa internamente?")
print("=" * 70)

def contar_sin_yield():
    """Cuenta del 1 al 5 y retorna TODO de golpe"""
    numeros = []
    for i in range(1, 6):
        print(f"      [sin yield] Generando número {i}")
        numeros.append(i)
    print(f"      [sin yield] Retornando TODOS los números de golpe")
    return numeros

def contar_con_yield():
    """Cuenta del 1 al 5 pero entrega UNO a la vez"""
    for i in range(1, 6):
        print(f"      [con yield] Generando número {i}")
        yield i
        print(f"      [con yield] Me pausé, esperando que me pidan el siguiente")

print("\n❌ SIN YIELD (return):")
resultado = contar_sin_yield()
print(f"   Resultado: {resultado}")
print(f"   Todo se ejecutó de golpe\n")

print("✅ CON YIELD (generador):")
generador = contar_con_yield()
print(f"   Generador creado: {generador}")
print(f"   ¡Todavía no ejecutó NADA!\n")

print("   Ahora voy a pedir el primer número:")
primero = next(generador)
print(f"   Recibí: {primero}\n")

print("   Ahora voy a pedir el segundo número:")
segundo = next(generador)
print(f"   Recibí: {segundo}\n")

print("   Voy a pedir el resto con un for:")
for numero in generador:
    print(f"   Recibí: {numero}")

# =============================================================================
# EJEMPLO 4: Caso real - Analizar logs de CloudWatch
# =============================================================================

print("\n" + "=" * 70)
print("EJEMPLO 4: Caso REAL - Logs de CloudWatch (millones de líneas)")
print("=" * 70)

def analizar_cloudwatch_logs(archivo):
    """
    Imagina que descargaste logs de CloudWatch de 1 semana.
    Son 50GB de logs. Con yield, puedes procesarlos sin problema.
    """
    errores_criticos = 0
    
    with open(archivo, 'r') as f:
        for linea in f:
            # Procesas línea por línea (yield implícito en el for)
            if 'CRITICAL' in linea or 'FATAL' in linea:
                errores_criticos += 1
                yield {
                    'tipo': 'CRITICO',
                    'linea': linea.strip(),
                    'total_hasta_ahora': errores_criticos
                }

# Crear log de ejemplo
print("\n📝 Simulando logs de CloudWatch...")
with open('cloudwatch.log', 'w') as f:
    for i in range(10000):
        if i % 1000 == 0:
            f.write(f"[CRITICAL] Sistema caído en timestamp {i}\n")
        else:
            f.write(f"[INFO] Request procesado {i}\n")

print("\n✅ Analizando 10,000 líneas con yield:")
print("   (Solo muestra los críticos, pero procesó todo)")

for evento in analizar_cloudwatch_logs('cloudwatch.log'):
    print(f"   🚨 {evento['tipo']}: {evento['linea'][:50]}... (Total: {evento['total_hasta_ahora']})")

# =============================================================================
# RESUMEN PARA TU ENTREVISTA
# =============================================================================

print("\n" + "=" * 70)
print("🎯 RESUMEN PARA TU ENTREVISTA CON J&J")
print("=" * 70)

print("""
1. ¿Qué es yield?
   → Es como un 'return' que PAUSA la función en lugar de terminarla
   
2. ¿Para qué sirve?
   → Para procesar archivos GIGANTES sin llenar la RAM
   → Logs de 50GB, CSVs de millones de filas, streams de datos
   
3. ¿Cuándo lo usas?
   → Cuando lees logs de CloudWatch
   → Cuando analizas archivos de auditoría
   → Cuando procesas métricas en tiempo real
   
4. ¿Qué ventaja tiene?
   → Memoria: Solo usa RAM para 1 línea a la vez
   → Velocidad: Empieza a procesar inmediatamente (no espera a leer todo)
   → Escalabilidad: Funciona igual con 100 líneas o 100 millones
   
5. Frase para la entrevista:
   "En mi script de análisis de logs, uso yield para procesar archivos
    de CloudWatch de varios GB sin problemas de memoria. El generador
    me permite iterar línea por línea de forma eficiente."

6. Analogía simple:
   "yield es como Netflix: te da un episodio a la vez, no descarga
    toda la temporada antes de empezar a ver"
""")

print("\n✅ Archivos de ejemplo creados:")
print("   - ejemplo.log")
print("   - app.log")
print("   - cloudwatch.log")
print("\n💡 Ejecuta este script para ver yield en acción:")
print("   python3 labs/scripting/yield-explicado-simple.py")

# Limpiar archivos de ejemplo
import os
for archivo in ['ejemplo.log', 'app.log', 'cloudwatch.log']:
    if os.path.exists(archivo):
        os.remove(archivo)
print("\n🧹 Archivos de ejemplo eliminados")
