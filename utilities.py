from graph import *
from SimpleVertex import SimpleVertex
from permv2 import *
from basicpermutationgroup import *

# All the helper functions are defined here.
# "tier 0" means the function is called directly by a main somewhere,
# for i other than 0, "tier i" is helper functions of "tier i-1"
# documentation is most detailed for "tier 0" functions.


# ================ finalizing functions ================


# ================ end of finalizing functions ================

# ================ wk6 ================

# tier 0
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


# tier 0
def get_generating_set(D, I, other, matrix, reference, X, enable_m_test):
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
        trivial, perm_obj = process_bijection_info(st_info)
        # X.append(permutation(len(perm_list), mapping=perm_list))  # add the perm_list to X, regardless trivial or not
        if trivial:
            return 1, False      # non_trivial_found is False
        else:
            # print("non trivial found: {}".format(st_info))
            if enable_m_test:
                if len(X) == 0:
                    X.append(perm_obj)  # perm_obj is the first perm ever
                else:
                    if not membership_testing(X, perm_obj):
                        X.append(perm_obj)  # add the perm_list to X
            else:
                X.append(perm_obj)
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

        num_found, non_trivial_auto_found = get_generating_set(new_D, new_I, new_other, matrix, reference, X, enable_m_test)
        num += num_found

        # pruning
        if non_trivial_auto_found:
            # upon finding the first non-trivial automorphism, don't spawn more branches
            break

    return num, False


# tier 1
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


