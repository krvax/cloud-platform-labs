"""
NIVEL 2: Módulo Collections

Los SRE procesan datos: conteos de errores HTTP, top IPs maliciosas, 
estructuras de diccionarios complejos, etc.

`collections` tiene herramientas en C altamente optimizadas:
- Counter: Para contar ocurrencias (ej. status codes).
- defaultdict: Diccionarios que no tiran KeyError si la clave no existe.
- deque: Colas thread-safe para procesar tareas estilo FIFO/LIFO.
"""

from collections import Counter, defaultdict, deque
import random

def demo_counter():
    print("--- 1. COUNTER ---")
    # Simulamos un log de códigos HTTP
    http_statuses = [random.choice([200, 200, 200, 404, 500, 502, 503]) for _ in range(1000)]
    
    # ❌ INCORRECTO: 
    # counts = {}
    # for status in http_statuses:
    #     if status in counts: counts[status] += 1
    #     else: counts[status] = 1
        
    # ✅ CORRECTO (SRE):
    status_counter = Counter(http_statuses)
    print(f"Total códigos: {status_counter}")
    print(f"Top 2 códigos más comunes: {status_counter.most_common(2)}\n")

def demo_defaultdict():
    print("--- 2. DEFAULTDICT ---")
    # Simulamos clasificar logs por servicio
    logs = [
        ("auth-svc", "Failed login"),
        ("db-svc", "Timeout"),
        ("auth-svc", "Invalid Token"),
    ]
    
    # ✅ Si la llave no existe, inicializa una lista automáticamente vacía.
    service_logs = defaultdict(list)
    for service, error in logs:
        service_logs[service].append(error)
        
    print(dict(service_logs), "\n")

def demo_deque():
    print("--- 3. DEQUE (Double-ended queue) ---")
    # Ideal para mantener una "ventana rodante" (ej. los últimos 5 errores en memoria)
    # Es mucho más rápido hacer append/pop a los lados que una lista normal.
    recent_errors = deque(maxlen=3)
    
    for i in range(5):
        error_msg = f"Exception-{i}"
        recent_errors.append(error_msg)
        print(f"Añadido {error_msg}. Estado de la cola: {list(recent_errors)}")
        
    print("Observa cómo Exception-0 y Exception-1 desaparecieron automáticamente.")

if __name__ == "__main__":
    demo_counter()
    demo_defaultdict()
    demo_deque()
