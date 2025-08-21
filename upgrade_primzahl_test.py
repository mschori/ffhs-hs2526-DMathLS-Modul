import math

# Dieser Primzahltest ist effizienter als der naive Test, aber immer noch zu langsam.

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


x = []
y = 2
while len(x) < 20:
    if is_prime(y):
        x.append(y)
    y += 1

print(x)
