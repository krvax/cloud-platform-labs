"""
Codility Assessment — 2026-05-06
Score: 100% (2/2 tasks perfect)

Resultados:
  - largest_letter:      Correctness 100% | Performance 100% | Task Score 100%
  - generate_palindrome: Correctness 100% | Task Score 100%
"""


# =============================================================================
# Task 1: largest_letter
# =============================================================================
# Dado un string S, encontrar la letra alfabéticamente más grande que aparezca
# tanto en minúscula como en mayúscula. Si no existe, retornar "NO".
#
# Ejemplos:
#   "aaBabcDaA"   → "B"  (A y B aparecen en ambos casos; B es mayor)
#   "Codility"    → "NO" (ninguna letra aparece en ambos casos)
#   "WeTestCodErs" → "T" (E y T aparecen en ambos; T es mayor)
# =============================================================================

def solution_largest_letter(S):
    lowercase = set(c for c in S if c.islower())
    uppercase = set(c for c in S if c.isupper())

    # Intersección: letras que aparecen en ambos casos
    both = set(c.upper() for c in lowercase) & set(c for c in uppercase)

    if not both:
        return "NO"

    return max(both)


# =============================================================================
# Task 2: generate_palindrome
# =============================================================================
# Dados dos enteros N y K, retornar un palíndromo de longitud N que consista
# en exactamente K letras minúsculas distintas (a-z).
#
# Ejemplos:
#   N=5, K=2 → "ababa"
#   N=8, K=3 → "abcaacba"
#   N=3, K=2 → "aba"
#
# Estrategia: construir la primera mitad ciclando las primeras K letras del
# abecedario, luego espejar para garantizar el palíndromo.
# =============================================================================

def solution_generate_palindrome(N, K):
    letters = 'abcdefghijklmnopqrstuvwxyz'[:K]
    half = (N + 1) // 2
    first = [letters[i % K] for i in range(half)]
    result = first + first[:N // 2][::-1]
    return ''.join(result)


# =============================================================================
# Tests
# =============================================================================

if __name__ == "__main__":
    # Task 1
    print("=== Task 1: largest_letter ===")
    assert solution_largest_letter("aaBabcDaA") == "B"
    assert solution_largest_letter("Codility") == "NO"
    assert solution_largest_letter("WeTestCodErs") == "T"
    print("[OK] Todos los tests pasaron")

    # Task 2
    print("\n=== Task 2: generate_palindrome ===")
    for n, k in [(5, 2), (8, 3), (3, 2), (1, 1)]:
        result = solution_generate_palindrome(n, k)
        is_palindrome = result == result[::-1]
        distinct = len(set(result))
        status = "[OK]" if is_palindrome and distinct == k else "[FAIL]"
        print(f"  {status} N={n}, K={k} -> '{result}' (palindrome={is_palindrome}, distinct={distinct})")
