from graph_io import write_dot, load_graph
from utilities import *
from datetime import datetime


# ========== reading file ==========
# ---------- wk4 examples ----------
# filename = 'torus24.grl'
filename = 'torus72.grl'
# filename = 'torus144.grl'
# filename = 'products72.grl'
# filename = 'products216.grl'
# filename = 'torus90.grl'
# filename = 'trees36.grl'

# filename = 'torus144.grl'
# --------- files that are mentioned for passing GI ---------
# filename = 'bigtrees3.grl'
# filename = 'cubes6.grl'
#
#
with open('coach_wk4/' + filename) as f:
    G = load_graph(f, read_list=True)

list_of_graphs = G[0]
print("{} contains {} graphs, each {} vertices".format(filename,
                                                       len(list_of_graphs),
                                                       len(list_of_graphs[0].vertices))
                                                       )
# ---------- wk3 examples ----------
# filename = 'colorref_smallexample_2_49.grl'
# filename = 'colorref_smallexample_4_7.grl'
# filename = 'colorref_smallexample_4_16.grl'
# filename = 'colorref_smallexample_6_15.grl'
# filename = 'colorref_largeexample_4_1026.grl'
# filename = 'colorref_largeexample_6_960.grl'
#
# with open('coach_wk3/' + filename) as f:
#     G = load_graph(f, read_list=True)
#
# list_of_graphs = G[0]
# print("{} contains {} graphs, each {} vertices".format(filename,
#                                                        len(list_of_graphs),
#                                                        len(list_of_graphs[0].vertices))
#                                                        )
# ========== finish reading file ==========


start = datetime.now()

# ============= main program ============
# ------------- iter over all graph in a list of graphs ----
for idx in range(0, len(list_of_graphs)):
    one_graph = list_of_graphs[idx]

    all_v, matrix, reference = initialization_automorphism(one_graph)
    X = []

    # last flag is True if want to enable m-test
    count, _ = get_generating_set([], [], all_v, matrix, reference, X, False)
    num_auto = order_computing(X)

    print("graph {} has {} ele in X, and {} automorphisms".format(idx, len(X), num_auto))

# ------------ check specific graph in the graph list
# idx = 3
# one_graph = list_of_graphs[idx]
#
# all_v, matrix, reference = initialization_automorphism(one_graph)
# X = []
#
# count, _ = get_generating_set([], [], all_v, matrix, reference, X, False)
# num_auto = order_computing(X)
#
# print("graph {} has {} ele in X, and {} automorphisms".format(idx, len(X), num_auto))


# ============= end of main program ============

end = datetime.now()
print("It took {} seconds to compute".format(end - start))

# ========== writing file ==========
# for i in range(1): # for each graph in graph list
#     with open('coach_wk3/dot/' + filename[:-4] + '_' + str(1) + '.dot', 'w') as g:
#         write_dot(G[0][i], g)
# ========== end of writing file ==========



