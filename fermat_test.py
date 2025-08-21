from random import randrange


def fermat_test(p):
    return randrange(2, p) ** (p - 1) % p == 1


def is_prime_own_solution(p: int, precision: int) -> bool:
    """
    Check if a number is prime using the Fermat primality test.
    :param p: The number to check for primality.
    :param precision: The number of tests to perform for accuracy.
    :return: True if p is probably prime, False if it is composite.
    """
    c = 0
    while c < precision:
        if not fermat_test(p):
            print('Amount of tests:', c + 1)
            return False
        c += 1
    print('Amount of tests:', c)
    return True


def is_prime(p, n):
    c = 0
    for i in range(n):
        if fermat_test(p):
            c += 1
    return c / n


print('is_prime_own_solution:', is_prime_own_solution(83, 10))
print('is_prime_own_solution', is_prime_own_solution(84, 10))

print('is_prime Wahrscheinlichkeit für Fehler:', is_prime(15, 1000))
print('is_prime Wahrscheinlichkeit für Fehler:', is_prime(1515, 1000))
print('is_prime Wahrscheinlichkeit für Fehler:', is_prime(561, 1000))
print('is_prime Wahrscheinlichkeit für Fehler:', is_prime(8911, 1000))
