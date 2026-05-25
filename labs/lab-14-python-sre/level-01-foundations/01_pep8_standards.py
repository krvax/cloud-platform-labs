"""
NIVEL 1: Fundamentos (PEP 8 y Código Limpio)

En SRE, el código es infraestructura. Si no es legible, es peligroso.
Este script muestra el contraste entre código "estilo script" y "estilo ingeniería".

Bridgewater Angle: 'Radical Transparency' requiere que tu código pueda ser leído
y entendido rápidamente por tus pares para facilitar la colaboración y revisión.
"""

# ❌ ESTILO SCRIPT (No recomendado para SRE)
def getinfo(a,b):
    if a=="":return False
    else:
        # hace una request
        res = {"user":a,"id":b,"status":"active"}
        return res

# ✅ ESTILO INGENIERÍA (Senior SRE - PEP 8 Compliant)
def fetch_user_information(username, user_id):
    """
    Recupera la información del estado del usuario desde el backend.
    
    Args:
        username (str): El nombre de usuario.
        user_id (int): El ID único del usuario.
        
    Returns:
        dict: Los datos del usuario si es exitoso, False en caso contrario.
    """
    if not username:
        return False
        
    # Todo script SRE debe ser legible como un libro.
    user_data = {
        "user": username,
        "id": user_id,
        "status": "active"
    }
    
    return user_data

if __name__ == "__main__":
    # Siempre usa este bloque. Evita que el código se ejecute accidentalmente 
    # si alguien importa este archivo como un módulo.
    print("Demostración de código SRE: Mantenibilidad sobre 'hacks'")
    
    result = fetch_user_information("jdoe", 101)
    print(f"Resultado: {result}")
