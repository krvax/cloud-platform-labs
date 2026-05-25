"""
PASO 2: EL DIAGNÓSTICO — ¿POR QUÉ es lento?

Este archivo NO tiene código ejecutable. Es tu guión mental.
Léelo en voz alta como si estuvieras en la entrevista.

Cuando el entrevistador te pregunte "Why is this slow?", 
esto es lo que dices:

─────────────────────────────────────────────────────────────
"""

DIAGNOSIS = """
🎤 TU RESPUESTA EN LA ENTREVISTA:

"The main issue is that the script is performing BLOCKING I/O sequentially.

Let me explain what that means:

1. BLOCKING: When we call `requests.get(url)`, Python sends the HTTP 
   request and then STOPS. It literally waits doing nothing until the 
   server responds. This is called 'blocking I/O'.

2. SEQUENTIAL: Because it's inside a `for` loop, each request must 
   COMPLETE before the next one STARTS.

   Timeline:
   
   Service 1: [████████████]                              2 sec
   Service 2:              [████████████]                  2 sec  
   Service 3:                            [████████████]    2 sec
   ─────────────────────────────────────────────────────────
   Total:                                                  6 sec

   With 200 services at ~2 sec each = ~400 seconds = ~6.7 minutes.

3. THE FIX: We need CONCURRENT, NON-BLOCKING I/O.
   
   Instead of waiting for each response, we fire ALL requests 
   simultaneously and collect the results:

   Service 1: [████████████]    2 sec
   Service 2: [████████████]    2 sec (runs at the same time!)
   Service 3: [████████████]    2 sec (runs at the same time!)
   ─────────────────────────────────────────────────────────
   Total:                       2 sec (!)

4. THE TOOL: Python's `asyncio` with `httpx.AsyncClient`.
   
   - asyncio uses a single-threaded EVENT LOOP
   - When one request is waiting for network, the loop runs another
   - httpx is the async-compatible HTTP library (requests is NOT async)
   
5. WHY NOT THREADING?
   Threading would also work for I/O, but asyncio is more efficient:
   - Threads consume OS resources (stack memory per thread)
   - 200 threads = ~200MB of stack memory
   - asyncio handles 200 coroutines in ~1MB
   - For I/O-bound tasks with many connections, asyncio wins"
"""


if __name__ == "__main__":
    print(DIAGNOSIS)
    print("\n💡 Ahora abre step_03_async_solution.py para ver la solución.")
