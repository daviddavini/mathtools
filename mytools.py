import time
from operator import mul
from functools import reduce
from collections import Counter
import itertools

def mrod(number, run, mod):
    if number < run:
        return number
    return (number - run) % mod + run

def prod(iterable):
    return reduce(mul, iterable, 1)

def differences(iterable):
    return [iterable[i+1] - iterable[i] for i in range(len(iterable)-1)]

def integrate_differences(start, iterable):
    return [start+sum(iterable[:i]) for i in range(len(iterable)+1)]

def Uniquify(iterable):
    new_iter = list(set(iterable))
    new_iter.sort()
    return new_iter

def uniquify(iterable):
    def _uniquify(iterable):
        seen = set()
        for x in iterable:
            if x in seen:
                continue
            seen.add(x)
            yield x
    return list(_uniquify(iterable))

def commons(list_of_lists):
    '''takes in a list of lists and returns a list of common elements'''
    return list(reduce(lambda x, y: Counter(x) & Counter(y), list_of_lists).elements())

def time_to(func, *args, print_res=True):
    start = time.time()
    res = func(*args)
    if print_res:
        print(res,time.time()-start)
    else:
        print(time.time()-start)
    return res

def timed_repeat(func, args, alloted_time, combiner=lambda x,y:x+y):
    start = time.time()
    combined_output = func(*args)
    reps = 1
    while alloted_time > time.time()-start:
        combined_output = combiner(combined_output, func(*args))
        reps += 1
    return combined_output, reps

def combine_iterator(func, args, combine_func=lambda x,y:x+y):
    combined_output = func(*args)
    while True:
        yield combined_output
        combined_output = combine_func(combined_output, func(*args))

def timed_iterator(iterator, alloted_time):
    start = time.time()
    reps = 1
    while alloted_time > time.time()-start:
        next(iterator)
        reps += 1
    return next(iterator), reps

def maxs(iterable, key=lambda x : x):
    maxs = None
    max_value = None
    for element in iterable:
        value = key(element)
        if maxs == None:
            maxs = [element]
            max_value = value
        elif value > max_value:
            maxs = [element]
            max_value = value
        elif value == max_value:
            maxs.append(element)
    return max_value, maxs

def mins(iterable, key=lambda x : x):
    mins = None
    min_value = None
    for element in iterable:
        value = key(element)
        if mins == None:
            mins = [element]
            min_value = value
        elif value < min_value:
            mins = [element]
            min_value = value
        elif value == min_value:
            mins.append(element)
    return min_value, mins

def range_count(start = 0, end = float('inf'), step = 1):
    if end < float('inf'):
        for i in range(start, end, step):
            yield i
    else:
        for i in itertools.count(start, step):
            yield i

def string_join(iterator, seperator):
    it = map(str, iterator)
    seperator = str(seperator)
    string = next(it, '')
    for s in it:
        string += seperator + s
    return string

def are_reorderings(list1, list2):
    has_paired = [False for elem in list2]
    for i in range(len(list1)):
        found = False
        for j in range(len(list2)):
            if not has_paired[j] and list1[i] == list2[j]:
                has_paired[j] = True
                found = True
                break
        if not found:
            return False
    return True

def get_bijections(list1, list2):
    '''Genarates every dictionary bijections between lists.'''
    if len(list1) == len(list2):
        for perm in itertools.permutations(list2):
            yield dict(zip(list1, perm))

def str_linear_by_xy(x, y, m=1):
    '''creates the integer equation for the line going through a point'''
    b = y - m*x
    if b > 0:
        return str(m) + "x+" + str(b)
    elif b == 0:
        return str(m) + "x"
    else:
        return str(m) + "x" + str(b)

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    xs = list(iterable)
    # note we return an iterator rather than a list
    return itertools.chain.from_iterable(itertools.combinations(xs,n) for n in range(len(xs)+1))
