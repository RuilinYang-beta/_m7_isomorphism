from graph_io import write_dot, load_graph
from utilities import *
from datetime import datetime
from SimpleVertex import SimpleVertex
from permv2 import *

# ================== temp section ==================


def initialization_automorphism(g: "Graph"):
    """
    - For each vertex v in g, generate two SimpleVertex object v' and v'', with the same v.label,
    but v'.graph_idx = 0, v'.graph_idx = 1. These two number together can uniquely identify a SimpleVertex obj.
    - In the process make an adjacency matrix, because when Vertex --> SimpleVertex,
    the neighborhood information is lost, so need an external structure to store neighborhood info.
    - Also, make a dictionary of reference, that maps each (graph_idx, label) pair to a SimpleVertex object.
    So that each SimpleVertex obj, through adj.matrix can find its neighbor,
    and through reference can actually refer back to the SimpleVertex, to get the color of its neighbor.
    Return:
        - new_vs: list of SimpleVertex that contains "vertex" of G and G',
                  which now **only** have two attr: v.graph_idx and v.label
        - mtx: an adjacency matrix recording the neighbouring info in the original graph,
               with the format { (graph_idx, label):   { (graph_idx, label):  1 } }
        -ref: a reference dict to refer back to the simplevertex obj,
              with format  { (graph_idx, label):  simple_vertex_obj }
    """
    # a dict of format { (graph_idx, label):   { (graph_idx, label):  1 }},
    mtx = {}
    # all the new SimpleVeretx
    new_vs = []
    # a dict of format { (graph_idx, label):  simple_vertex_obj},
    # is used to traceback to the simplevertex v2 that is neighboring to v1
    ref = {}
    # init v.label and v.graph_idx
    for v in g.vertices:
        new_v0 = SimpleVertex(0, v.label)
        new_vs.append(new_v0)
        ref[(0, v.label)] = new_v0

        new_v1 = SimpleVertex(1, v.label)
        new_vs.append(new_v1)
        ref[(1, v.label)] = new_v1

        # --- record v in mtx ---
        mtx[(0, v.label)] = {}
        mtx[(1, v.label)] = {}
        for nb in v.neighbours:
            mtx[(0, v.label)][(0, nb.label)] = 1
            mtx[(1, v.label)][(1, nb.label)] = 1

    return new_vs, mtx, ref


def get_generating_set(D, I, other, matrix, reference, X):
    """
    Require:
        - len(D) == len(I)
        - assuming v in D and u in I has a bijection relationship
    Params:
        - D: a subset of vertices of a graph G
        - I: a subset of vertices of the same graph G
        - other: all the other vertices in the graphs of interest that do not have a bijection relationship yet
        - matrix: adjacency matrix of the format { (graph_idx, label):   { (graph_idx, label):  1 } }
        - reference: a reference dict to refer back to the simplevertex obj,
              with format  { (graph_idx, label):  simple_vertex_obj }
        - X: a list of permutation found so far that forms automorphism
    Return:
        - number of isomorphisms between the (two) graphs of interest
        - X: a list of permutation that forms automorphism
    """
    # ===== [1] get info from D + I + other =====
    init_info = get_info(D, I, other, True, matrix, reference)

    # ===== [2] coarsest stable info under the assumption that D_i and I_i bijection =====
    st_info = color_refinement(init_info, True, matrix, reference)

    # ===== [3] quick check =====
    bijection, unbalanced = check_balanced_bijection(st_info)

    # print("bijection: {}; unbalanced: {}".format(bijection, unbalanced))

    if unbalanced:
        return 0, False
    if bijection:
        trivial, perm_list = process_bijection_info(st_info)
        if trivial:
            return 1, False      # non_trivial_found is False
        else:
            # print("non trivial found: {}".format(st_info))
            X.append(permutation(len(perm_list), mapping=perm_list))   # add the perm_list to X
            return 1, True

    # ===== [4] recursion comes into play when info is balanced =====
    for key in st_info:
        if len(st_info[key]) >= 4:
            break

    if len(D) == 0:
        fromG, fromH = stratify_vertices(st_info[key])
    else:
        fromG, fromH = stratify_vertices(st_info[key], D[0].graph_idx)

    x = fromG[0]
    num = 0
    reorder_fromH(x, fromH)
    for y in fromH:
        new_D = D + [x]
        new_I = I + [y]
        new_other = list(filter(lambda ele: ele is not x and ele is not y, other))

        num_found, non_trivial_auto_found = get_generating_set(new_D, new_I, new_other, matrix, reference, X)
        num += num_found

        if non_trivial_auto_found:
            # upon finding the first non-trivial automorphism, don't spawn more branches
            break

    return num, False


def reorder_fromH(x, fromH):
    """
    Reorder fromH in place such that if there is a v in fromH, v is swapped to the first position of fromH.
    """
    if fromH[0].label == x.label:
        return

    for i in range(len(fromH)):
        if fromH[i].label == x.label:
            fromH[0], fromH[i] = fromH[i], fromH[0]

    return


def process_bijection_info(info):
    """
    Require:
        - info forms a bijection, ie. every color class has exactly 2 (simple) vertices,
          and they have diff v.graph_idx
    """
    # a mapping from graph 0 vertex to graph 1 vertex
    mappings = {}
    for color in info:
        group = info[color]
        if group[0].graph_idx == 0:
            mappings[group[0].label] = group[1].label
        elif group[0].graph_idx == 1:
            mappings[group[1].label] = group[0].label
        else:
            print("You shouldn't reach here.")

    perm_list = []
    for key in sorted(mappings.keys()):
        perm_list.append(mappings[key])

    trivial = None
    if is_trivial(perm_list):
        trivial = True
    else:
        trivial = False

    return trivial, perm_list





def is_trivial(perm_list):
    for i in range(len(perm_list)):
        if i != perm_list[i]:
            return False

    return True



# ================== end of temp section ==================

# ========== reading file ==========
# ---------- wk4 examples ----------
# filename = 'torus24.grl'
# filename = 'torus90.grl'
# filename = 'trees36.grl'
filename = 'products72.grl'
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
idx = 0
one_graph = list_of_graphs[idx]

all_v, matrix, reference = initialization_automorphism(one_graph)

X = []

count, _ = get_generating_set([], [], all_v, matrix, reference, X)

print("graph {} of file {} has {} automorphisms".format(idx, filename, count))
print("len of X (generating set) is {}".format(len(X)))
print("first element of X is {}".format(X[0]))


# ============= end of main program ============

end = datetime.now()
print("It took {} seconds to compute".format(end - start))

# ========== writing file ==========
# for i in range(1): # for each graph in graph list
#     with open('coach_wk3/dot/' + filename[:-4] + '_' + str(1) + '.dot', 'w') as g:
#         write_dot(G[0][i], g)
# ========== end of writing file ==========



