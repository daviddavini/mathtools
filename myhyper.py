from mytools import *

def exp_chain(base, run, mod):
    equiv_base = mrod(base, run, mod)
    chain = [1]
    next_number = equiv_base
    while next_number not in chain:
        chain.append(next_number)
        next_number = mrod(next_number*equiv_base, run, mod)
    ring_start = chain.index(next_number)
    ring_length = len(chain) - ring_start
    return chain, ring_start, ring_length

def tetra_mod(base, t, mod, run=0):
    if base == 0 and t == float('inf'):
        #print("whoahhhhh there.  what is the inf tetration of 0?  beats me")
        return 0
    if t == 0:
        return 1
    if t == 1:
        return mrod(base, run, mod)
    chain, ring_start, ring_length = exp_chain(base, run, mod)
    if t == float('inf') and mod == 1:
        return chain[-1]
    power = tetra_mod(base, t-1, ring_length, run=ring_start)
    return chain[power]
