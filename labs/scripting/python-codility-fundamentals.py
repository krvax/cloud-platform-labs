#!/usr/bin/env python3
"""
Python Fundamentals for Codility Test
Critical Infrastructure SRE - Practice Guide

Tiempo: 30 minutos de repaso
Enfoque: Estructuras de datos y algoritmos básicos para SRE
"""

# =============================================================================
# 1. LISTAS - La estructura más común en Codility
# =============================================================================

# Crear y manipular listas
nums = [1, 2, 3, 4, 5]
print("Lista original:", nums)

# Agregar elementos
nums.append(6)          # Agrega al final
nums.insert(0, 0)       # Inserta en posición 0
print("Después de append/insert:", nums)

# Eliminar elementos
nums.pop()              # Elimina el último
nums.pop(0)             # Elimina en posición 0
nums.remove(3)          # Elimina el primer 3 que encuentre
print("Después de eliminar:", nums)

# Slicing (muy importante!)
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print("nums[2:5]:", nums[2:5])      # [2, 3, 4] - del índice 2 al 4
print("nums[:3]:", nums[:3])        # [0, 1, 2] - primeros 3
print("nums[7:]:", nums[7:])        # [7, 8, 9] - del 7 al final
print("nums[-3:]:", nums[-3:])      # [7, 8, 9] - últimos 3
print("nums[::2]:", nums[::2])      # [0, 2, 4, 6, 8] - cada 2
print("nums[::-1]:", nums[::-1])    # [9, 8, 7...] - reversa

# Operaciones comunes
print("len(nums):", len(nums))      # Longitud
print("max(nums):", max(nums))      # Máximo
print("min(nums):", min(nums))      # Mínimo
print("sum(nums):", sum(nums))      # Suma total
print("sorted(nums):", sorted(nums))  # Ordenada (nueva lista)

# =============================================================================
# 2. DICCIONARIOS - Para contar, agrupar, mapear
# =============================================================================

# Crear diccionario
count = {}
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

# Contar ocurrencias (patrón MUY común)
for word in words:
    count[word] = count.get(word, 0) + 1
print("Conteo:", count)

# Alternativa con defaultdict
from collections import defaultdict
count2 = defaultdict(int)
for word in words:
    count2[word] += 1
print("Conteo con defaultdict:", dict(count2))

# Alternativa con Counter (la más fácil)
from collections import Counter
count3 = Counter(words)
print("Conteo con Counter:", count3)
print("Más común:", count3.most_common(2))  # Top 2

# Iterar diccionarios
for key, value in count.items():
    print(f"{key}: {value}")

# =============================================================================
# 3. SETS - Para elementos únicos y operaciones de conjuntos
# =============================================================================

# Crear set
nums_with_duplicates = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique = set(nums_with_duplicates)
print("Únicos:", unique)

# Operaciones de conjuntos
set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}

print("Unión:", set1 | set2)           # {1, 2, 3, 4, 5, 6, 7, 8}
print("Intersección:", set1 & set2)    # {4, 5}
print("Diferencia:", set1 - set2)      # {1, 2, 3}

# Verificar pertenencia (muy rápido O(1))
print("3 in set1:", 3 in set1)         # True

# =============================================================================
# 4. STRINGS - Manipulación de texto
# =============================================================================

text = "Hello World"

# Operaciones básicas
print("Minúsculas:", text.lower())
print("Mayúsculas:", text.upper())
print("Reemplazar:", text.replace("World", "Python"))
print("Split:", text.split())          # ['Hello', 'World']
print("Join:", "-".join(["a", "b", "c"]))  # "a-b-c"

# Verificaciones
print("Empieza con 'Hello':", text.startswith("Hello"))
print("Termina con 'World':", text.endswith("World"))
print("Contiene 'lo':", "lo" in text)

# Caracteres individuales
print("Primer char:", text[0])
print("Último char:", text[-1])
print("Reversa:", text[::-1])

# =============================================================================
# 5. LOOPS Y ENUMERATE
# =============================================================================

# Loop básico
for i in range(5):
    print(i, end=" ")  # 0 1 2 3 4
print()

# Loop con enumerate (índice + valor)
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Loop con zip (dos listas en paralelo)
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} tiene {age} años")

# =============================================================================
# 6. LIST COMPREHENSIONS - Código más limpio
# =============================================================================

# Crear lista de cuadrados
squares = [x**2 for x in range(10)]
print("Cuadrados:", squares)

# Filtrar pares
evens = [x for x in range(10) if x % 2 == 0]
print("Pares:", evens)

# Transformar strings
words = ["hello", "world", "python"]
upper_words = [w.upper() for w in words]
print("Mayúsculas:", upper_words)

# =============================================================================
# 7. FUNCIONES ÚTILES
# =============================================================================

# any() - True si al menos uno es True
print("any([False, False, True]):", any([False, False, True]))

# all() - True si todos son True
print("all([True, True, True]):", all([True, True, True]))

# map() - Aplicar función a cada elemento
nums = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, nums))
print("Duplicados:", doubled)

# filter() - Filtrar elementos
evens = list(filter(lambda x: x % 2 == 0, nums))
print("Pares con filter:", evens)

