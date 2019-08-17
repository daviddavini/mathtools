from mytools import *
from myfactor import *
from myoptimizers import *
from mysystems import *
from collections import OrderedDict
from random import randint
import time

#1* 2 3* 4 5 6* 7 8

class Coloring:
    def __init__(self, r, n, mapping):
        '''r and n are integers, colorings is list'''
        self.r = r
        self.n = n
        self.mapping = mapping
        if not self.is_valid():
            raise Exception("coloring object is improperly defined: "+self.__str__())
    def is_valid(self):
        return (len(self.mapping)==self.n and
                set(self.mapping).issubset(set(range(self.r))))
    def appended(self, new_element):
        return Coloring(self.r, self.n+1, self.mapping+tuple([new_element]))
    def flipped(self):
        return Coloring(self.r, self.n, self.mapping[::-1])
    def __eq__(self, other):
        if self.r != other.r or self.n != other.n:
            return False
        return self.mapping == other.mapping
    def __hash__(self):
        return hash(self.r*self.n)
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        string = "Coloring("+str(self.r)+","+str(self.n)+","+str(self.mapping)+")"
        return string
    def adj_colorings(self):
        colorings = []
        for i in range(self.n):
            for j in range(self.r):
                colorings += [Coloring(self.r, self.n,
                                      self.mapping[:i]+[j]+self.mapping[i+1:])]
        return colorings
    def all_as(self, k):
        '''returns all arith. subsequences'''
        for a in range(self.n-k+1):
            for d in range(1, (self.n-1-a)//(k-1)+1):
                yield self.mapping[a:a+(k-1)*d+1:d]
    def all_ras(self, k):
        for seq in filter(is_rainbow, self.all_as(k)):
            yield seq
    def all_mas(self, k):
        for seq in filter(is_monochrome, self.all_as(k)):
            yield seq
    def numb_of_ras(self, k):
        '''returns the number of k-term rainbow arith. sequences'''
        return len(list(filter(is_rainbow, self.all_as(k))))
    def numb_of_mas(self, k):
        '''returns the number of k-term monochromatic arith. sequences'''
        return len(list(filter(is_monochrome, self.all_as(k))))
    def recurs_all_as(self, k):
        '''generator for all the new a.s. that the last element (integer) creates'''
        for d in range(1, (self.n-1)//(k-1)+1):
                yield self.mapping[self.n-1-(k-1)*d:self.n:d]
    def recurs_numb_of_ras(self, k):
        return len(list(filter(is_rainbow, self.recurs_all_as(k))))
    def uniquified_colors(self):
        iso_func = [None for i in range(self.r)]
        r = 0
        for m in self.mapping:
            if iso_func[m] is None:
                iso_func[m] = r
                r += 1
        return Coloring(self.r, self.n, [iso_func[m] for m in self.mapping])
    def uniquified(self):
        coloringA = self.uniquified_colors()
        coloringB = self.flipped().uniquified_colors()
        for i in range(self.n):
            if coloringA.mapping[i] > coloringB.mapping[i]:
                return coloringB
            if coloringA.mapping[i] < coloringB.mapping[i]:
                return coloringA
        return coloringA

    @classmethod
    def all(cls, r, n):
        "iterator for all r**n r-colorings of [n]"
        for mapping in itertools.product(*[range(r) for i in range(n)]):
            yield Coloring(r,n,mapping)
    @classmethod
    def random(cls, r, n):
        return Coloring(r,n,[randint(0, r-1) for i in range(n)])
    @classmethod
    def randoms(cls, r, n, sample_size):
        for i in range(sample_size):
            yield Coloring(r,n,[randint(0, r-1) for i in range(n)])
    @classmethod
    def R(cls, r, n):
        return Coloring(r, n, [i%r for i in range(n)])
    
def is_rainbow(sequence):
    return len(set(sequence)) == len(sequence)

def is_monochrome(sequence):
    return len(set(sequence)) == 1

def max_ras(k, colorings):
    max_ras, max_colorings = maxs(colorings, key=lambda c:c.numb_of_ras(k))
    return max_ras, list(set([c.uniquified() for c in max_colorings]))

def min_mas(k, colorings):
    min_mas, min_colorings = mins(colorings, key=lambda c:c.numb_of_mas(k))
    return min_mas, list(set([c.uniquified() for c in min_colorings]))

#functions that find the Coloring with the max ras

def timed_rand_max_ras2(r, n, k, alloted_time):
    best_coloring, total_sample_size = timed_repeat(Coloring.random, (r, n), alloted_time,
                        combiner = lambda c1, c2:max(c1, c2, key=lambda c:c.numb_of_ras(k)))
    return best_coloring.uniquified(), total_sample_size

def timed_climb_max_ras(r, n, k, alloted_time):
    def climbed_rand():
        return climber(Coloring.random(r,n),
                   lambda c:Coloring.adj_colorings(c),
                   lambda c:c.numb_of_ras(k))
    best_coloring, total_sample_size = timed_repeat(climbed_rand, (), alloted_time,
                        combiner = lambda c1, c2:max(c1, c2, key=lambda c:c.numb_of_ras(k)))
    return best_coloring.uniquified(), total_sample_size

def timed_SBS_max_ras(r, n, k, alloted_time):
    SBS_rand = SBS(Coloring.random(r,n),
                    lambda c:Coloring.adj_colorings(c),
                    lambda c:c.numb_of_ras(k), N=3)
    best_coloring, total_sample_size = timed_iterator(SBS_rand, alloted_time)
    return best_coloring.uniquified(), total_sample_size

def timed_climb_min_mas(r, n, k, alloted_time):
    def climbed_rand():
        return climber(Coloring.random(r,n),
                   lambda c:Coloring.adj_colorings(c),
                   lambda c:-c.numb_of_mas(k))
    best_coloring, total_sample_size = timed_repeat(climbed_rand, (), alloted_time,
                        combiner = lambda c1, c2:min(c1, c2, key=lambda c:c.numb_of_mas(k)))
    return best_coloring.uniquified(), total_sample_size

def timed_rand_max_ras(r, n, k, alloted_time):
    start = time.time()
    total_sample_size = 0
    sample_size = 1
    best_coloring = None
    best_ras = 0
    while sample_size > 0:
        total_sample_size += sample_size
        sample_start = time.time()
        coloring = max(Coloring.randoms(r,n, sample_size), key=lambda c:c.numb_of_ras(k))
        if coloring.numb_of_ras(k) > best_ras:
            best_coloring = coloring
            best_ras = coloring.numb_of_ras(k)
        sample_size = int((alloted_time-(time.time()-start))*
                          (sample_size/(time.time()-sample_start)))
    return best_coloring.uniquified(), best_ras, total_sample_size

def recurs_max_ras(r, n, k):
    '''uses recursion to only check colorings that are "in the running"'''
    def inner_recurs_max_ras_coloring(r, n, k, itr_ras_range=0):
        colorings = []
        if n < k:
            colorings = [(c, c.numb_of_ras(k)) for c in Coloring.all(r,n)]
        else:
            old_itr_ras_range = itr_ras_range + (r-k+1)*((n-1)//(k-1)) #possible error
            old_best_coloring, old_best_ras, old_itr_colorings = inner_recurs_max_ras_coloring(
                r, n-1, k, itr_ras_range=old_itr_ras_range)
        
            for c, numb_of_ras in old_itr_colorings:   
                for i in range(r):
                    new_c = c.appended(i)
                    new_numb_of_ras = numb_of_ras + new_c.recurs_numb_of_ras(k)
                    colorings.append((new_c, new_numb_of_ras))

        best_coloring, best_ras = max(colorings, key=lambda c:c[1])
        itr_colorings = list(filter(lambda c: c[1] >= best_ras - itr_ras_range, colorings))
        return best_coloring, best_ras, itr_colorings

    return inner_recurs_max_ras_coloring(r,n,k)[:2]

def compare_max_ras(r, n, k, alloted_time=3):
    best_coloring = Coloring.R(r,n)
    print(best_coloring, best_coloring.numb_of_ras(k))
    searchers = [lambda:timed_climb_max_ras(r,n,k,alloted_time),
                  lambda:timed_rand_max_ras(r,n,k,alloted_time),
                  lambda:recurs_max_ras(r,n,k)]
    for searcher in searchers:
        data = searcher()
        print(data, data[0].numb_of_ras(k))

def compare_min_mas(r, n, k, alloted_time=3):
    searchers = [lambda:timed_climb_min_mas(r,n,k,alloted_time)]
    for searcher in searchers:
        data = searcher()
        print(data, data[0].numb_of_mas(k))
    best_coloring = min_mas(k, Coloring.all(r, n))[1][0]
    print(best_coloring, best_coloring.numb_of_mas(k))

