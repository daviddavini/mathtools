from mytools import *
import random
import math

def anneal(state, neighbor_states_func, height_func,
           temp_func=lambda t:1/t, ending_temp = 0):
    '''uses simulated annealing, makes steps towards relative max'''
    h1 = height_func(state)
    for t in range_count(1):
        T = temp_func(t)
        if T <= ending_temp:
            return state
        next_state = random.choice(neighbor_states_func(state))
        h2 = height_func(next_state)
        if h2 - h1 > 0 or random.random() < math.e**((h2-h1)/T):
            print(t, state, math.e**((h2-h1)/T))
            state = next_state
            h1 = h2

def climber(state, neighbor_states_func, height_func):
    '''hill-climbing algorithm to first local maximum it can find'''
    h1 = height_func(state)
    for t in range_count(1):
        next_states = neighbor_states_func(state)
        h2, highest_states = maxs(next_states, key=height_func)
        if h2 <= h1:
            return state
        h1 = h2
        state = random.choice(highest_states)

def SBS(state, neighbor_states_func, height_func, N=1):
    '''stochastic beam search, using N parallel hill-climbers'''
    h1 = height_func(state)
    states = random.choices(neighbor_states_func(state), k=N)
    for t in range_count(1):
        neighborss = [neighbor_states_func(s) for s in states]
        next_states = list(set().union(*neighborss))
        states = random.choices(
            next_states, [height_func(state) for state in next_states], k=N)
        states.sort(key=height_func)
        yield states[0]

#anneal(10, lambda x:[x-1, x+1], lambda x:-x*x, lambda t:t)
#climber(10, lambda x:[x-1, x+1], lambda x:-x*x)
