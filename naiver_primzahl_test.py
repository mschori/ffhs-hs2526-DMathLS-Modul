def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, n):
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