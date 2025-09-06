# Konkrete Mathematik (nicht nur) für Informatiker

# Aufgabe 49
def congruent_modulo(a, b, n):
    return a % n == b % n

print(congruent_modulo(201, 101, 10))
print(congruent_modulo(201, 101, 19))
print(congruent_modulo(101, 101, 19))
print(congruent_modulo(0, 42, 7))


def fact(n):
    f = 1
    i = 1
    while i <= n:
        f *= i
        i += 1
    return f

print(fact(8) % 256)

def fact_in_c(n):
    f = 1
    i = 1
    while i <= n:
        f = (f * i) % 256 # Simulation eines 8-Bit CPU (2 hoch 8)
        i += 1
    return f

print(fact_in_c(8))