from graph_io import write_dot, load_graph
from datetime import datetime
from utilities import *

# treating graph as undirected

# ========== reading file ==========
# ---------- wk5 examples ----------
# ---------- while the examples here are .gr, all functionalities should accommodate .grl ----------
# filename = 'threepaths5.gr'
# filename = 'threepaths10.gr'
# filename = 'threepaths20.gr'
# filename = 'threepaths40.gr'
# filename = 'threepaths80.gr'
# filename = 'threepaths160.gr'
# filename = 'threepaths320.gr'
# filename = 'threepaths640.gr'
# filename = 'threepaths1280.gr'
# filename = 'threepaths2560.gr'
# filename = 'threepaths5120.gr'
filename = 'threepaths10240.gr'

with open('coach_wk5/' + filename) as f:
    G = load_graph(f)
print("{} contains 1 graphs with {} vertices".format(filename, len(G.vertices)))

list_of_graphs = [G]

# ---------- wk3 examples ----------

# dealing with files
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
#
# list_of_graphs = G[0]
# print("{} contains {} graphs, each {} vertices".format(filename,
#                                                        len(list_of_graphs),
#                                                        len(list_of_graphs[0].vertices))
#                                                        )

# ========== finish reading file ==========


# start time after file-reading
start = datetime.now()


# color refinement
init_info = initialization(list_of_graphs)
info = color_refinement(init_info)

# processing result
num_graphs = len(list_of_graphs)
mappings = from_info_to_mappings(info)

# interpreting result
for i in range(0, num_graphs-1):
    for j in range(i+1, num_graphs):
        if same_dict_value(mappings[i], mappings[j]):
            if is_bijection(mappings[i]):
                print("Graph {} and {} is isomorphic".format(i, j))
            else:
                print("Graph {} and {} is potentially isomorphic".format(i, j))

end = datetime.now()
print("It took {} seconds to compute".format(end - start))


# ========== writing file ==========
# for i in range(len(G[0])): # for each graph in graph list
#     with open('coach_wk3/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
#         write_dot(G[0][i], g)
# ========== end of writing file ==========