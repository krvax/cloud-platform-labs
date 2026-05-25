"""
PASO 1: EL PROBLEMA — El script que te dan en la entrevista

Escenario: Un ingeniero junior escribió este health checker.
Funciona, pero tarda 10 minutos para 200 servicios.
Tu manager te pide que lo arregles.

Ejecútalo y observa cuánto tarda con solo 5 URLs.
Luego imagina 200...

    python step_01_the_problem.py
"""

import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import requests  # Librería sincrónica (bloqueante)

# ── SERVIDOR LOCAL MOCK (SRE Approach) ──────────────────────────────────
# Levantamos un servidor local que simule la latencia de 2 segundos.
# Usamos ThreadingHTTPServer para procesar peticiones concurrentemente.
class MockHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor para mantener la consola limpia

    def do_GET(self):
        time.sleep(2.0)  # Simula 2 segundos de latencia de red
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "healthy"}')

def start_local_server() -> str:
    # Port 0 le pide al Sistema Operativo cualquier puerto libre automáticamente
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_port}/health"
# ─────────────────────────────────────────────────────────────────────────

def check_health(url: str) -> dict:
    """Hace un GET a la URL y devuelve el resultado."""
    response = requests.get(url)
    return {"url": url, "status": response.status_code}

def main():
    print("🚀 Iniciando Servidor de Pruebas Local...")
    target_url = start_local_server()
    
    # Vamos a simular 5 endpoints en nuestro propio servidor local
    services = [target_url] * 5

    print("⏳ Ejecutando health check SECUENCIAL...\n")
    start = time.time()

    results = []
    for service in services:
        # 🐌 AQUÍ ESTÁ EL PROBLEMA:
        # Cada requests.get() BLOQUEA el programa entero.
        # Python se queda parado esperando la respuesta de red.
        result = check_health(service)
        print(f"  ✅ {result['url']} -> {result['status']}")
        results.append(result)

    elapsed = time.time() - start
    print(f"\n⏱️  Total: {elapsed:.2f} segundos para {len(services)} servicios")
    print(f"📊 Proyección para 200 servicios: ~{elapsed / len(services) * 200:.0f} segundos ({elapsed / len(services) * 200 / 60:.1f} minutos)")
    print("\n❌ Esto es INACEPTABLE para un SRE. Vamos a arreglarlo.\n")

if __name__ == "__main__":
    main()
