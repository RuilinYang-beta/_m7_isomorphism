class SimpleVertex():

    def __init__(self, graph_idx, label):
        self.graph_idx = graph_idx
        self.label = label


    # def __init__(self, colornum, nb, graph_idx, label):
    #     self.colornum = colornum
    #     self.nb = nb
    #     self.grahp_idx = graph_idx
    #     self.label = label

    def __str__(self):
        return str((self.graph_idx, self.label))

    def __repr__(self):
        return str((self.graph_idx, self.label))

    # def __str__(self):
    #     return "graph: {}; label: {}; colornum: {}; nb: {}".format(self.graph_idx,
    #                                                                self.label,
    #                                                                self.colornum,
    #                                                                self.nb)

