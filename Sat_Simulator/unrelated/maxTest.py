import numpy as np
import random
import networkx as nx
size = 80000
adj_0 = np.random.randint(0, 1, (size, size))
a = np.random.rand(size)
print("Adjacency matrix created", adj_0.shape)

grph = nx.from_numpy_matrix(adj_0)
print("Graph created")
min_weights = nx.maximal_independent_set(grph)
print(min_weights)
print("Min weights found")
