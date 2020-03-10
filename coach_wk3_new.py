from graph_io import write_dot, load_graph
from graph import *
from datetime import datetime, time
from utilities import *

# treating graph as undirected

start = datetime.now()

# dealing with files
# filename = 'colorref_smallexample_2_49.grl'
# filename = 'colorref_smallexample_4_7.grl'
filename = 'colorref_smallexample_6_15.grl'

with open('coach_wk3/' + filename) as f:
    G = load_graph(f, read_list=True)

# color refinement
info = color_refinement(G[0])

# processing result
num_graphs = len(G[0])
mappings = extract_color_mappings(info, num_graphs)

# interpreting result
for i in range(0, num_graphs-1):
    for j in range(i+1, num_graphs):
        if same_nb(mappings[i], mappings[j]):
            if is_bijection(mappings[i]):
                print("Graph {} and {} is isomorphic".format(i, j))
            else:
                print("Graph {} and {} is potentially isomorphic".format(i, j))

end = datetime.now()
print("It took {} seconds to compute".format(end - start))