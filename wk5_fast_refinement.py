from graph_io import write_dot, load_graph
from utilities import *
from datetime import datetime


# whenever update dlls, also update dlls_len
#   if the update of dll including adding new color, also update also update queue and in_queue

# ================== temp section ==================

def init_single_graph_fast_refinement(g: "Graph", idx: int):
    """
    Add two attr to each vertice of a graph:
    - v.colornum
    - v.graph_idx
    """
    for v in g.vertices:
        v.colornum = v.degree
        v.graph_idx = idx

# tier 0
def initialization_fast_refinement(graphs: List["Graph"]):
    """
    Add 4 attr to each vertex, and summarize some overview of the entire disjoint union of all graphs.
    Return:
        - dlls, a dictionary dll of each color, with format:
                {color1: the_first_vertex_of_color1_regardless_of_which_graph_it_belongs_to,
                color2: the_first_vertex_of_color2_regardless_of_which_graph_it_belongs_to,
                color3: the_first_vertex_of_color3_regardless_of_which_graph_it_belongs_to,
                }
                where the vertex v = dlls[color_i] has two pointers: v.prev, v.next
        - dlls_len, a dictionary of the length of dll of each color, with format:
               {color1: number_of_vertices_of_color1_regardless_of_which_graph_it_belongs_to,
                color2: number_of_vertices_of_color1_regardless_of_which_graph_it_belongs_to,
                color3: number_of_vertices_of_color1_regardless_of_which_graph_it_belongs_to,
               }
       - all_vertices, a list of all vertices regardless of which graph they belong to.
    """
    for i in range(len(graphs)):
        init_single_graph_fast_refinement(graphs[i], i)

    # organize graph into dlls

    # and each vertex has two additional attr: v.prev, v.next
    dlls = {}
    # dlls_len is recording the lenth of each dll in dlls
    dlls_len = {}
    # a list of all vertices in the disjoint union of all graphs
    all_vertices = []
    # init biggest color label
    max_color = 0
    for graph in graphs:
        all_vertices.extend(graph.vertices)
        for v in graph.vertices:
            if v.colornum not in dlls:
                # add v as the first ele in the dll of its color
                dlls[v.colornum] = create_new_dll_head(v)
                dlls_len[v.colornum] = 1
            else:
                # insert v to the start of an existing, non-empty dll of its color
                dlls[v.colornum] = insert_new_head(dlls[v.colornum], v)
                dlls_len[v.colornum] += 1

    next_color = max(dlls.keys()) + 1

    return dlls, dlls_len, all_vertices, next_color


def insert_new_head(old_head, v):
    """
    Params:
        - old_head, the current first ele of a dll
        - v, the vertex to be inserted as new head
    Return:
        - the new head v with pointers of v and old_head updated
    """
    v.prev = None
    v.next = old_head
    old_head.prev = v
    return v


def create_new_dll_head(v):
    """
    Add 2 attr to v, so it can function as the first ele of a dll
    - v.prev
    - v.next
    """
    v.prev = None
    v.next = None
    return v

def inspect_dlls(dlls):
    """
    Iter print for each v in each dll in dlls, some key information.
    """
    for key in dlls:
        print(" ========== In dll {} ==========".format(key))
        current = dlls[key]
        while current is not None:
            print("vertex {}; graph {}; colornum {}; next {}".format(current, current.graph_idx, current.colornum,
                                                                     current.next))
            current = current.next


def init_queue(init_dlls):
    """
    Params:
        - init_dlls, the initial dlls
    Return:
        - q, a list recording every color_key in dlls, apart from the first key
        - in_q, a dict of {color_key: whether_this_color_is_in_q}
    """
    q = []
    in_q = {}
    is_first = True
    for key in init_dlls:
        # don't add the first color in dlls to queue
        if is_first:
            in_q[key] = False
            is_first = False
            continue
        q.append(key)
        in_q[key] = True
    return q, in_q


def pop_queue_head(q, in_q):
    head = q.pop(0)
    in_q[head] = False
    return head


def update_queue(q, in_q, old_color, new_color):
    """
    Params:
        - q: the queue, a list of color class
        - in_q: whether a color is in queue, a dict of {color_class: whether_this_color_is_in_queue}
        - old_color, new_color: some vertices of old_color is going to be split into a new_color, and the rest remains
    """
    if old_color in in_q:
        # if in_q has recorded old_color as one of its key,
        # then add new_color to queue
        q.append(new_color)
        in_q[new_color] = True
    else:
        # in_q has NOT recorded old_color as one of its key,
        # then add the smaller one of old_color and new_color to queue
        to_add = min(old_color, new_color)
        q.append(to_add)
        in_q[to_add] = True


