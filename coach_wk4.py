from graph_io import write_dot, load_graph
from utilities import *
from datetime import datetime
import copy

# ==================== temp section ====================


def extract_partial_info(info, i, j):
    partial_info = {}
    for color_key in info:
        all_vertices = info[color_key]
        target_vertices = list(filter(lambda x: x.graph_idx == i or x.graph_idx == j, all_vertices))
        if len(target_vertices) > 0:
            partial_info[color_key] = target_vertices
    return partial_info


def check_balanced_bijection(info, i, j):
    """
    Require: info only contain mappings {color1: [v1, v2, ...], ...} of **two** graphs
    """
    balanced = True
    bijection = False

    # check balance
    for key in info:
        all_v = info[key]
        # if balanced => each color should have even num of vertices
        if len(all_v) % 2 != 0:
            return False, False

        # if balanced => each color's vertices should be fairly shared between two graphs
        if len(list(filter(lambda x: x.graph_idx == i, all_v))) != len(list(filter(lambda x: x.graph_idx == j, all_v))):
            return False, False

    # check whether a balanced mapping is bijection
    for key in info:
        all_v = info[key]
        if len(list(filter(lambda x: x.graph_idx == i, all_v))) != 1:
            return True, False

    return True, True


# ==================== end of temp ====================



start = datetime.now()

filename = 'torus_4_24.grl'
with open('coach_wk4/' + filename) as f:
    G = load_graph(f, read_list=True)

# filename = 'colorref_smallexample_4_7.grl'
# with open('coach_wk3/' + filename) as f:
#     G = load_graph(f, read_list=True)


print("{} has {} graphs, with each graph {} vertices".format(filename, len(G[0]), len(G[0][0].vertices)))

# color refinement
init_info = initialization(G[0])
info = color_refinement(init_info)

# extract the info of two graphs that has balanced coloring
p = 0
q = 3
partial_info = extract_partial_info(info, p, q)
# print(partial_info)


def count_isomorphism(info, p, q, num, is_refined=False):
    if not is_refined:
        info = color_refinement(info)

    balanced, bijection = check_balanced_bijection(info, p, q)
    if not balanced:
        return 0
    if bijection:
        return 1

    next_color = max(info.keys()) + 1
    for color_key in info:
        if len(info[color_key]) >= 4:
            break
    print("====== another call ======")
    # print(info)
    # print("len(info[color_key] = {}".format(len(info[color_key])))
    # print("current color key: {}".format(color_key))
    #
    # if len(info[color_key]) == 4:
    #     for j in range(len(info[color_key])):
    #         print("{}-th vertex has graph_idx {}".format(j, info[color_key][j].graph_idx))

    benchmark = info[color_key][0].graph_idx
    count = 0
    for i in range(1, len(info[color_key])):
        if info[color_key][i].graph_idx != benchmark:
            print("enter if, color_key: {}; count: {}; i: {}".format(color_key, count, i))
            # info_copy = info.copy()
            info_copy = copy.deepcopy(info)
            y = info_copy[color_key].pop(i)
            x = info_copy[color_key].pop(0)
            info_copy[next_color] = [x, y]
            # num += count_isomorphism(info_copy, p, q, num, False)
            count += count_isomorphism(info_copy, p, q, False)
    # return num
    return count

print(count_isomorphism(partial_info, p, q, 0, True))





# mappings = extract_color_number_mappings(partial_info, 4)
# print(mappings)



# # processing result
# num_graphs = len(G[0])
# mappings = extract_color_number_mappings(info, num_graphs)
#
# print(mappings)
#
# # interpreting result
# for i in range(0, num_graphs-1):
#     for j in range(i+1, num_graphs):
#         if same_nb(mappings[i], mappings[j]):
#             if is_bijection(mappings[i]):
#                 print("Graph {} and {} is isomorphic".format(i, j))
#             else:
#                 print("Graph {} and {} is potentially isomorphic".format(i, j))






# for i in range(len(G[0])): # for each graph in graph list
#     with open('coach_wk4/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
#         write_dot(G[0][i], g)




end = datetime.now()
print("It took {} seconds to compute".format(end - start))