from utilities import *
from os import listdir
from graph_io import write_dot, load_graph
from datetime import datetime

# tier 0
def get_files(path):
    """
    Get a list of filenames that are either .gr or .grl files in the given path.
    """
    files = list(filter(lambda x: x.endswith('.grl') or x.endswith('.gr'), listdir(path)))
    return files


# tier 0
def AUT(filename, do_m_test):
    """
    Input a filename, can be a .gr file or .grl file,
    compute its automorphism result and output as project manual demanded.
    Params:
        - do_m_test: is True if you want to do membership testing
    """
    if filename.endswith('.gr'):
        # file contains single graph
        with open(filename) as f:
            G = load_graph(f)
        print("{} contains 1 graphs with {} vertices".format(filename, len(G.vertices)))

        AUT_single(G, do_m_test)

    elif filename.endswith('.grl'):
        # file contains a list of graphs
        with open(filename) as f:
            G = load_graph(f, read_list=True)
        list_of_graphs = G[0]
        print("{} contains {} graphs, each {} vertices".format(filename,
                                                               len(list_of_graphs),
                                                               len(list_of_graphs[0].vertices)))

        AUT_many(list_of_graphs)


# tier 1
def AUT_many():
    print("not implemented yet")
    # todo: first call GI(list_of_graph) to get equivalent classes
    # todo:
    return None


# tier 1
def AUT_single(one_graph, do_m_test=False):

    all_v, matrix, reference = initialization_automorphism(one_graph)

    X = []

    count, _ = get_generating_set([], [], all_v, matrix, reference, X, do_m_test)

    num_auto = order_computing(X)

    print("This graph has {} ele in X, and {} automorphisms".format(len(X), num_auto))


# tier 0 and tier 1
def GI(filename):
    """
    filename will always be a .grl file.
    """
    # file contains a list of graphs
    with open(filename) as f:
        G = load_graph(f, read_list=True)

    list_of_graphs = G[0]
    print("{} contains {} graphs, each {} vertices".format(filename,
                                                           len(list_of_graphs),
                                                           len(list_of_graphs[0].vertices))
                                                           )

    # color refinement
    init_info = initialization(list_of_graphs)
    info = color_refinement(init_info)

    # processing result
    num_graphs = len(list_of_graphs)
    mappings = from_info_to_mappings(info)

    bij_def, bij_g, bal_def, bal_g = typify_mappings(mappings)


    print("These are bijections found in first applying color refinement")
    for key in bij_g:
        print(bij_g[key])

    # a dict recording { type0: [list_of_graph_idx_of_this_type], ...}
    bij_from_bal = []

    # if there are undecided groups
    if len(bal_g) > 0:
        for key in bal_g:
            group = bal_g[key]      # a list of graphs that potentially is isomorphic
            bij_from_bal.extend((typify_group(group, list_of_graphs)))

        print("These are iso found from balanced mappings")
        for ele in bij_from_bal:
            print(ele)


# tier 1
def typify_group(group, list_of_graphs):
    """
    Params:
        - group: a list of graph_idx that potentially is isomorphic
    Return:
        - types: a nested list, of which each element is a list of graph_idx that
                 are in the same equivalent class
    """
    types = []
    typified = []
    for i in range(0, len(group)-1):
        if group[i] not in typified:
            matches = []
            for j in range(i+1, len(group)):
                if group[j] not in typified:
                    if is_iso(list_of_graphs, [group[i], group[j]]):
                        matches.append(group[j])
                    else:
                        pass
            typified.append(group[i])
            typified.extend(matches)
            types.append([group[i]] + matches)

    return types


# tier 1
def is_iso(list_of_g, idx_list):
    p = idx_list[0]
    q = idx_list[1]

    v = extract_vertices(list_of_g, [p, q])

    # the last param is True if you want to stop at finding the first iso
    count = count_isomorphism([], [], v, True)

    if count != 0:
        return True
    else:
        return False


# tier 1
def typify_mappings(mappings):
    """
    Params:
        - mappings, the nested dictionary of all the graphs of format
          {graph_index0: {color1: number_of_vertices_of_this_color_within_this_graph,
                          color2: number_of_vertices_of_this_color_within_this_graph, ...},
           graph_index1: {color1: number_of_vertices_of_this_color_within_this_graph,
                          color2: number_of_vertices_of_this_color_within_this_graph, ...},
           ...}
    Return:
        - print a bunch of equivalent classes of graph indices
    """
    # a dict of format {type_key: {color1: number_of_vertices_of_this_color_within_this_graph,
    #                              color2: number_of_vertices_of_this_color_within_this_graph, ...},
    # the definition of this bijection type
    bijection_type_def = {}
    # a dict of format {type_key1: [list_of_graph_idx_that_belongs_to_this_type],
    #                   type_key2: [list_of_graph_idx_that_belongs_to_this_type],
    bijection_type_g = {}
    # a dict of format {type_key: {color1: number_of_vertices_of_this_color_within_this_graph,
    #                              color2: number_of_vertices_of_this_color_within_this_graph, ...},
    # the definition of this bijection type
    balanced_type_def = {}
    # a dict of format {type_key1: [list_of_graph_idx_that_belongs_to_this_type],
    #                   type_key2: [list_of_graph_idx_that_belongs_to_this_type],
    balanced_type_g = {}

    bijection_next_type = 0
    balanced_next_type = 0

    for g_key in mappings:
        if is_bijection(mappings[g_key]):
            if len(bijection_type_def) == 0:
                bijection_type_def[bijection_next_type] = mappings[g_key]
                bijection_type_g[bijection_next_type] = [g_key]
                bijection_next_type += 1
            else:
                typified = False
                for t_key in bijection_type_def:
                    if same_dict_value(bijection_type_def[t_key], mappings[g_key]):
                        bijection_type_g[t_key].append(g_key)
                        typified = True
                        break
                    else:
                        pass
                if not typified:
                    bijection_type_def[bijection_next_type] = mappings[g_key]
                    bijection_type_g[bijection_next_type] = [g_key]
                    bijection_next_type += 1
        else:
            # this is a balanced color mapping
            if len(balanced_type_def) == 0:
                balanced_type_def[balanced_next_type] = mappings[g_key]
                balanced_type_g[balanced_next_type] = [g_key]
                balanced_next_type += 1
            else:
                typified = False
                for t_key in balanced_type_def:
                    if same_dict_value(balanced_type_def[t_key], mappings[g_key]):
                        balanced_type_g[t_key].append(g_key)
                        typified = True
                        break
                    else:
                        pass
                if not typified:
                    balanced_type_def[balanced_next_type] = mappings[g_key]
                    balanced_type_g[balanced_next_type] = [g_key]
                    balanced_next_type += 1

    return bijection_type_def, bijection_type_g, balanced_type_def, balanced_type_g




# ================== body of functions
path = 'coach_wk4/'

# filename = 'torus24.grl'
# filename = 'trees36.grl'
# filename = 'products72.grl'
# filename = 'torus144.grl'
# filename = 'cubes5.grl'
# filename = 'cubes7.grl'
# filename = 'cubes9.grl'
# filename = 'trees90.grl'
filename = 'bigtrees3.grl'    # mentioned by the manual
# filename = 'cubes6.grl'    # mentioned by the manual

GI(path + filename)