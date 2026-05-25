"""
PASO 5: SIMULADOR DE ENTREVISTA INTERACTIVO CON OLLAMA (WSL/Windows)

Este script se conecta a tu instancia local de Ollama (que corre nativa en Windows)
y simula un entrevistador de Bridgewater Associates de nivel Principal SRE.

Adopta la cultura de "Radical Transparency" e "Idea Meritocracy".
¡Te evaluará de forma brutalmente honesta!

Requisitos:
- Tener Ollama corriendo.
- Tener algún modelo descargado (ej. llama3, codellama, etc.)

Ejecutar:
    python step_05_ollama_mock_interviewer.py
"""

import asyncio
import sys
import json
import httpx

OLLAMA_HOST = "http://localhost:11434"

SYSTEM_PROMPT = """
You are a Principal Site Reliability Engineer at Bridgewater Associates. 
Your interviewing style is deeply rooted in Bridgewater's culture of "Radical Transparency" and "Idea Meritocracy".
You are evaluating a candidate (Miguel) for a Senior Python SRE role.

RULES FOR YOUR BEHAVIOR:
1. Be direct, precise, and brutally honest (Radical Truth). Do not sugarcoat evaluations.
2. Value engineering leverage, automation, scalability, safety (dry-runs), observability, and robust error handling above everything else.
3. If the candidate gives a shallow or textbook generic answer, challenge them immediately.
4. You are assessing if they think like a Senior+ SRE (who builds systems) or a Mid-level developer (who just writes code snippets).

STRUCTURE OF THE INTERVIEW:
- Ask ONE high-stakes Python SRE question at a time (GIL, Memory-efficient generation, Async concurrency vs Multiprocessing, AWS auditing via Boto3, Mock-testing infrastructure, Error decorators).
- Wait for the candidate's answer.
- When they answer:
  1. Give a "Radically Transparent Evaluation": Rate their answer from 1 to 10.
  2. Point out exactly what they missed (e.g., "You forgot to mention memory limits", "You didn't consider rate limits").
  3. Give them a SRE Seniority Rating for that answer: [Junior / Mid / Senior / Staff / Principal].
  4. Ask the next challenging follow-up question.
"""

async def check_ollama():
    """Verifica si Ollama está corriendo en localhost."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                return models
        except Exception:
            return None

async def chat_with_ollama(model: str, messages: list):
    """Envía la conversación a Ollama y streamea la respuesta en la consola."""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            
            # Usamos streaming para que se sienta como una conversación real
            async with client.stream("POST", f"{OLLAMA_HOST}/api/chat", json=payload, timeout=60.0) as response:
                if response.status_code != 200:
                    print(f"\n❌ Error de Ollama: HTTP {response.status_code}")
                    return ""
                
                full_reply = ""
                async for chunk in response.aiter_lines():
                    if chunk:
                        data = json.loads(chunk)
                        content = data.get("message", {}).get("content", "")
                        print(content, end="", flush=True)
                        full_reply += content
                return full_reply
        except Exception as e:
            print(f"\n❌ Error al conectar con Ollama: {e}")
            return ""

async def main():
    print("🤖 Simulador de Entrevista de Bridgewater SRE con Ollama 🤖")
    print("Checking connection to Ollama...")
    
    available_models = await check_ollama()
    
    if not available_models:
        print("\n❌ ERROR: No se pudo conectar a Ollama en http://localhost:11434")
        print("Asegúrate de:")
        print("  1. Que la aplicación Ollama en Windows esté abierta.")
        print("  2. Que tengas modelos instalados corriendo 'ollama list'.")
        sys.exit(1)
        
    print(f"✅ Conexión exitosa. Modelos encontrados: {available_models}")
    
    # Elegir modelo
    model = available_models[0]
    if len(available_models) > 1:
        print("\nElige qué modelo usar:")
        for idx, m in enumerate(available_models):
            print(f"  [{idx}] {m}")
        try:
            sel = int(input("\nSelección (número): "))
            model = available_models[sel]
        except Exception:
            print(f"Selección no válida. Usando por defecto: {model}")
            
    print(f"\n🚀 Iniciando simulación con el modelo: {model}")
    print("Recuerda las reglas de Bridgewater: Verdad Radical, Transparencia Radical.")
    print("Escribe 'exit' o 'salir' en cualquier momento para terminar.\n")
    print("─────────────────────────────────────────────────────────────────────────────")
    
    # Historial de mensajes
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hello. I am Miguel, applying for the Senior Python SRE position at Bridgewater. Let's start the interview."}
    ]
    
    # Primer prompt del entrevistador
    print("🤖 Entrevistador (Bridgewater SRE): ", end="")
    bot_reply = await chat_with_ollama(model, messages)
    messages.append({"role": "assistant", "content": bot_reply})
    print("\n")
    
    # Loop de entrevista
    while True:
        try:
            user_input = input("✍️ Tu respuesta (Miguel): ")
            if user_input.lower() in ["exit", "salir", "quit"]:
                print("\n👋 Entrevista finalizada. ¡Mucho éxito el miércoles!")
                break
                
            if not user_input.strip():
                continue
                
            messages.append({"role": "user", "content": user_input})
            print("\n🤖 Entrevistador (Bridgewater SRE): ", end="")
            
            bot_reply = await chat_with_ollama(model, messages)
            messages.append({"role": "assistant", "content": bot_reply})
            print("\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Entrevista interrumpida. ¡Hasta luego!")
            break

if __name__ == "__main__":
    asyncio.run(main())
