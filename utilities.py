from graph import *

# All the helper functions are defined here.
# "tier 0" means the function is called directly by a main somewhere,
# for i other than 0, "tier i" is helper functions of "tier i-1"
# documentation is most detailed for "tier 0" functions.

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
def count_isomorphism(D, I, other):
    """
    Require:
        - len(D) == len(I)
        - assuming v in D and u in I has a bijection relationship
    Params:
        - D: a subset of vertices of a graph G
        - I: a subset of vertices of another graph H
        - other: all the other vertices in the graphs of interest that do not have a bijection relationship yet
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
    for key in info:
        if len(info[key]) >= 4:
            break

    if len(D) == 0:
        fromG, fromH = stratify_vertices(info[key])
    else:
        fromG, fromH = stratify_vertices(info[key], D[0].graph_idx)

    x = fromG[0]
    num = 0
    for y in fromH:
        new_other = list(filter(lambda ele: ele is not x and ele is not y, other))
        new_D = D + [x]
        new_I = I + [y]
        num += count_isomorphism(new_D, new_I, new_other)
        # print("Num of isomorphism: {}".format(num))

    return num


# tier 1
def get_info(D, I, other):
    """
    Adding v.colornum and v.nb attr to each vertex of D + I + other, and organize D + I + other into an info dict.
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
        add_v_nb(v)
    for v in I:
        add_v_nb(v)
    for v in other:
        add_v_nb(v)
    return info


# tier 2
def add_v_nb(v: "Vertex"):
    """
    Add v.nb attr for a given vertex.
    """
    v.nb = {}
    for neighbor in v.neighbours:
        if neighbor.colornum not in v.nb:
            v.nb[neighbor.colornum] = 1
        else:
            v.nb[neighbor.colornum] += 1


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
def update_nb(new_info):
    """
    update v.nb field for all the vertice in the graph
    v.nb = {color_of_nb: number_of_nb_with_that_color, .....}
    """
    for color_key in new_info:
        for v in new_info[color_key]:
            v.nb = {}
            for neighbor in v.neighbours:
                if neighbor.colornum not in v.nb:
                    v.nb[neighbor.colornum] = 1
                else:
                    v.nb[neighbor.colornum] += 1


# tier 0
def color_refinement(info):
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
            update_nb(new_info)
            # prepare for the next iteration
            info = new_info
            new_info = {}
        # nothing changed, has reach stable coloring, break
        else:
            break
    return info



# tier 0
def extract_color_number_mappings(info):
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

