from graph_io import write_dot, load_graph
from datetime import datetime
from utilities import *

# treating graph as undirected

start = datetime.now()

# dealing with files
# filename = 'colorref_smallexample_2_49.grl'
filename = 'colorref_smallexample_4_7.grl'
# filename = 'colorref_smallexample_4_16.grl'
# filename = 'colorref_smallexample_6_15.grl'
# filename = 'colorref_largeexample_4_1026.grl'
# filename = 'colorref_largeexample_6_960.grl'

with open('coach_wk3/' + filename) as f:
    G = load_graph(f, read_list=True)

# color refinement
init_info = initialization(G[0])
info = color_refinement(init_info)

# processing result
num_graphs = len(G[0])
mappings = extract_color_number_mappings(info)

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

# write to .dot file
for i in range(len(G[0])): # for each graph in graph list
    with open('coach_wk3/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
        write_dot(G[0][i], g)