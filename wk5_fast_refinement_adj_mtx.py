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
                color2: number_of_vertices_of_color2_regardless_of_which_graph_it_belongs_to,
                color3: number_of_vertices_of_color3_regardless_of_which_graph_it_belongs_to,
               }
       - matrix, an adjacency matrix recording the neighborhood information of all the vertices,
         in the format:
              {v1: {nb_of_v1: 1,
                    nb_of_v1: 1,
                    nb_of_v1: 1,}
               v2: {nb_of_v2: 1,
                    nb_of_v2: 1,
                    nb_of_v2: 1}
              }
          where type(v1) == Vertex, type(nb_of_v2 == Vertex.
          That is, the "matrix" is actually with many holes, because it's a dict that only records
          every vertex and it's neighbor:
              - v2 is v1's neighbour <==> v2 in matrix[v1] == True
              - v2 is not v1's neighbour <==> v2 in matrix[v1] == False
    """
    for i in range(len(graphs)):
        init_single_graph_fast_refinement(graphs[i], i)

    # organize graph into dlls

    # and each vertex has two additional attr: v.prev, v.next
    dlls = {}
    # dlls_len is recording the lenth of each dll in dlls
    dlls_len = {}
    # adjacency "matrix" of the disjoint union of graphs
    mtx = {}
    for graph in graphs:
        for v in graph.vertices:
            # --- record v in dlls and dlls_len ---
            if v.colornum not in dlls:
                # add v as the first ele in the dll of its color
                dlls[v.colornum] = create_new_dll_head(v)
                dlls_len[v.colornum] = 1
            else:
                # insert v to the start of an existing, non-empty dll of its color
                dlls[v.colornum] = insert_new_head(dlls[v.colornum], v)
                dlls_len[v.colornum] += 1
            # --- record v in mtx ---
            mtx[v] = {}
            for nb in v.neighbours:
                mtx[v][nb] = 1

    return dlls, dlls_len, mtx


def insert_new_head(old_head: "Vertex", v:"Vertex"):
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


def create_new_dll_head(v: "Vertex"):
    """
    Add 2 attr to v, so it can function as the first ele of a dll, and return the v.
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
        inspect_dll(dlls[key])


def inspect_dll(dll_head: "Vertex"):
    current = dll_head
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
        - in_q, a dict of {color_key: 1}, where
            - color_key is in queue <==> color_key in in_q == True
            - color_key is not in queue <==> color_key in in_q == False
    """
    q = []              # use list becuase list.pop(0) is fast
    in_q = {}           # use dict because key in dict check is fast, and dict.pop(key) is fast
    is_first = True
    for key in init_dlls:
        # don't add the first color in dlls to queue
        if is_first:
            is_first = False
            continue
        q.append(key)
        in_q[key] = 1
    return q, in_q


def pop_queue_head(q, in_q):
    head = q.pop(0)
    in_q.pop(head)
    return head


def update_queue(q, in_q, old_color: int, new_color: int):
    """
    Params:
        - q: the queue, a list of color class
        - in_q: whether a color is in queue, a dict of {color_in_queue: 1}
        - old_color, new_color: some vertices of old_color is going to be split into a new_color, and the rest remains
    """
    if old_color in in_q:
        # if in_q has recorded old_color as one of its key,
        # then add new_color to queue
        q.append(new_color)
        in_q[new_color] = 1
    else:
        # in_q has NOT recorded old_color as one of its key,
        # then add the smaller one of (old_color, new_color) to queue
        to_add = min(old_color, new_color)
        q.append(to_add)
        in_q[to_add] = 1


def refine_color(color: int, dlls, dlls_len, mtx, q, in_q):
    """
    For a given color color, refine it over all D_i,
    where D_i is a set of vertices that have i neighbours in the given color class.
    """
    # === [1] compute partition D over all i ===
    # D's format see doc for get_partition_D()
    D = get_partition_D(color, dlls, mtx)


    for num_nb in D:
        # === [2] for each cell in D, compute L_len, L_v ===
        # --- where L_len and L_v is the material to decide whether a color class is splittable ---
        # sub_D is the list of vertex with num_nb neighbours in color C
        sub_D = D[num_nb]
        L_v, L_len = investigate_sub_D(sub_D)

        for old_color in L_v:
            # ===== [3] split the splittable color class =====
            # --- and update related values accordingly ---
            if L_len[old_color] < dlls_len[old_color]:
                split_color(dlls, old_color, L_v[old_color], q, in_q)


def split_color(dlls, old_color, vertices_to_split, q, in_q):
    """
    Split an old color class into two parts:
        - one part remains in the old class
        - the other part form a new color class
    """

    # === [3.1] generate new color label ===
    new_color = max(dlls.keys()) + 1

    # === [3.2] update q, in_q ===
    update_queue(q, in_q, old_color, new_color)

    # === [3.3] move every v in L_v[old_color] from dlls[old_color] to dlls[new_color] ===
    # --- in the process also update v.colornum ---
    for v in vertices_to_split:
        dlls[v.colornum] = remove_v_from_old_dll(v, dlls)  # if v is the head, then after rm v, head has changed
        add_v_to_new_dll(v, dlls, new_color)

    return None


def investigate_sub_D(sub_D: List["Vertex"]):
    """
    Params:
        - sub_D: a list of vertex
    Return:
        - L_v: a dict of format {potentially_splittable_color: [list_of_vertices_in_D_of_this_color]}
        - L_len: a dict of format {potentially_splittable_color: num_of_v_in_D_of_this_color}
    """
    L_v = {}
    L_len = {}
    for v in sub_D:
        if v.colornum not in L_v:
            L_v[v.colornum] = [v]
            L_len[v.colornum] = 1
        else:
            L_v[v.colornum].append(v)
            L_len[v.colornum] += 1
    return L_v, L_len


def get_partition_D(C, dlls, mtx):
    """
    For a given color C, partition all vertices into: D_0, D_1, ..., D_k, (at most k+1 cells)
        - where D_i is the set of vertices that has i neighbours in C
        - k is the number of vertices in C
    Params:
        - C: the target class
        - dlls, dlls_len, mtx: see definition in initialization_fast_refinement()
    Return:
        - D: a partition of all the vertices, with the format
                {0: [list_of_vertices_that_has_0_nb_in_C],
                 1: [list_of_vertices_that_has_1_nb_in_C],
                 2: [list_of_vertices_that_has_2_nb_in_C] }
    """
    D = {}
    # iter over every vertex in the disjoint union
    for vertex_key in mtx:
        nb_count = 0
        current = dlls[C]
        # iter over every vertex in the color C
        while current is not None:
            # if current is neighbour of vertex_key, incr nb_count
            if current in mtx[vertex_key]:
                nb_count += 1
            current = current.next
        # add vertex_key to D[nb_count]
        if nb_count in D:
            D[nb_count].append(vertex_key)
        else:
            D[nb_count] = [vertex_key]

    return D


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
    Add vertex v to a dll of new_color, and update v.colornum = new_color
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

dlls, dlls_len, matrix = initialization_fast_refinement(list_of_graphs)
q, in_q = init_queue(dlls)


while len(q) > 0:
    # print("================================ one iter while loop ================================")
    # print("queue is: {}; in_queue is: {}".format(q, in_q))

    C = pop_queue_head(q, in_q)

    # print("color {} popped out of queue".format(C))
    # print("now queue is: {}; in_queue is: {}".format(q, in_q))

    refine_color(C, dlls, dlls_len, matrix, q, in_q)


end = datetime.now()
print("It took {} seconds to compute".format(end - start))
print("BIG CONGRATES!!!! You have reach the end!")
# print("dlls_len is: {}".format(dlls_len))

mappings = from_dlls_to_mappings(dlls)

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
# for i in range(len(list_of_graphs)): # for each graph in graph list
#     with open('coach_wk3/dot/' + filename[:-4] + '_' + str(i) + '.dot', 'w') as g:
#         write_dot(list_of_graphs[i], g)

# ========== end of writing file ==========