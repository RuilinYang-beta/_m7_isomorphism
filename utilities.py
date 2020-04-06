from graph import *

# All the helper functions are defined here.
# "tier 0" means the function is called directly by a main somewhere,
# for i other than 0, "tier i" is helper functions of "tier i-1"
# documentation is most detailed for "tier 0" functions.

# ================ wk4 ================



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
            if same_nb(type_definition[type_key], target_vertex.nb):
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
def same_nb(nb1, nb2):
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

