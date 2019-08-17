from mytools import *
from collections import ChainMap
from mygrapher import run_graph
import random

class Graph:

    def draw(self):
        self.classify()
        run_graph(self.neighbors, self.order, name=str(self), wait=True, keep_wiggle=True,
                  partit=[set(graph.neighbors.keys()) for graph in self.separation])

    def test_K(self):
        self.is_K = self.bar().test_E()
        return self.is_K

    def test_E(self):
        self.is_E = not any([nodes for node, nodes in self.neighbors.items()])
        return self.is_E

    def test_C(self):
        if set(self.degrees)!={2}:
            self.is_C = False
            return False
        node1 = next(iter(self.nodes()))
        if len(self.neighbors[node1]) == 0:
            self.is_C = False
            return False
        node2 = next(iter(self.neighbors[node1]))
        ring = [node1, node2]
        while ring[len(ring)-1] != ring[0]:
            branches = self.neighbors[ring[len(ring)-1]]-{ring[len(ring)-2]}
            if len(branches) != 1:
                break
            ring.append(next(iter(branches)))
        if len(ring) == 1+len(self.neighbors):
            self.ring = ring
            self.is_C = True
            return True
        self.is_C = False
        return False

    def test_specials(self):
        self.is_specials = dict([(key, self.is_isomorphic_to(SPECIALS[key])) for key in SPECIALS])
        return self.is_specials

    def test_decomposable(self):
        self.decomposition = self.decompose()
        self.is_decomposable = len(self.decomposition) > 1
        return self.is_decomposable

    def test_separable(self):
        self.separation = self.separate()
        self.is_separable = len(self.separation) > 1
        return self.is_separable

    def test_elementary(self):
        self.test_E()
        self.test_K()
        self.test_C()
        self.is_elementary = self.is_E or self.is_K or self.is_C
        return self.is_elementary

    def test_elem_complement(self):
        self.complement = self.bar()
        self.has_elem_complement = self.complement.test_elementary()
        return self.has_elem_complement

    def is_iso_to(self, graph, bijection):
        '''Tests if PARTICULAR dictionary function iso is an isomorphism from self to graph'''
        for node1, nodes in self.neighbors.items():
            for node2 in nodes:
                if not bijection[node2] in graph.neighbors[bijection[node1]]:
                    return False
            for node2 in self.neighbors.keys()-nodes-{node1}:
                if bijection[node2] in graph.neighbors[bijection[node1]]:
                    return False
        return True

    def is_isomorphic_to(self, graph):
        '''Tests if ANY dictionary function iso is an isomorphism from self to graph'''
        if self.degrees != graph.degrees:
            return False
        # A list of lists of dictionaries, to be selected from
        bij_piece_gens = [get_bijections(self.nodes_by_degree[i], graph.nodes_by_degree[i])
                            for i in range(len(self.nodes_by_degree))]
        for bijection_pieces in itertools.product(*bij_piece_gens):
            bijection = dict(ChainMap(*bijection_pieces))
            if self.is_iso_to(graph, bijection):
                return True
        return False

    def classify(self):
        if self.is_classified:
            return True
        self.is_classified = True
        self.classification = False
        self.test_elementary()
        self.test_elem_complement()
        self.test_decomposable()
        self.test_separable()
    
    def __init__(self, neighbors=dict()):
        '''IMMUTABLE graph theoretic class. Neighbors is a dictionary node->set of adjacent nodes.'''
        self.neighbors = neighbors
        self.is_classified = False
        self.order = len(self.neighbors)
        self.degrees = [len(nodes) for node, nodes in self.neighbors.items()]
        self.degrees.sort()
        self.nodes_by_degree = [[node for node, nodes in self.neighbors.items() if len(nodes)==i] for i in set(self.degrees)]
        self.size = sum(self.degrees)
        self.min_degree = min(self.degrees) if len(self.degrees)>0 else 0
        self.numb_triangles = self.numb_triangles()

    def get_size(self):
        self.size = sum([len(nodes) for node, nodes in self.neighbors.items()])

    def bar(self):
        return Graph(dict([(node, self.neighbors.keys()-nodes-{node}) for node, nodes in self.neighbors.items()]))

    def numb_triangles(self):
        count_by_node = 0
        for node, nodes in self.neighbors.items():
            for pair in itertools.combinations(nodes, 2):
                if pair[1] in self.neighbors[pair[0]]:
                    count_by_node += 1
        return int(count_by_node/3)
    
    def subgraph(self, nodes):
        '''returns INDUCED subgraph of inputed nodes'''
        return Graph(dict([(node, self.neighbors[node] & nodes) for node in nodes]))

    def is_subgraph_of(self, graph):
        '''Checks if self is an INDUCED subgraph of graph'''
        for node_list in itertools.combinations(list(graph.neighbors.keys()), self.order):
            if graph.subgraph(set(node_list)) == self:
                return True
        return False
    
    def friends(self, node):
        '''Returns the largest connected subgraph containing node'''
        friends = set([])
        new_friends = {node}
        while new_friends:
            friends |= new_friends
            new_friends = set.union(*[self.neighbors[new_friend]-friends for new_friend in new_friends])
        return friends

    def nodes(self):
        return set(self.neighbors.keys())

    def separate(self):
        '''Returns the graph partitioned into connected subgraphs (list).'''
        nodes_left = self.nodes()
        subgraphs = []
        while nodes_left:
            node = next(iter(nodes_left))
            friends = self.friends(node)
            nodes_left -= friends
            subgraphs.append(self.subgraph(friends))
        return subgraphs

    def up_index_copy(self, shift):
        return Graph(dict([(node+shift, set([n+shift for n in nodes])) for node, nodes in self.neighbors.items()]))

    def combine(self, graph):
        '''Puts the two graphs together into one disjoint graph'''
        shift = len(self.neighbors)
        up_graph = graph.up_index_copy(shift)
        return self.overlap(up_graph)

    def overlap(self, graph2):
        '''Adds the edges of the input graph to self graph'''
        new_neighbors = self.copy_neighbors()
        for node, nodes in graph2.neighbors.items():
            if node in new_neighbors.keys():
                new_neighbors[node].update(nodes)
            else:
                new_neighbors[node] = nodes.copy() #check for sets that arent being copied
        return Graph(new_neighbors)
    
    def join(self, graph):
        '''Puts the graphs together, and connects every node of one with every node of other'''
        shift = len(self.neighbors)
        up_graph = graph.up_index_copy(shift)
        join_graph1 = Graph(dict([(node, set(up_graph.neighbors.keys())) for node in self.neighbors.keys()]))
        join_graph2 = Graph(dict([(node, set(self.neighbors.keys())) for node in up_graph.neighbors.keys()]))
        return self.overlap(join_graph1).overlap(join_graph2).overlap(up_graph)

    def __add__(self, other):
        return self.join(other)

    def __radd__(self, other):
        return other.join(self)

    def decompose(self):
        return [graph.bar() for graph in self.bar().separate()]

    def possibly_K4_sat(self):
        for node1, nodes in self.neighbors.items():
            for node2 in self.nodes()-nodes-{node1}:
                if self.subgraph(self.neighbors[node1] & self.neighbors[node2]).test_E():
                    return False
        return True

    def possibly_K3_sat(self):
        for node1, nodes in self.neighbors.items():
            for node2 in self.nodes()-nodes-{node1}:
                if len(self.neighbors[node1] & self.neighbors[node2]) == 0:
                    return False
        return True

    def contains_K(self, n):
        #poss_nodes = [node if len(nodes)>=n-1 for node, nodes in self.neighbors.items()]
        for nodes in itertools.combinations(set(self.neighbors.keys()), n):
            if self.subgraph(set(nodes)).test_K():
                return True
        return False

    def copy(self):
        return Graph(self.copy_neighbors())

    def copy_neighbors(self):
        return dict([(node, nodes.copy()) for node, nodes in self.neighbors.items()])
    
    def remove_edge(self, node1, node2):
        neighbors = self.copy_neighbors()
        neighbors[node1].remove(node2)
        neighbors[node2].remove(node1)
        return Graph(neighbors)

    def add_edge(self, node1, node2):
        neighbors = self.copy_neighbors()
        neighbors[node1].add(node2)
        neighbors[node2].add(node1)
        return Graph(neighbors)

    def get_edge_removes(self):
        '''Returns the  graphs attained by removing one edge (No duplicates)'''
        for node1, nodes in self.neighbors.items():
            for node2 in nodes:
                if node1 > node2:
                    continue
                yield self.remove_edge(node1, node2)

    def get_rand_edge_removes(self, number):
        '''Returns thegraphs attained by removing n random edge (No duplicates)'''
        for i in range(number):
            node1, nodes = random.choice(list(self.neighbors.items()))
            node2 = random.sample(nodes, 1)[0]
            yield self.remove_edge(node1, node2)

    def get_edge_adds(self):
        '''Returns the  graphs attained by removing one edge (No duplicates)'''
        for node1, nodes in self.neighbors.items():
            for node2 in self.neighbors.keys()-nodes-{node1}:
                if node1 > node2:
                    continue
                yield self.add_edge(node1, node2)

    def __eq__(self, other):
        if self.order != other.order:
            return False
        #check by classification, catches isomorphism
        self.classify()
        other.classify()
        if self.is_K and other.is_K:
            return True, "K"
        if self.is_E and other.is_E:
            return True
        if self.is_C and other.is_C:
            return True
