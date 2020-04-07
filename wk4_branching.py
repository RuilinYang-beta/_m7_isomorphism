from graph_io import write_dot, load_graph
from utilities import *
from datetime import datetime

start = datetime.now()

# ========== wk4 examples ==========
# filename = 'torus24.grl'
# filename = 'trees36.grl'
filename = 'products72.grl'
# filename = 'cubes5.grl'
# filename = 'cubes6.grl'

with open('coach_wk4/' + filename) as f:
    G = load_graph(f, read_list=True)

# ========== wk3 examples ==========
# filename = 'colorref_smallexample_4_7.grl'
# filename = 'colorref_smallexample_6_15.grl'
# with open('coach_wk3/' + filename) as f:
#     G = load_graph(f, read_list=True)

print("{} contains {} graphs, each {} vertices".format(filename, len(G[0]), len(G[0][0].vertices)))


# ============= test on every pair of graph ============
# ========== only applicable to trees36!!! ==========
# num_graphs = len(G[0])
# for p in range(0, num_graphs-1):
#     for q in range(p+1, num_graphs):
#
#         v = extract_vertices(G[0], [p, q])
#
#         start = datetime.now()
#
#         print("{}: graph {} and graph {} has {} isomorphism ".format(filename, p, q, count_isomorphism([], [], v)))
#
#         end = datetime.now()
#         print("It took {} seconds to compute".format(end - start))
#
# print("===== mark, you have reach the end =====")


# ========== test on specific pair of graph ==========
p = 1
q = 5
v = extract_vertices(G[0], [p, q])

print("{}: graph {} and graph {} has {} isomorphism ".format(filename, p, q, count_isomorphism([], [], v)))

end = datetime.now()
print("It took {} seconds to compute".format(end - start))