def refine_color(color, dlls, dlls_len, all_vertices, q, in_q):
    max_num_nb = dlls_len[color]
    for i in range(0, max_num_nb + 1):
        # print("========================= one call to refine(C, i) =========================")
        # print("C is {}; i is {}".format(color, i))
        refine_color_numnb_pair(color, i, dlls, dlls_len, all_vertices, q, in_q)


def refine_color_numnb_pair(C, i, dlls, dlls_len, all_vertices, q, in_q):

    # ===== [1] get a list of vertices that have i neighbors of color C =====
    # O(n^2)
    D = list(filter(lambda v: if_v_has_i_nb_in_C(v, i, C), all_vertices))

    # ===== [2] prepare the material to decide whether a color class is splittable =====
    # a dict of format {potentially_splittable_color: [list_of_vertices_in_D_of_this_color]}
    L_v = {}
    # a dict of format {potentially_splittable_color: num_of_v_in_D_of_this_color}
    L_len = {}
    for v in D:
        if v.colornum not in L_v:
            L_v[v.colornum] = [v]
            L_len[v.colornum] = 1
        else:
            L_v[v.colornum].append(v)
            L_len[v.colornum] += 1


    # ===== [3] split the splittable color class =====
    for old_color in L_v:
        # print("===== one iter over a old_color =====")
        # print("L_len: {}".format(L_len))
        # print("dlls_len: {}".format(dlls_len))
        # print("target color in L_v: {}".format(old_color))

        # do the following things only when old_color is splittable
        if L_len[old_color] < dlls_len[old_color]:
            # === [3.1] generate new color label ===
            new_color = max(dlls_len.keys()) + 1
            # print("----- this old_color is to be splitted -----")
            # print("L_len[old_color]: {}; dlls_len[old_color]: {}".format(L_len[old_color], dlls_len[old_color]))
            # print("old_color: {}; new_color: {}".format(old_color, new_color))

            # === [3.2] update q, in_q ===
            # print("before update_queue, q: {}; in_q: {}".format(q, in_q))

            update_queue(q, in_q, old_color, new_color)

            # print("after update_queue, q: {}; in_q: {}".format(q, in_q))

            # === [3.3] move every v in L_v[old_color] from dlls[old_color] to dlls[new_color] ===
            # === in the process also update v.colornum ===
            for v in L_v[old_color]:
                # print("going to move this vertex: {}".format(v))
                dlls[v.colornum] = remove_v_from_old_dll(v, dlls)   # if v is the head, then after rm v, head has changed
                add_v_to_new_dll(v, dlls, new_color)
                # move_v_to_new_dll(v, dlls, old_color, new_color)

        else:
            pass


def remove_v_from_old_dll(v, dlls):
    """
    Remove vertex v from its current dll, (ie. dlls[v.colornum]).
    v's position can be one of the following:
        - v is the first node of its current dll,  v.prev = None, v.next != None
        - v is the end node of its current dll,    v.prev != None, v.next = None
        - v is somewhere in the middle of the dll, v.prev != None, v.next != None
    v cannot be both the start node and the end node of dll, this is guaranteed by L_len[old_color] < dlls_len[old_color]
    Return:
        - head: the first node of dlls[v.colornum] after removing v
    """
    # modify the dll of v's old color, by rm v

    head = dlls[v.colornum]

    # if v is the start of dll
    if v is head:
        head = v.next
        v.next.prev = None
    else:
        # if v is the end of dll
        if v.next is None:
            v.prev.next = None
        # v is somewhere in the middle of dll
        else:
            v.prev.next = v.next
            v.next.prev = v.prev

    # modify dlls_len of v's old color, by subtract 1
    dlls_len[v.colornum] -= 1

    return head


def add_v_to_new_dll(v, dlls, new_color):
    """
    Add vertex v to a dll of new_color.
    """
    if new_color not in dlls:
        # v should be the first node of a newly created dll
        dlls[new_color] = create_new_dll_head(v)
        dlls_len[new_color] = 1
    else:
        # v should be the new first node of an existing dll
        old_head = dlls[new_color]
        dlls[new_color] = insert_new_head(old_head, v)
        dlls_len[new_color] += 1

    v.colornum = new_color

# def move_v_to_new_dll(v, dlls, old_color, new_color):
#     """
#     Move vertex v from its old color class dll (v.colornum) to a new color class dll (dlls[new_color]),
#     and in the process update v.colornum.
#     """
#     # add v to dlls[new_color], update dlls_len[new_color]
#     if new_color not in dlls:
#         dlls[new_color] = create_new_dll_head(v)
#         dlls_len[new_color] = 1
#     else:
#         old_head = dlls[new_color]
#         dlls[new_color] = insert_new_head(dlls[v.colornum], v)
#         dlls_len[new_color] += 1
#
#     # update dlls_len[old_color]
#     dlls_len[v.colornum] -= 1
#
#     v.colornum = new_color