##        if any([self.is_specials[key] and other.is_specials[key] for key in SPECIALS]):
##            return True
        if (self.has_elem_complement and other.has_elem_complement
            and not self.is_elementary and not other.is_elementary):
            return self.complement == other.complement
        if self.is_decomposable and other.is_decomposable:
            return are_reorderings(self.decomposition, other.decomposition)
        if self.is_separable and other.is_separable:
            return are_reorderings(self.separation, other.separation)
        #quicker checks
        #checks isomorphism, very time consuming
        if self.is_isomorphic_to(other):
            return True
        return False

    def get_removes_of_for(self, of_condition, for_condition):
        fors = set()
        valid_removes = set([remove for remove in self.get_edge_removes() if of_condition(remove)])
        while len(valid_removes):
            start = time.time()
            fors |= set([graph for graph in valid_removes if for_condition(graph)])
            valid_removes_list = []
            for graph in valid_removes:
                valid_removes_list += [set([remove for remove in graph.get_edge_removes()
                                           if of_condition(remove)])]
            valid_removes = set.union(*valid_removes_list)
            print("did remove", time.time() - start, len(valid_removes), len(fors))
        return fors
    #K_(6).get_removes_of_for(lambda x : x.possibly_K3_sat(), lambda x : not x.contains_K(3))
    #K_(7).get_removes_of_for(lambda x : x.possibly_K4_sat(), lambda x : not x.contains_K(4))

    def get_rand_removes_of_for(self, of_condition, for_condition):
        fors = set()
        max_numb_removes = 10
        valid_removes = set([remove for remove in self.get_rand_edge_removes(max_numb_removes) if of_condition(remove)])
        while len(valid_removes):
            start = time.time()
            fors |= set([graph for graph in valid_removes if for_condition(graph)])
            valid_removes_list = []
            for graph in valid_removes:
                valid_removes_list += [set([remove for remove in
                                            graph.get_rand_edge_removes(max_numb_removes//len(valid_removes))
                                           if of_condition(remove)])]
            valid_removes = set.union(*valid_removes_list)
            print("did remove", time.time() - start, len(valid_removes), len(fors))
        return fors

    def get_adds_of_for(self, of_condition, for_condition):
        fors = set()
        valid_adds = set([add for add in self.get_edge_adds() if of_condition(add)])
        while len(valid_adds):
            start = time.time()
            fors |= set([graph for graph in valid_adds if for_condition(graph)])
            valid_adds_list = []
            for graph in valid_adds:
                valid_adds_list += [set([add for add in graph.get_edge_adds()
                                           if of_condition(add)])]
            valid_adds = set.union(*valid_adds_list)
            print("did add", time.time() - start, len(valid_adds), len(fors))
        return fors

    #E_(5).get_adds_of_for(lambda x : not x.contains_K(4), lambda x : x.possibly_K4_sat())
    #E_(6).get_adds_of_for(lambda x : not x.contains_K(3), lambda x : x.possibly_K3_sat())

    def __hash__(self):
        return hash(str(self.degrees))

    def __repr__(self):
        return self.__str__()

    def display(self):
        print(self.__str__()+"\tn: "+str(self.order)+"\tmin_degree: "+str(self.min_degree)+"\tK3s: "+str(
            self.numb_triangles)+" "+str_linear_by_xy(self.order, self.numb_triangles, m=2))
    
    def __str__(self):
        resp = ""
        self.classify()
        if self.is_E:
            return "E"+str(self.order)
        elif self.is_K:
            return "K"+str(self.order)
        elif self.is_decomposable:
            return string_join(self.decomposition, "+")
        elif self.is_separable:
            return string_join(self.separation, ".")
        elif self.is_C:
            return "C"+str(self.order)
        elif self.has_elem_complement:
            return str(self.complement)+"*"
        else:
            self.test_specials()
            for key in SPECIALS:
                if self.is_specials[key]:
                    return key
            return "Graph("+str(self.neighbors)+")"

# X, A B B - k3 sats
# R S T - k4 sats
with open('special_graphs.txt','r') as inf:
    SPECIALS = eval(inf.read())
locals().update(SPECIALS)

#explicitly created graph families
def K_(n):
    if n<2:
        return E_(1)
    return Graph(dict([(i, set(range(n))-{i}) for i in range(n)]))

def E_(n):
    return Graph(dict([(i, set()) for i in range(n)]))

def C_(n):
    if n<2:
        return E_(1)
    return Graph(dict([(i, {i-1,i+1}) for i in range(1,n-1)]+[(0,{n-1, 1}), (n-1,{n-2,0})]))

def Super_of_min_degree(min_degree, n):
    return Graph(dict([(0,set(range(1,min_degree+1)))]+
                      [(i, set(range(n))-{i}) for i in range(1,min_degree+1)]+
                      [(i, set(range(n))-{i,0}) for i in range(min_degree+1, n)]))

#finds the k4-sat graphs possible of order n
def K3_graphs(n):
    return E_(n).get_adds_of_for(lambda x : not x.contains_K(3),
                                 lambda x : x.possibly_K3_sat())
def K4_graphs(n):
    return K_(n).get_removes_of_for(lambda x : x.possibly_K4_sat(),
                                    lambda x : not x.contains_K(4))
def rand_K4_graphs(n):
    return K_(n).get_rand_removes_of_for(lambda x : x.possibly_K4_sat(),
                                    lambda x : not x.contains_K(4))
def K4_graphs_d4(n):
    return Super_of_min_degree(4, n).get_removes_of_for(lambda x : x.possibly_K4_sat() and x.min_degree >= 4,
                                    lambda x : not x.contains_K(4))

for i in range(4,10):
    graphs = time_to(rand_K4_graphs, i)
    for graph in graphs:
        graph.display()
    input()
    allk3 = reduce(lambda x, y: x.combine(y), list(graphs))
