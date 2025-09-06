# Pow Berechnung
print(f'POW: {pow(7,9,73)}') # 7^9 mod 793

# Berechnung pow mit multiplikation
print(f'Result pow mit multi: {(66**9)*4%73}')
print(f'Result pow mit multi: {(56**59)*57%73}')


# Kehrwert berechnen beim RSA Kryptoverfahren
# Beispiel: 7^-1 mod 1380
# d = 7
# phi(n) = 1380
print(pow(7,-1,1380))

# Berechnung, um zu Verschlüsseln mit RSA
crypt = lambda N, e, n: N ** e % n
S = crypt(20, 7,1457)
print(f'S={S}')

# Berechnung, um zu Entschlüsseln mit RSA
decrypt = lambda S, d, n: S ** d % n
N = decrypt(10, 1183, 1457)
print(f'N={N}')