def if_v_has_i_nb_in_C(v, i, C):
    """
    Returns True if vertex v has i neighbors in color class C.
    Params:
        - v, the vertex of target
        - i, number of neighbors of v that is desired to have color C
        - C, the target color in refine_color(color)
    """
    desired_nb = 0
    for nb in v.neighbours:
        if nb.colornum == C:
            desired_nb += 1
        if desired_nb > i:
            return False

    if desired_nb == i:
        return True
    else:
        return False


def from_dlls_to_mappings(dlls):
    """
    Transform the dlls into mappings,
        - where dlls is of format:
                {color1: the_first_vertex_of_color1_regardless_of_which_graph_it_belongs_to,
                color2: the_first_vertex_of_color2_regardless_of_which_graph_it_belongs_to,
                color3: the_first_vertex_of_color3_regardless_of_which_graph_it_belongs_to,
                }
                where the vertex v = dlls[color_i] has two pointers: v.prev, v.next
        - and mapping is a nested dictionary of all the graphs of format:
              {graph_index0: {color1: number_of_vertices_of_this_color_within_this_graph,
                              color2: number_of_vertices_of_this_color_within_this_graph, ...},
               graph_index1: {color1: number_of_vertices_of_this_color_within_this_graph,
                              color2: number_of_vertices_of_this_color_within_this_graph, ...},
               ...}

    """
    mappings = {}
    for color_key in dlls:
        # deal with the first node in the dll
        current = dlls[color_key]

        while current is not None:
            # record current in mappings
            if current.graph_idx not in mappings:
                mappings[current.graph_idx] = {}
                mappings[current.graph_idx][color_key] = 1
            else:
                if color_key not in mappings[current.graph_idx]:
                    mappings[current.graph_idx][color_key] = 1
                else:
                    mappings[current.graph_idx][color_key] += 1

            # update current to point to the next vertex
            current = current.next

    return mappings


# ================== end of temp section ==================


# ========== reading file ==========
# ---------- wk5 examples ----------
# ---------- while the examples here are .gr, all functionalities should accommodate .grl ----------
# filename = 'threepaths5.gr'
# filename = 'threepaths10.gr'
# filename = 'threepaths20.gr'
# filename = 'threepaths40.gr'
# filename = 'threepaths80.gr'
# filename = 'threepaths160.gr'
# filename = 'threepaths320.gr'
# filename = 'threepaths640.gr'
# filename = 'threepaths1280.gr'
filename = 'threepaths2560.gr'
# filename = 'threepaths5120.gr'
# filename = 'threepaths10240.gr'

with open('coach_wk5/' + filename) as f:
    G = load_graph(f)
print("{} contains 1 graphs with {} vertices".format(filename, len(G.vertices)))

list_of_graphs = [G]

# ---------- wk3 examples ----------
# filename = 'colorref_smallexample_2_49.grl'
# filename = 'colorref_smallexample_4_7.grl'
# filename = 'colorref_smallexample_4_16.grl'
# filename = 'colorref_smallexample_6_15.grl'
# filename = 'colorref_largeexample_4_1026.grl'
# filename = 'colorref_largeexample_6_960.grl'
#
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


# start time after file-reading
start = datetime.now()

dlls, dlls_len, all_vertices, next_color = initialization_fast_refinement(list_of_graphs)
q, in_q = init_queue(dlls)

while len(q) > 0:
    # print("================================ one iter while loop ================================")
    # print("queue is: {}; in_queue is: {}".format(q, in_q))

    C = pop_queue_head(q, in_q)

    # print("color {} popped out of queue".format(C))
    # print("now queue is: {}; in_queue is: {}".format(q, in_q))

    refine_color(C, dlls, dlls_len, all_vertices, q, in_q)


end = datetime.now()
print("It took {} seconds to compute".format(end - start))
# print("BIG CONGRATES!!!! You have reach the end!")
# print("dlls_len is: {}".format(dlls_len))

mappings = from_dlls_to_mappings(dlls)

# print("mappings is: {}".format(mappings))



# interpreting result
num_graphs = len(list_of_graphs)
for i in range(0, num_graphs-1):
    for j in range(i+1, num_graphs):
        if same_dict_value(mappings[i], mappings[j]):
            if is_bijection(mappings[i]):
                print("Graph {} and {} is isomorphic".format(i, j))
            else:
                print("Graph {} and {} is potentially isomorphic".format(i, j))


# ========== writing file ==========
# ---------- wk5 examples (single graph) ----------
# with open('coach_wk5/dot/' + filename[:-4] + '.dot', 'w') as g:
#     write_dot(G, g)


# ---------- wk3 wk4 examples (list of graph) ----------
# for i in range(len(G[0])): # for each graph in graph list
#     with open('coach_wk3/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
#         write_dot(G[0][i], g)

# ========== end of writing file ==========


