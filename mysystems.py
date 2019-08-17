from myfactor import *

def to_digits(number, base=10):
    digs = []
    while number > 0:
        digs.append(number % base)
        number //= base
    digs = digs[::-1]
    return digs

def from_digits(digs, base=10):
    number = 0
    for dig in digs:
        number *= base
        number += dig
    return number

def to_prime_counts(number):
    if number == 1:
        return [0]
    pcounts = []
    pfactors = prime_factors(number)
    for p in prime_range(max(pfactors)+1):
        pcounts.append( pfactors.count(p) )
    pcounts.reverse()
    return pcounts

def from_prime_counts(prime_counts):
    pcounts = prime_counts.copy()[::-1]
    print(pcounts)
    number = 1
    for i in range(len(pcounts)):
        number *= prime_get(i) ** pcounts[i]
    return number

def to_quacks(number):
    if number == 0:
        return 0
    pcounts = to_prime_counts(number)
    return [to_quacks(i) for i in pcounts]

def from_quacks(quacks):
    if quacks == 0:
        return 0
    return from_prime_counts([from_quacks(quack) for quack in quacks])
    
#the mess:

def format_quacks(quacks):
    if quacks == 0:
        return ""
    s = str(quacks)
    s = s.replace('0', '')
    s = s.replace(' ', '')
    return s

def nice(x):
    return format_quacks(to_quacks(x))
