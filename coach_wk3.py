from graph_io import write_dot, load_graph
from graph import *
from datetime import datetime, time

# treating graph as undirected


# ================ helper functions ================
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


def initialization(a: "Graph"):
    """
    Init 3 critical data:
    - v.colornum: color number for each vertex
    - v.nb: neighbourhood information for each vertex
    - info: external observation of the entire graph
    Return: info
    """
    # init color as degree of each vertex
    for v in a.vertices:
        v.colornum = v.degree

    # init nb field of each vertex, recording the neighbor information
    # v.nb = {degree_of_nb: number_of_nb_with_that_degree, .....}
    for v in a.vertices:
        v.nb = {}
        for neighbor in v.neighbours:
            if neighbor.degree not in v.nb:
                v.nb[neighbor.degree] = 1
            else:
                v.nb[neighbor.degree] += 1

    # organize graph into info
    # info is a dictionary of format {degree: [vertice_having_this_degree], ...}
    info = {}
    for v in a.vertices:
        if v.colornum not in info:
            info[v.colornum] = [v]
        else:
            info[v.colornum].append(v)

    return info


def get_stable_info(a: "Graph", info):
    # new colors starts at the |V| because after init no vertice has degree of |V|
    next_color = len(a.vertices)

    # temp = 1
    new_info = {}
    while True:
        # print("times in while loop: {}".format(temp))
        # temp += 1

        # new iteration over info, init change as False
        # if after iter, change has not happend, can stop loop
        change = False

        for color_key in sorted(info.keys()):
            group = info[color_key]
            if len(group) == 1:
                # no need to further investigate
                new_info[color_key] = info[color_key]
                continue
            else:
                # recording the definition of each type: {type: nb_dict}
                type_def = {}
                # recording the type-vertices relationship: {type: [list_of_vertices_of_this_type]}
                type_ver = {}

                type_def[0] = group[0].nb
                type_ver[0] = [group[0]]

                next_type = 1
                # iter check vertices v_2 to v_n of this group
                for i in range(1, len(group)):
                    target_vertex = group[i]
                    typified = False
                    # if the vertex match one of the existing type
                    # record the vertex in type_ver
                    for type_key in type_def:
                        if same_nb(type_def[type_key], target_vertex.nb):
                            type_ver[type_key].append(target_vertex)
                            typified = True
                        else:
                            pass
                    # if the vertex does not match any existing type
                    # record this new type in type_def
                    # record the vertex in the type_ver
                    if not typified:
                        type_def[next_type] = target_vertex.nb
                        type_ver[next_type] = [target_vertex]
                        next_type += 1

                # if no need to further split
                if len(type_def) == 1:
                    new_info[color_key] = info[color_key]
                # if need to further split
                else:
                    change = True
                    new_info[color_key] = type_ver[0]
                    for i in range(1, len(type_ver)):
                        new_info[next_color] = type_ver[i]
                        # re-color
                        for v in new_info[next_color]:
                            v.colornum = next_color
                        next_color += 1

        # some group of the same color has been splitted,
        # update nb
        if change:
            # update nb field of each vertex
            update_nb(a)
            # update info dict
            info = new_info
            new_info = {}
        else:
            break

    return info


def get_summary(info):
    # after the while loop, info stores the stable coloring
    summary = {}
    for key in info:
        summary[key] = len(info[key])
    return summary


def is_bijection(dic):
    for key in dic:
        if dic[key] != 1:
            return False
    return True

# ================ end of helper functions ================


start = datetime.now()

# filename = 'colorref_smallexample_2_49.grl'
# filename = 'colorref_smallexample_4_7.grl'
filename = 'colorref_smallexample_6_15.grl'

with open('coach_wk3/' + filename) as f:
    G = load_graph(f, read_list=True)

# iter over each graph, for each graph, generate a summary
# of format {color: number_of_vertice_with_this_color}
# where the coloring is stable
summaries = []
for a in G[0]:
    info = initialization(a)
    stable_info = get_stable_info(a, info)
    summary = get_summary(stable_info)
    summaries.append(summary)

# print isomorphism result
for i in range(0, len(summaries)-1):
    for j in range(i+1, len(summaries)):
        # if they are potentially isomorphic
        # - can be bijection
        # - can be balanced/undecided
        if same_nb(summaries[i], summaries[j]):
            if is_bijection(summaries[i]):
                print("Graph {} is isomorphic with graph {}".format(i, j))
            else:
                print("Graph {} potentially isomorphic with graph {} but can't be decided now".format(i, j))




# timing
end = datetime.now()
print("It took {} seconds to compute".format(end - start))

# write to .dot file
for i in range(len(G[0])): # for each graph in graph list
    with open('coach_wk3/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
        write_dot(G[0][i], g)
