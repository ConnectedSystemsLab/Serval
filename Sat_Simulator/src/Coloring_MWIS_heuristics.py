# -*- coding: utf-8 -*-
""" "Coloring_MWIS_heuristics.py" file contains a greedy heuristic and an exact
recursive heuristic for maximum weighted independent sets
@author: Philippe Chervi"""

from itertools import combinations
from operator import itemgetter
import networkx as nx
from timeit import default_timer

EPS = 1e-6


def greedy_MWIS(graph, pi, threshold, n_shuffle, all_solutions=False):
    ''' compute greedy maximum weighted independent based on a specific node
    ordering and a n_shuffle number of reshuffling of ordering.
    Input items are:
    - graph, a networkx graph
    - pi, a dictionary of dual values
    - threshold, a value of 1.0 or above
    - n_shuffle : number of reshuffles
    - all_solutions: a boolean, True to report all solutions, False otherwise
    It returns:
    - mwis_set, a MWIS as a sorted tuple of nodes
    - mwis_weight (a float), its MWIS weight '''

    from random import shuffle
    assert n_shuffle > 0
    #assert sum(pi) > 0
    # order nodes by maximum (degree X dual value)
    node_list = list(graph.degree)
    node_list.sort(key=itemgetter(1), reverse=True)
    pi_list = list(map(itemgetter(0), node_list))
    # get greedy solution
    best_score_set, best_score = tuple(), 0
    while n_shuffle:
        mwis_set, mwis_weight = tuple(), 0
        for elem in pi_list:
            feasible_iter = ((elem, c) not in graph.edges for c in mwis_set)
            # add elem to mwis_set if not connected
            if all(feasible_iter):
                mwis_set += (elem,)
                mwis_weight += pi[elem]
                # if sum_pi > threshold, update best scores
                if mwis_weight > threshold + EPS:
                    if mwis_weight > best_score + EPS:
                        best_score_set, best_score = mwis_set[:], mwis_weight
                        # report solution based on all_solutions flag
                
        # shuffle pi_list to get a new pre-ordered list of nodes
        shuffle(pi_list)
        n_shuffle -= 1
    # report best solution above threshold of all_solutions = False
    return best_score_set


def exact_MWIS(graph, pi, b_score=0):
    ''' compute mawimum weighted independent set (recursively) using python
    networkx package. Input items are:
    - graph, a networkx graph
    - pi, a dictionary of dual values attached to node (primal constraints)
    - b_score, a bestscore (if non 0, it pruned some final branches)
    It returns:
    - mwis_set, a MWIS as a sorted tuple of nodes
    - mwis_weight, the sum over n in mwis_set of pi[n]'''
    global best_score
    assert sum(pi) > 0
    graph_copy = graph.copy()
    # mwis weight is stored as a 'score' graph attribute
    graph_copy.graph['score'] = 0
    best_score = b_score

    def get_mwis(G):
        '''compute mawimum weighted independent set (recursively) for non
        yet computed sets. Input is a networkx graph, output is the 
        exact MWIS set of nodes and its weight.
        Based on "A column generation approach for graph coloring" from
        Mehrotra and Trick, 1995, using recursion formula:
        MWIS(G union {i}) = max(MWIS(G), MWIS({i} union AN(i)) where
        AN(i) is the anti-neighbor set of node i'''
        global best_score
        # score stores the best score along the path explored so far
        key = tuple(sorted(G.nodes()))
        ub = sum(pi[n] for n in G.nodes())
        score = G.graph['score']
        # if graph is composed of singletons, leave now
        if G.number_of_edges == 0:
            if score + ub > best_score + EPS:
                best_score = score + ub
            return key, ub
        # compute highest priority node (used in recursion to choose {i})
        node_iter = ((n, deg*pi[n]) for (n, deg) in G.degree())
        node_chosen, _ = max(node_iter, key=lambda x: x[1])
        pi_chosen = pi[node_chosen]
        node_chosen_neighbors = list(G[node_chosen])
        pi_neighbors = sum(pi[n] for n in node_chosen_neighbors)
        G.remove_node(node_chosen)
        # Gh = G - {node_chosen} union {anti-neighbors{node-chosen}}
        # For Gh, ub decreases by value of pi over neighbors of {node_chosen}
        # and value of pi over {node_chosen} as node_chosen is disconnected
        # For Gh, score increases by value of pi over {node_chosen}
        Gh = G.copy()
        Gh.remove_nodes_from(node_chosen_neighbors)
        mwis_set_h, mwis_weight_h = tuple(), 0
        if Gh:
            ubh = ub - pi_neighbors - pi_chosen
            if score + pi_chosen + ubh > best_score + EPS:
                Gh.graph['score'] += pi_chosen
                mwis_set_h, mwis_weight_h = get_mwis(Gh)
            del Gh
        mwis_set_h += (node_chosen, )
        mwis_weight_h += pi_chosen
        # Gp = G - {node_chosen}
        # For Gp, ub decreases by value of pi over {node_chosen}
        # For Gh, score does not increase
        mwis_set_p, mwis_weight_p = tuple(), 0
        if G:
            ubp = ub - pi_chosen
            if score + ubp > best_score + EPS:
                mwis_set_p, mwis_weight_p = get_mwis(G)
            del G
        # select case with maximum score
        if mwis_set_p and mwis_weight_p > mwis_weight_h + EPS:
            mwis_set, mwis_weight = mwis_set_p, mwis_weight_p
        else:
            mwis_set, mwis_weight = mwis_set_h, mwis_weight_h
        # increase score
        score += mwis_weight
        if score > best_score + EPS:
            best_score = score
        # return set and weight
        key = tuple(sorted(mwis_set))
        return key, mwis_weight

    return get_mwis(graph_copy)


if __name__ == "__main__":

    sols = []
    for ntest in range(5, 50, 5):
        G = nx.wheel_graph(ntest)
        print("wheel graph, order ", ntest)
        pi = dict(zip(G.nodes(), (1 for i in G.nodes())))

        threshold = 1.0 + EPS
        G_check = G.copy()

        def is_set_independent(mwis_set):
            return all((s, t) not in G_check.edges
                       for (s, t) in combinations(mwis_set, 2))

        start_time = default_timer()
        n_shuffle = len(pi)
        all_solutions = False
        mwis_set, mwis_weight = set(), 0
        for mwis_set, mwis_weight in greedy_MWIS(G, pi, threshold,
                                                 n_shuffle, all_solutions):
            pass
        elapsed = default_timer() - start_time
        print('greedy set', mwis_set)
        sol = ['greedy', ntest, mwis_weight, elapsed]
        sols.append(sol)
        print(sol)
        print('feasible set?', is_set_independent(mwis_set))

        start_time = default_timer()
        mwis_set, mwis_weight = exact_MWIS(G, pi, 0)
        elapsed = default_timer() - start_time
        print('exact set', mwis_set)
        sol = ['exact', ntest, mwis_weight, elapsed]
        sols.append(sol)
        print(sol)
        print('feasible set?', is_set_independent(mwis_set))
        print("\n")

        del G_check
        del G

    for sol in sols:
        print(sol)