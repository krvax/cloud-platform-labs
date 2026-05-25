import ollama
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
import random

console = Console()

# Bridgewater/SRE persona prompt
SYSTEM_PROMPT = """
Eres un Senior Site Reliability Engineer en un hedge fund de alto nivel (estilo Bridgewater). 
Tu misión es mentorear a un ingeniero DevOps que se prepara para sus entrevistas técnicas.
Valoras el 'Leverage' (apalancamiento), la automatización robusta, la observabilidad, la transparencia radical y la búsqueda de la causa raíz.
Sé directo, técnico y proporciona ejemplos de código cuando sea útil.
Tu tono es profesional, exigente pero alentador ('no pain, no gain').
Habla en español (con términos técnicos en inglés).
"""

QUESTIONS = [
    "¿Cuál es la diferencia entre Yield (generadores) y usar una lista para leer un log de 100GB? Explica el impacto en memoria.",
    "¿En qué escenario de SRE usarías `asyncio` en lugar de `multiprocessing`?",
    "Escribe un decorador `@retry` simple en Python que implemente exponential backoff. ¿Por qué es crucial en la nube?",
    "¿Por qué en un entorno crítico de SRE preferimos usar el módulo `logging` en lugar de simplemente usar `print`?",
    "Explícame cómo manejarías de forma segura las credenciales de AWS en un script de Python usando Boto3 en producción.",
    "¿Qué es el GIL en Python y cómo afecta nuestras decisiones de diseño al hacer herramientas SRE concurrentes?"
]

def chat_mode():
    console.print("[bold cyan]🤖 SRE Mentor (Modo Chat)[/bold cyan] Escribe 'salir' para terminar.")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        user_input = Prompt.ask("\n[bold green]Tú[/bold green]")
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        with console.status("[bold yellow]El Mentor está pensando...[/bold yellow]"):
            try:
                response = ollama.chat(model='llama3', messages=messages)
                ai_reply = response['message']['content']
                messages.append({"role": "assistant", "content": ai_reply})
                
                console.print("\n[bold magenta]Mentor:[/bold magenta]")
                console.print(Markdown(ai_reply))
            except Exception as e:
                console.print(f"[bold red]Error al conectar con Ollama: {e}[/bold red]")
                console.print("Asegúrate de que Ollama esté corriendo y tengas el modelo 'llama3' instalado (`ollama run llama3`).")
                break

def quiz_mode():
    console.print("[bold cyan]🎯 SRE Mentor (Modo Quiz)[/bold cyan]")
    question = random.choice(QUESTIONS)
    console.print("\n[bold magenta]Pregunta del Mentor:[/bold magenta]")
    console.print(f"[italic]{question}[/italic]")
    
    console.print("\nPiensa en tu respuesta. Cuando estés listo para ver la respuesta del mentor, presiona Enter.")
    input()
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Hazme una simulación de respuesta excelente de nivel Senior SRE para esta pregunta: '{question}'"}
    ]
    
    with console.status("[bold yellow]Generando la respuesta ideal...[/bold yellow]"):
        try:
            response = ollama.chat(model='llama3', messages=messages)
            ai_reply = response['message']['content']
            console.print("\n[bold green]Respuesta Ideal (Nivel Senior):[/bold green]")
            console.print(Markdown(ai_reply))
        except Exception as e:
            console.print(f"[bold red]Error al conectar con Ollama: {e}[/bold red]")


def main():
    console.print("""
[bold blue]🚀 Bienvenido al AI SRE Mentor (Ollama Powered)[/bold blue]
Elige una opción:
1. Modo Chat Libre (Hazme preguntas sobre Python SRE)
2. Modo Quiz (Te haré una pregunta técnica de entrevista)
3. Salir
    """)
    
    choice = Prompt.ask("Opción", choices=["1", "2", "3"])
    
    if choice == "1":
        chat_mode()
    elif choice == "2":
        quiz_mode()
    else:
        console.print("[yellow]¡Nos vemos! Recuerda: No pain, no gain.[/yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()
