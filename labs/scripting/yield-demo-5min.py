#!/usr/bin/env python3
"""
YIELD en 5 minutos - Demo interactiva
Ejecuta esto y VE la diferencia con tus propios ojos
"""

print("=" * 60)
print("🍕 YIELD = Pizzería que entrega pizza por pizza")
print("=" * 60)

# =============================================================================
# DEMO 1: La diferencia básica
# =============================================================================

print("\n📌 DEMO 1: ¿Cuál es la diferencia?")
print("-" * 60)

print("\n❌ SIN YIELD (return):")
print("   Ejecuta TODO de golpe, luego entrega\n")

def pizzas_sin_yield():
    print("      🍕 Cocinando pizza 1...")
    print("      🍕 Cocinando pizza 2...")
    print("      🍕 Cocinando pizza 3...")
    print("      📦 Empacando las 3 pizzas...")
    return ["Pizza 1", "Pizza 2", "Pizza 3"]

resultado = pizzas_sin_yield()
print(f"\n   Cliente recibe: {resultado}")
print("   ↑ Todo se ejecutó ANTES de que el cliente reciba algo")

print("\n" + "=" * 60)
print("\n✅ CON YIELD:")
print("   Entrega UNA, se pausa, espera, entrega otra...\n")

def pizzas_con_yield():
    print("      🍕 Cocinando pizza 1...")
    yield "Pizza 1"
    print("      [PAUSADO - esperando que pidan la siguiente]")
    
    print("      🍕 Cocinando pizza 2...")
    yield "Pizza 2"
    print("      [PAUSADO - esperando que pidan la siguiente]")
    
    print("      🍕 Cocinando pizza 3...")
    yield "Pizza 3"
    print("      [PAUSADO - esperando que pidan la siguiente]")

generador = pizzas_con_yield()
print("   Generador creado (no cocinó nada todavía)\n")

print("   Cliente pide la primera:")
primera = next(generador)
print(f"   Cliente recibe: {primera}\n")

print("   Cliente pide la segunda:")
segunda = next(generador)
print(f"   Cliente recibe: {segunda}\n")

print("   Cliente pide la tercera:")
tercera = next(generador)
print(f"   Cliente recibe: {tercera}\n")

# =============================================================================
# DEMO 2: Caso real - Leer archivo línea por línea
# =============================================================================

print("=" * 60)
print("📌 DEMO 2: Leer logs (tu caso de uso real)")
print("-" * 60)

# Crear archivo de ejemplo
print("\n📝 Creando archivo de logs...")
with open('demo.log', 'w') as f:
    f.write("Línea 1: INFO - Todo bien\n")
    f.write("Línea 2: ERROR - Algo falló\n")
    f.write("Línea 3: INFO - Todo bien\n")
    f.write("Línea 4: ERROR - Otro error\n")
    f.write("Línea 5: INFO - Todo bien\n")

print("\n❌ SIN YIELD (carga todo a memoria):")

def leer_sin_yield(archivo):
    print(f"      Abriendo {archivo}...")
    with open(archivo) as f:
        lineas = f.readlines()  # Lee TODAS las líneas
    print(f"      Cargó {len(lineas)} líneas a memoria")
    return lineas

todas = leer_sin_yield('demo.log')
print(f"   Tipo: {type(todas)}")
print(f"   Contenido: {todas[0].strip()}")

print("\n✅ CON YIELD (una línea a la vez):")

def leer_con_yield(archivo):
    print(f"      Abriendo {archivo}...")
    with open(archivo) as f:
        for linea in f:
            print(f"      Leyendo: {linea.strip()}")
            yield linea

gen = leer_con_yield('demo.log')
print(f"   Tipo: {type(gen)}")
print("   No leyó nada todavía - esperando que le pidas\n")

print("   Pidiendo primera línea:")
primera = next(gen)
print(f"   Recibí: {primera.strip()}\n")

print("   Pidiendo segunda línea:")
segunda = next(gen)
print(f"   Recibí: {segunda.strip()}\n")

print("   Pidiendo el resto con un for:")
for linea in gen:
    print(f"   Recibí: {linea.strip()}")

# =============================================================================
# DEMO 3: Filtrar errores (tu trabajo diario)
# =============================================================================

print("\n" + "=" * 60)
print("📌 DEMO 3: Buscar solo los ERRORs (caso SRE real)")
print("-" * 60)

def buscar_errores(archivo):
    """Solo entrega las líneas con ERROR"""
    with open(archivo) as f:
        for linea in f:
            if 'ERROR' in linea:
                yield linea

print("\n✅ Buscando errores con yield:")
print("   (Procesa las 5 líneas pero solo entrega 2)\n")

for error in buscar_errores('demo.log'):
    print(f"   🚨 {error.strip()}")

# =============================================================================
# DEMO 4: La ventaja de memoria
# =============================================================================

print("\n" + "=" * 60)
print("📌 DEMO 4: ¿Por qué importa? (Memoria)")
print("-" * 60)

import sys

print("\n❌ Lista (sin yield):")
lista = [1, 2, 3, 4, 5]
print(f"   Tamaño en memoria: {sys.getsizeof(lista)} bytes")
print(f"   Contenido: {lista}")

print("\n✅ Generador (con yield):")
def numeros():
    for i in [1, 2, 3, 4, 5]:
        yield i

gen = numeros()
print(f"   Tamaño en memoria: {sys.getsizeof(gen)} bytes")
print(f"   Contenido: {gen} (no cargó los números todavía)")

print("\n💡 Diferencia:")
print(f"   Lista usa {sys.getsizeof(lista)} bytes")
print(f"   Generador usa {sys.getsizeof(gen)} bytes")
print(f"   Ahorro: {sys.getsizeof(lista) - sys.getsizeof(gen)} bytes")
print("\n   ↑ Con 1 millón de números, la diferencia es GIGANTE")

# =============================================================================
# RESUMEN
# =============================================================================

print("\n" + "=" * 60)
print("🎯 RESUMEN EN 3 PUNTOS")
print("=" * 60)

print("""
1. YIELD = Pausa la función y entrega un valor
   - No termina la función (como return)
   - Espera a que le pidas el siguiente valor
   
2. GENERADOR = Función con yield
   - Se ejecuta BAJO DEMANDA (lazy)
   - Usa poquísima memoria
   - Perfecto para archivos grandes
   
3. CUÁNDO USARLO:
   ✅ Logs de CloudWatch (GB de datos)
   ✅ Archivos CSV gigantes
   ✅ Streams de métricas
   ✅ Cuando no sabes cuántos datos vas a procesar
   
ANALOGÍA:
   Netflix (yield) vs Descargar toda la serie (return)
   
PARA LA ENTREVISTA:
   "Uso yield en mis scripts de análisis de logs para
    procesar archivos grandes sin problemas de memoria.
    Es como streaming de datos - proceso línea por línea."
""")

# Limpiar
import os
os.remove('demo.log')
print("🧹 Archivo demo.log eliminado")

print("\n✅ ¡Listo! Ahora entiendes yield")
print("📚 Lee el cheatsheet: labs/scripting/YIELD-CHEATSHEET.md")
