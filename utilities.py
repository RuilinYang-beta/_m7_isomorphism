from graph import *

# ================ wk3 ================


# tier 2
def init_single_graph(a: "Graph", idx: int):
    """
    Adds 3 fields to a vertex:
    - v.colornum: the color of the vertex
    - v.graph_idx: the graph(int) this vertex belongs to
    - v.nb: dictionary recording neighboring infomation of the vertex
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


# tier 1
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

    type_definition[0] = group[0].nb
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
    compare whether the two dictionary are the same
    return: True if they have the same value
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
def update_nb(graph):
    """
    update v.nb field for all the vertice in the graph
    v.nb = {color_of_nb: number_of_nb_with_that_color, .....}
    """
    for v in graph.vertices:
        v.nb = {}
        for neighbor in v.neighbours:
            if neighbor.colornum not in v.nb:
                v.nb[neighbor.colornum] = 1
            else:
                v.nb[neighbor.colornum] += 1


# tier 0
def color_refinement(graphs):
    """
    graphs: a list of graph object
    return: a dictionary of info, where info is a dictionary of format
            {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
             color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
             color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
             ....}
             that is coarsest stable coloring
    """
    info = initialization(graphs)

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
            else:
                type_definition, type_vertices = typify_group(group)

            # if no need to further split
            if len(type_definition) == 1:
                new_info[color_key] = info[color_key]
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
            for graph in graphs:
                update_nb(graph)
            # prepare for the next iteration
            info = new_info
            new_info = {}
        # nothing changed, has reach stable coloring, break
        else:
            break
    return info


# tier 1
def extract_color_mapping(info, i):
    """
    From info extract the color mapping of a certain graph i, where
    # info is a dictionary of format {color1: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                 color2: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                 color3: [list_of_vertices_of_this_color_regardless_of_which_graph_they_belong_to],
    #                                }
    # that has reached stable coloring
    """
    # now need to extract {color1: num_of_v_of_this_color,
    #                      color2: num_of_v_of_this_color,
    #                      ....}
    # for a certain graph
    mapping = {}
    for color_key in info:
        all_vertices = info[color_key]
        num_of_nb = len(list(filter(lambda x: x.graph_idx == i, all_vertices)))
        if num_of_nb != 0:
            mapping[color_key] = num_of_nb
    return mapping


# tier 0
def extract_color_mappings(info, num_graphs):
    mappings = {}
    for i in range(num_graphs):
        mappings[i] = extract_color_mapping(info, i)
    return mappings


# tier 0
def is_bijection(dic):
    for key in dic:
        if dic[key] != 1:
            return False
    return True

# ================ end of wk3 ================

