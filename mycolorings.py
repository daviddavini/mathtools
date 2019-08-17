from mytools import *
from myfactor import *
from mysystems import *

#1* 2 3* 4 5 6* 7 8

class Coloring:
    def __init__(self, n, blues):
        '''n is integer, blues is list'''
        self.n = n
        self.blues = blues
        self.classified = False

    def flip(self):
        self.blues = [8-i+1 for i in self.blues]
        return self

    def flipped(self):
        '''doesn't modify self, creates new coloring'''
        return Coloring(self.n, [self.n-i+1 for i in self.blues[::-1]])

    def invert(self):
        self.blues = [i for i in range(1,self.n+1) if i not in self.blues]
        return self

    def inverted(self):
        '''doesn't modify self, creates new coloring'''
        return Coloring(self.n,
                        [i for i in range(1,self.n+1) if i not in self.blues])

    def joined(self, other):
        return Coloring(self.n+other.n, self.blues+[i+self.n for i in other.blues])

    def classify(self):
        if not self.classified:
            self.classified = True
            self.self_symmetrical = self.is_self_symm()

    def is_self_symm(self):
        return self.inverted().flipped().blues == self.blues

    def __eq__(self, other):
        if self.n != other.n:
            return False
        return self.blues == other.blues

    def __hash__(self):
        return hash(self.n)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        string = str(self.n)+" "+str(self.blues)
        self.classify()
        if self.self_symmetrical:
            string += " (SS)"
        else:
            string += " (NSS)"
        return string

def all_colorings(n):
    for i in range(n+1):
        for coloring in itertools.combinations(list(range(1,n+1)), i):
            yield Coloring(n, list(coloring))

def all_colorings_reduced(n):
    for i in range((n-1)//2 +1, n+1):
        for coloring in itertools.combinations(list(range(1,n+1)), i):
            yield Coloring(n, list(coloring))

def B_(m, k):
    for n in range_count(start=1):
        contra = has_contra(m, k, n)
        if contra is None:
            return n

def has_contra(m, k, n):
    '''tests for the existence of a coloring with no k-length m-pseudo prog'''
    for coloring in all_colorings_reduced(n):
        if not has_mkPP(m, k, coloring):
            return coloring
    return None

def all_contras(m, k, n):
    for coloring in all_colorings(n):
        if not has_mkPP(m, k, coloring):
            yield coloring

def all_self_sym_contras(m, k, n):
    for coloring in all_colorings_reduced(n):
        if not has_mkPP(m, k, coloring):
            if coloring.is_self_symm():
                yield coloring

def build_contras(m, k, n, previous_contras=None):
    '''Uses n-1's contras to build n's contras (k>=3)'''
    if n < k:
        return set(all_colorings(n))
    if previous_contras is None:
        prev_contras = time_to(build_contras, m, k, n-1, print_res=False)
    else:
        prev_contras = previous_contras
    contras = set([])
    for building_blocks in itertools.product(prev_contras, build_contras(m,k,1)):
        poss_contra = reduce(lambda x,y:x.joined(y), building_blocks)
        if not has_mkPP(m, k, poss_contra):
            contras.add(poss_contra)
    return contras

def B_2(m, k):
    contras = []
    last_contras = None
    for n in range_count(start=k-1):
        last_contras = build_contras(m, k, n, last_contras)
        contras.append((n, last_contras))
        print(n, len(last_contras))
        if len(last_contras) == 0:
            break
    return n, contras[-2][1]

def d_(m, k, l):
    '''returns the smallest n where there exists a l-length mono with contra'''
#check for conditions on k, l, m
    for n in range_count(start=l):
        for part_of_coloring in itertools.combinations(list(range(2,n)), l-2):
            coloring = Coloring(n, [1]+list(part_of_coloring)+[n])
            if not mono_has_mkPP(m, k, coloring):
                return n, coloring

def Travell_UB(m, k):
    '''uses d to find an upper bound for B_2 (when the min mono 'pops' out of bounds)'''
# check for errors
    for l in range_count(start=k):
        d = d_(m,k,l)[0]
        if d > 2*l-1:
            return d

def build_contras2(m, k, n):
    '''Splits n in half, uses n/2's contras to build n's contras (k>=3)'''
    if n < k:
        return set(all_colorings(n))
    prev_contras = time_to(build_contras2, m, k, n//2, print_res=False)
    contras = set([])
    if n%2 == 0:
        prev_contrass = [prev_contras, prev_contras]
    elif n%2 == 1:
        prev_contrass = [prev_contras, prev_contras]
    for building_blocks in itertools.product(*prev_contrass):
        poss_contra = reduce(lambda x,y:x.joined(y), building_blocks)
        if not has_mkPP(m, k, poss_contra):
            contras.add(poss_contra)
    print(n, len(contras))
    return contras

def mono_has_mkPP(m, k, coloring, listed_coloring = None):
    '''tests for the existence of a k-length m-pseudo prog in monochrome'''
    if type(listed_coloring) == list:
        coloring = Coloring(coloring, listed_coloring)
    n = coloring.n
    blues = coloring.blues
    for k_prog in itertools.combinations(blues, k):
        if len(set(differences(k_prog))) <= m:
            return k_prog
    return False

def has_mkPP(m, k, coloring, listed_coloring = None):
    '''tests for the existence of a k-length m-pseudo prog in coloring'''
    if type(listed_coloring) == list:
        coloring = Coloring(coloring, listed_coloring)
    n = coloring.n
    blues = coloring.blues
    blues_2 = coloring.inverted().blues
    if 2*len(blues) >= n:
        major_blues = blues
        minor_blues = blues_2
    else:
        major_blues = blues_2
        minor_blues = blues
    for k_prog in itertools.combinations(major_blues, k):
        if len(set(differences(k_prog))) <= m:
            return k_prog
    
    for k_prog in itertools.combinations(minor_blues, k):
        if len(set(differences(k_prog))) <= m:
            return k_prog
    return False

# rough write-up for greedy avoidance of k-length 2-pseudo progressions
##s = [1,2]
##def up(s):
##    n = set([])
##    for i in range(0, len(s)):
##        for j in range(i+1, len(s)+1):
##            n.add(sum(s[i:j]))
##    for i in range_count(start=1):
##        if i not in n:
##            return s+[i]
##for i in range_count(start=1):
##    s=up(s)
##    print(s)
##    input()