# =============================================================================
# 8. ALGORITMOS BÁSICOS COMUNES
# =============================================================================

# 8.1 Encontrar el máximo
def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for num in arr:
        if num > max_val:
            max_val = num
    return max_val

print("Máximo manual:", find_max([3, 7, 2, 9, 1]))

# 8.2 Contar ocurrencias
def count_occurrences(arr, target):
    count = 0
    for num in arr:
        if num == target:
            count += 1
    return count

print("Ocurrencias de 2:", count_occurrences([1, 2, 3, 2, 4, 2], 2))

# 8.3 Reversa de string
def reverse_string(s):
    return s[::-1]
    # O manualmente:
    # result = ""
    # for char in s:
    #     result = char + result
    # return result

print("Reversa:", reverse_string("hello"))

# 8.4 Palíndromo
def is_palindrome(s):
    return s == s[::-1]

print("¿Es palíndromo 'radar'?:", is_palindrome("radar"))

# 8.5 FizzBuzz (clásico)
def fizzbuzz(n):
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

print("FizzBuzz(15):", fizzbuzz(15))

# 8.6 Two Sum (muy común en entrevistas)
def two_sum(nums, target):
    """Encuentra dos números que sumen target"""
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return None

print("Two sum [2,7,11,15], target=9:", two_sum([2, 7, 11, 15], 9))

# 8.7 Encontrar duplicados
def find_duplicates(arr):
    seen = set()
    duplicates = set()
    for num in arr:
        if num in seen:
            duplicates.add(num)
        seen.add(num)
    return list(duplicates)

print("Duplicados:", find_duplicates([1, 2, 3, 2, 4, 5, 3]))

# =============================================================================
# 9. MANEJO DE ERRORES (importante para Codility)
# =============================================================================

def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
    except TypeError:
        return None

print("10 / 2:", safe_divide(10, 2))
print("10 / 0:", safe_divide(10, 0))

# =============================================================================
# 10. TIPS PARA CODILITY
# =============================================================================

"""
TIPS IMPORTANTES:

1. LEE EL PROBLEMA COMPLETO antes de empezar a codear
2. IDENTIFICA los casos edge:
   - Lista vacía []
   - Un solo elemento [1]
   - Todos iguales [5, 5, 5]
   - Negativos [-1, -2, -3]
   
3. PIENSA EN LA COMPLEJIDAD:
   - O(n) es bueno - un loop
   - O(n²) puede ser aceptable para n pequeño - loops anidados
   - O(n log n) es bueno - sorting
   
4. USA ESTRUCTURAS CORRECTAS:
   - ¿Necesitas contar? → dict o Counter
   - ¿Necesitas únicos? → set
   - ¿Necesitas orden? → list
   
5. PRUEBA CON EJEMPLOS:
   - Ejemplo del problema
   - Caso vacío
   - Caso de un elemento
   - Caso grande
   
6. NO TE COMPLIQUES:
   - La solución más simple suele ser la correcta
   - Usa funciones built-in cuando puedas
   
7. MANEJA ERRORES:
   - Verifica que la lista no esté vacía
   - Verifica índices válidos
   - Usa try/except si es necesario
"""

# =============================================================================
# EJERCICIO PRÁCTICO - Intenta resolverlo
# =============================================================================

def ejercicio_1():
    """
    Dada una lista de números, retorna el número que aparece más veces.
    Si hay empate, retorna el menor.
    
    Ejemplo: [1, 2, 2, 3, 3, 3] → 3
    Ejemplo: [1, 1, 2, 2] → 1 (empate, retorna el menor)
    """
    # TU CÓDIGO AQUÍ
    pass

def ejercicio_2():
    """
    Dada una string, retorna True si todos los caracteres son únicos.
    
    Ejemplo: "abcdef" → True
    Ejemplo: "hello" → False (la 'l' se repite)
    """
    # TU CÓDIGO AQUÍ
    pass

def ejercicio_3():
    """
    Dada una lista de números, retorna una nueva lista con los números
    en orden inverso, pero solo los pares.
    
    Ejemplo: [1, 2, 3, 4, 5, 6] → [6, 4, 2]
    """
    # TU CÓDIGO AQUÍ
    pass

# =============================================================================
# SOLUCIONES (no mires hasta intentarlo!)
# =============================================================================

def solucion_1(nums):
    if not nums:
        return None
    count = Counter(nums)
    max_count = max(count.values())
    # Filtrar los que tienen max_count y retornar el menor
    candidates = [num for num, cnt in count.items() if cnt == max_count]
    return min(candidates)

def solucion_2(s):
    return len(s) == len(set(s))

def solucion_3(nums):
    evens = [x for x in nums if x % 2 == 0]
    return evens[::-1]

# Pruebas
print("\n=== SOLUCIONES ===")
print("Ejercicio 1:", solucion_1([1, 2, 2, 3, 3, 3]))
print("Ejercicio 2:", solucion_2("abcdef"))
print("Ejercicio 3:", solucion_3([1, 2, 3, 4, 5, 6]))

print("\n✅ Repaso completado! Ahora practica en HackerRank o LeetCode")
