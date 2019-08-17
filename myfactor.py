from mytools import *
 
primes = [2]
last_known = 2

def prime_get(index):
    if index < len(primes):
        return primes[index]
    else:
        p_range = prime_range()
        while index >= len(primes):
            next(p_range)
        return primes[index]

def prime_range(end=float("inf")):
    global last_known
    for p in primes:
        if p >= end:
            break
        yield p
    if last_known+1 < end:
        for last_known in range_count(start=last_known+1, end=end):
            if is_prime(last_known):
                primes.append(last_known)
                yield last_known

def least_factor(number):
    max_test = int(number**0.5)
    for p in prime_range(max_test+1):
        if number % p == 0:
            return p
    return number

def is_prime(number):
    return least_factor(number) == number and not number == 1 and not number == 0

def prime_factors(number):
    prime_facs = []
    while number > 1:
        least_fac = least_factor(number)
        prime_facs.append(least_fac)
        number //= least_fac
    return prime_facs

def factors(x):
    def _factors(prime_facs):
        if len(prime_facs) == 0:
            return [1]
        factor = prime_facs.pop()
        rest = _factors(prime_facs)
        return rest + [factor * x for x in rest]
    prime_facs = prime_factors(x)
    return uniquify(_factors(prime_facs))

import time
def test(n):
    start = time.time()
    for prime in prime_range(n):
        print(prime, time.time()-start)
        start = time.time()
        
    
