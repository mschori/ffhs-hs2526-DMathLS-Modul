from sympy import prime, factorint, mod_inverse

p, q = prime(50), prime(54)  # Wir ermitteln mit sympy die 50. und 54. Primzahl
print('p:', p, 'q:', q)  # -> p: 229 q: 269
n = p * q  # n ist das Produkt der beiden Primzahlen
phi = (p - 1) * (q - 1)  # phi(n) ist die Eulersche Phi-Funktion für n
print('n:', n, 'phi:', phi)

# Wir wählen eine kleine Zahl e, die teilerfremd zu phi(n) ist
# Dazu verwenden wir die factorint-Funktion von sympy, um die Primfaktorzerlegung von phi(n) zu erhalten
print(factorint(phi))  # -> {2: 3, 3: 1, 5: 1, 19: 1}
e = 7 * 11 * 13  # Wir wählen e = 1001, da es teilerfremd zu phi(n) ist --> auch 7 wäre ok gewesen
print('e:', e)

# Wir berechnen den Kehrwert d von e modulo phi(n)
d = mod_inverse(e, phi)  # d ist der private Schlüssel
print('d:', d)

# Jetzt haben wir e, d und n, die wir für die RSA-Verschlüsselung verwenden können
print('------------')
print('Öffentlicher Schlüssel (e, n):', (e, n))
print('Privater Schlüssel (d, n):', (d, n))

# Beispiel für die Verschlüsselung und Entschlüsselung
# Übermitteln möchten wir die Nachricht N = 52134
N = 52134
print('Nachricht N:', N)

# Verschlüsselung
crypt = lambda x, y: x ** y % n
S = crypt(N, e)  # S ist die verschlüsselte Nachricht
print('Verschlüsselte Nachricht S:', S)

# Entschlüsselung
print('Entschlüsselung der Nachricht S:', crypt(S, d))  # Entschlüsselung der Nachricht