# tier 1
def process_bijection_info(info):
    """
    Require:
        - info forms a bijection, ie. every color class has exactly 2 (simple) vertices,
          and they have diff v.graph_idx
    Return:
        - trivial: a boolean, is True if the mapping given by info forms a tricial permutation
        - perm_list: a permutation object
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

    return trivial, permutation(len(perm_list), mapping=perm_list)


# tier 2
def is_trivial(perm_list):
    for i in range(len(perm_list)):
        if i != perm_list[i]:
            return False

    return True


# tier 0
def order_computing(X):
    """
    Params:
        - X: a list of permutation object
    """
    # base case, trivial generating set
    if len(X) == 0:
        return 1

    # find the element with its |orbit| >= 2
    for ele in X[0].P:
        O = Orbit(X, ele)
        if len(O) >= 2:
            break

    new_gen_set = Stabilizer(X, ele)

    return len(O) * order_computing(new_gen_set)


# tier 1
def membership_testing(X, permu: "permutation"):
    """
    Param:
        - X, a set of permutation object, is the generating set of a larger perm group
        - permu, a permutation object, that is defined by a bijection currently found in the pruned tree
    Return:
        - True if permu is an element of <X>, the perm group generated by X
    """
    if permu.istrivial():
        return True

    # find the element with its |orbit| >= 2
    for alpha in range(len(permu.P)):
        O, U = Orbit(X, alpha, True)
        if len(O) >= 2:
            break


    # if there is no element with its |orbit| >= 2, must be trivial mapping
    if len(O) == 1:
        return True


    image = permu[alpha]
    for i in range(len(O)):
        if image == O[i]:
            return membership_testing( Stabilizer(X, alpha),  -U[i] * permu)

    return False


# ================ end of wk6 ================


# ================ wk5 ================
# todo move wk 5 helper function here
# ================ end of wk5 ================


# ================ wk4 ================


# tier 0
def extract_vertices(lst_graphs, lst_idx) -> List["Vertex"]:
    """
    Given a list of graphs, and a list of indexes, extract all the vertices of the graphs of interest,
    in the process add an attr v.graph_idx to each vertex.
    Params:
        - lst_graphs: a list of graph object
        - lst_idx: a list of indices of all the graph of interest
    Return:
        - a list of vertices that comes from disjoint union of all the graphs of interest
    """
    target_vertices = []
    for idx in lst_idx:
        # init v.graph_idx
        for v in lst_graphs[idx].vertices:
            v.graph_idx = idx
        target_vertices.extend(lst_graphs[idx].vertices)
    return target_vertices


# tier 0
def count_isomorphism(D, I, other, stop_at_first_iso = False):
    """
    Require:
        - len(D) == len(I)
        - assuming v in D and u in I has a bijection relationship
    Params:
        - D: a subset of vertices of a graph G
        - I: a subset of vertices of another graph H
        - other: all the other vertices in the graphs of interest that do not have a bijection relationship yet
        - stop_at_first_iso: True if you are satisfied as long as there is 1 iso
    Return:
        - number of isomorphisms between the (two) graphs of interest
    """
    # print("one call")
    # print("len(D) is {}; len(I) is {}".format(len(D), len(I)))

    # ===== [1] get info from D + I + other =====
    info = get_info(D, I, other)

    # ===== [2] coarsest stable info under the assumption that D_i and I_i bijection =====
    st_info = color_refinement(info)

    # ===== [3] quick check =====
    bijection, unbalanced = check_balanced_bijection(st_info)

    # print("bijection: {}; unbalanced: {}".format(bijection, unbalanced))

    if unbalanced:
        return 0
    if bijection:
        return 1

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
    for y in fromH:
        new_other = list(filter(lambda ele: ele is not x and ele is not y, other))
        new_D = D + [x]
        new_I = I + [y]
        num += count_isomorphism(new_D, new_I, new_other, stop_at_first_iso)
        # enable this line when want to stop as far as there is ONE isomorphism
        if stop_at_first_iso:
            if num == 1:
                break

    return num


# tier 1
def get_info(D, I, other, use_mtx = False, matrix = None, reference = None):
    """
    Adding v.colornum and v.nb attr to each vertex of D + I + other,
    and organize D + I + other into an info dict.
    """
    info = {}
    next_color = 1

    if len(D) > 0:
        for i in range(len(D)):
            # add v.colornum to each vertex
            D[i].colornum = next_color
            I[i].colornum = next_color
            # record in info
            info[next_color] = [D[i], I[i]]
            next_color += 1

    # all the other vertices are colored 0
    for v in other:
        v.colornum = 0
    info[0] = other

    # add v.nb to v in D + I + other
    for v in D:
        add_v_nb(v, use_mtx, matrix, reference)
    for v in I:
        add_v_nb(v, use_mtx, matrix, reference)
    for v in other:
        add_v_nb(v, use_mtx, matrix, reference)
    return info


# tier 2
def add_v_nb(v, use_mtx, matrix, reference):
    """
    Add v.nb attr for a given vertex.
    - v is an "Vertex" object when not using matrix
    - v is an "SimpleVertex" object when using matrix
    """
    if not use_mtx:
        v.nb = {}
        # adding v.nb using v.neighbours
        for neighbor in v.neighbours:
            if neighbor.colornum not in v.nb:
                v.nb[neighbor.colornum] = 1
            else:
                v.nb[neighbor.colornum] += 1
    else:
        # adding v.nb using adj.matrix
        add_v_nb_use_mtx(v, matrix, reference)


# tier 3
def add_v_nb_use_mtx(v, mtx, ref):
    v.nb = {}
    for key in mtx[(v.graph_idx, v.label)]:
        nb = ref[key]
        if nb.colornum not in v.nb:
            v.nb[nb.colornum] = 1
        else:
            v.nb[nb.colornum] += 1



# tier 1
def check_balanced_bijection(info):
    """
    An info can be one of the 3: bijection, unbalanced, balanced.
    The return value is either:
        - True, False (bijection)
        - False, True (unbalanced)
        - False, False (balanced, need further investigation)
    Require:
        - info only contain mappings {color1: [v1, v2, ...], ...} of TWO graphs, ie. len(unique(info[color_i].graph_idx)) == 2
    Params:
        - info, the stable color mapping computed by color_refinement()
    Return: bool1, bool2
        - bool1: True if info is bijection
        - bool2: True if info is unbalanced
    """
    dict1, dict2 = get_dict(info)

    if not same_dict_value(dict1, dict2):
        return False, True

    if is_bijection(dict1):
        return True, False

    return False, False


# tier 2
def get_dict(info):
    """
    Requires:
        - info is a color mapping of TWO graphs
    Return:
        - dict1, dict2: a {color_num: num_of_vertex_of_this_color} for each graph, resp.
    """
    # re-organize info into 2 dict, each represents the color summary of one graph
    dict1 = {}
    dict2 = {}

    benchmark_graph_idx = None
    benchmark_graph_set = False
    for key in info:
        if not benchmark_graph_set:
            benchmark_graph_idx = info[key][0].graph_idx
            benchmark_graph_set = True
        for v in info[key]:
            if v.graph_idx == benchmark_graph_idx: # go to dict1
                if key in dict1:
                    dict1[key] += 1
                else:
                    dict1[key] = 1
            else:  # go to dict2
                if key in dict2:
                    dict2[key] += 1
                else:
                    dict2[key] = 1
    return dict1, dict2


# tier 1
def stratify_vertices(lst_vertices, g = None):
    """
    Params:
        - lst_vertices: a list of vertices from 2 graphs
        - g: the graph_idx of the first of the two graphs, v in set D comes from graph g
    Return:
        - fromG, fromH: two list of vertices from 2 graphs resp.
    """
    fromG = []
    fromH = []

    benchmark_graph_idx = None  # the index of graph g
    benchmark_graph_set = False

    if g is None:                         # the program need to figure out how to seperate vertices
        pass
    else:
        benchmark_graph_idx = g
        benchmark_graph_set = True

    for v in lst_vertices:
        if not benchmark_graph_set:
            benchmark_graph_idx = v.graph_idx
            benchmark_graph_set = True
        if v.graph_idx == benchmark_graph_idx:
            fromG.append(v)
        else:
            fromH.append(v)
    return fromG, fromH


# ================ end of wk4 ================


# ================ wk3 ================


# tier 2
def init_single_graph(a: "Graph", idx: int):
    """
    Adds 3 fields to a vertex:
    - v.colornum: the color of the vertex
    - v.graph_idx: the graph(int) this vertex belongs to
    - v.nb: dictionary recording neighboring information of the vertex, where the neighbor information is {color_of_neighbor: num_of_nb_of_that_color}
    """
    for v in a.vertices:
        v.colornum = v.degree
        v.graph_idx = idx

    # v.nb = {degree_of_nb: number_of_nb_with_that_degree, .....}
    for v in a.vertices:
        v.nb = {}
        for neighbor in v.neighbours:
            if neighbor.degree not in v.nb:
                v.nb[neighbor.degree] = 1
            else:
                v.nb[neighbor.degree] += 1


# tier 0
def initialization(graphs: List["Graph"]):
    # init each graph by adding 3 attr to each vertex of each graph
    for i in range(len(graphs)):
        init_single_graph(graphs[i], i)

    # organize graph into info
    # info is a dictionary of format {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                 color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                 color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                }
    info = {}
    for graph in graphs:
        for v in graph.vertices:
            if v.colornum not in info:
                info[v.colornum] = [v]
            else:
                info[v.colornum].append(v)

    return info


# tier 1
def typify_group(group):
    # recording the definition of each type: {type: nb_dict}
    type_definition = {}
    # recording the type-vertices relationship: {type: [list_of_vertices_of_this_type]}
    type_vertices = {}

    # a dict of format {type_num: {color_of_neighbor: num_of_nb_of_that_color}
    type_definition[0] = group[0].nb
    # a dict of format {type_num: [list_of_vertices_of_this_type_regardless_of_which_graph_they_belong_to]}
    type_vertices[0] = [group[0]]

    next_type = 1
    # iter check vertices v_2 to v_n of this group
    for i in range(1, len(group)):
        target_vertex = group[i]
        typified = False
        # if the vertex match one of the existing type
        # record the vertex in type_ver
        for type_key in type_definition:
            if same_dict_value(type_definition[type_key], target_vertex.nb):
                type_vertices[type_key].append(target_vertex)
                typified = True
                break  #
            else:
                pass
        # if the vertex does not match any existing type
        # record this new type in type_def
        # record the vertex in the type_ver
        if not typified:
            type_definition[next_type] = target_vertex.nb
            type_vertices[next_type] = [target_vertex]
            next_type += 1
    return type_definition, type_vertices


# tier 0 & tier 2
def same_dict_value(nb1, nb2):
    """
    Compare whether the two dictionary are the same.
    Params: nb1 and nb2 are two dictionaries of neighborhood infomation,
            both of the format {color_of_nb: num_of_nb_of_this_color,
                                color_of_nb: num_of_nb_of_this_color,
                                ...}
    Return: True if nb1 and nb2 have the same value.
    """
    if len(nb1) != len(nb2):
        return False
    for key in nb1:
        if key not in nb2:
            return False
        elif nb1[key] != nb2[key]:
            return False
    return True


# tier 1
def update_nb(new_info, use_mtx, matrix, reference):
    """
    update v.nb field for all the vertice in the graph
    v.nb = {color_of_nb: number_of_nb_with_that_color, .....}
    """
    for color_key in new_info:
        for v in new_info[color_key]:
            if not use_mtx:
                # adding v.nb using v.neighbours
                v.nb = {}
                for neighbor in v.neighbours:
                    if neighbor.colornum not in v.nb:
                        v.nb[neighbor.colornum] = 1
                    else:
                        v.nb[neighbor.colornum] += 1
            else:
                # adding v.nb using adj.matrix
                add_v_nb_use_mtx(v, matrix, reference)


# tier 0
def color_refinement(info, use_mtx=False, matrix=None, reference=None):
    """
    Refine the coloring of the a list of graphs.
    Params:
    - info, where info is a dictionary of format:
      {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       ....}
      the coloring is **not stable** yet.
    Return:
    - info, where info is a dictionary of format:
      {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
       ....}
       that is coarsest stable coloring for the disjoint union of all the graph in graphs.
    """

    next_color = max(info.keys()) + 1

    new_info = {}
    while True:
        change = False

        for color_key in sorted(info.keys()):
            group = info[color_key]
            type_definition = {}
            type_vertices = {}
            if len(group) == 1:
                # no need to further investigate
                new_info[color_key] = info[color_key]
                # go investigate next group
                continue
            else:
                type_definition, type_vertices = typify_group(group)

            # if no need to further split
            if len(type_definition) == 1:
                new_info[color_key] = info[color_key]
                continue
            # if need to further split
            else:
                change = True
                for type_key in type_vertices:
                    new_info[next_color] = type_vertices[type_key]
                    # re-color
                    for v in new_info[next_color]:
                        v.colornum = next_color
                    next_color += 1

        # after 1 iteration over all color
        # if any color_key-[vertices] pair has been splitted, need to update v.nb for all v
        if change:
            update_nb(new_info, use_mtx, matrix, reference)
            # prepare for the next iteration
            info = new_info
            new_info = {}
        # nothing changed, has reach stable coloring, break
        else:
            break
    return info


# tier 0
def from_info_to_mappings(info):
    """
    From the info dictionary, extract for each graph,
    the mapping between color of neighbor and number of neighbor of that color.
    Params:
    - info, a dictionary of format {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
                                    color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
                                    color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
                                    }
            that is coarsest stable coloring for the disjoint union of all the graph in graphs.
    - num_graphs: number of graphs in the disjoint union of graphs
    Return:
    - mappings, the nested dictionary of all the graphs of format
      {graph_index0: {color1: number_of_vertices_of_this_color_within_this_graph,
                      color2: number_of_vertices_of_this_color_within_this_graph, ...},
       graph_index1: {color1: number_of_vertices_of_this_color_within_this_graph,
                      color2: number_of_vertices_of_this_color_within_this_graph, ...},
       ...}
    """
    mappings = {}
    for color_key in info:
        for v in info[color_key]:
            if v.graph_idx not in mappings:
                mappings[v.graph_idx] = {}
                mappings[v.graph_idx][color_key] = 1
            else:
                if color_key not in mappings[v.graph_idx]:
                    mappings[v.graph_idx][color_key] = 1
                else:
                    mappings[v.graph_idx][color_key] += 1
    return mappings


# tier 0
def is_bijection(dic):
    """
    Whether in the dictionary, every key maps to value 1.
    Params:
    - dic, the dictionary of interest.
    Return:
    - True if every key maps to value 1.
    """
    for key in dic:
        if dic[key] != 1:
            return False
    return True

# ================ end of wk3 ================

