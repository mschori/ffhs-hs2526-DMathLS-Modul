def sieve(n: int) -> list[int]:
    primes = []
    numbers = list(range(2, n))
    c = 2
    while c * c < n:
        for k in range(c, n, c):
            if k in numbers:
                numbers.remove(k)
        primes.append(c)
        c = numbers[0]
    primes.extend(numbers)
    return primes


print(sieve(100))
