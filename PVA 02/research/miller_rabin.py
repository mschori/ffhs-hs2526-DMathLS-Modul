from random import randrange


def miller_rabin(p):
    d = p - 1  # Exponent
    c = 0
    while d % 2 == 0:
        d //= 2
        c += 1
    a = randrange(2, p - 1)
    x = (a ** d) % p
    if x == 1 or x == p - 1:  # Wenn der erste Wert 1 oder -1 ist, dann ist p wahrscheinlich prim.
        return True
    while c > 1:
        x = (x ** 2) % p  # Quadrieren des Resultates
        if x == 1:
            return False  # Wenn das Resultat 1 ist, dann ist p nicht prim, da vorher keine -1 gefunden wurde.

        if x == p - 1:  # Die -1 wird ja durch p-1 dargestellt. Weil bei Z89 die -1 die Zahl 88 ist.
            return True  # Wenn das Resultat -1 ist, dann ist p wahrscheinlich prim.
        c -= 1
    return False  # Wenn am Ende noch keine 1 gefunden wurde, dann ist p nicht prim.


print('miller_rabin mit Zahl 89:', miller_rabin(89))  # 89 ist prim
print('miller_rabin mit Zahl 105:', miller_rabin(105))  # 105 ist nicht prim
print('miller_rabin mit Zahl 221:', miller_rabin(221))  # 221 ist nicht prim

"""
Jetzt wollen wir mal die Fehlerwahrscheinlichkeit des Miller-Rabin-Tests untersuchen.
"""
zaehler = 0
anzahl_durchlaeufe = 1000
while anzahl_durchlaeufe > 0:
    if miller_rabin(221):
        zaehler += 1
    anzahl_durchlaeufe -= 1
print('Fehlerwahrscheinlichkeit des Miller-Rabin-Tests für 221:', zaehler / 1000)
