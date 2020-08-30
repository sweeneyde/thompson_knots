import thompson
from fractions import Fraction
from collections import deque

def vertex_placement(tree: thompson.Vertex):
    vertices = deque()
    leaves = []
    for v in tree.in_order_vertices():
        if v.is_leaf():
            leaves.append(v)
        else:
            vertices.append(v)

    placements = {L: (Fraction(i), Fraction(0)) for (i, L) in enumerate(leaves)}

    while vertices:
        v = vertices.popleft()
        try:
            lx, ly = placements[v.left]
            rx, ry = placements[v.right]
        except KeyError:
            vertices.append(v)
            continue
        else:
            x = (ry - ly + lx + rx) / 2
            y = ly + x - lx
            placements[v] = (x, y)

    return placements, leaves

def get_segments(word1, word2):

    tree1, tree2, label_to_vertex = \
        thompson.construct_trees(word1, word2)

    placements, leaves = vertex_placement(tree1)
    placements2, _ = vertex_placement(tree2)
    bottom_placements = {v: (x, -y)
                         for v, (x, y)
                         in placements2.items()}
    placements.update(bottom_placements)

    segments = []

    for tree in tree1, tree2:
        for v in tree.in_order_vertices():
            if v.is_leaf():
                continue
            segments += [
                (placements[v], placements[v.left]),
                (placements[v], placements[v.right]),
            ]

    return segments, [placements[x] for x in leaves]

def plot_rectangle_diagram(word1, word2=None):
    if word2 is None:
        word1, word2 = word1.split(' / ')
    import matplotlib.pyplot as plt
    from matplotlib import collections as mc

    segs, leaves = get_segments(word1, word2)
    segs = mc.LineCollection(segs, colors='k', linewidths=1)
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.add_collection(segs)
    for L in leaves:
        ax1.plot(*L, 'r.')
    ax1.autoscale()
    fig.show()

def plot_all(lines, rows=4, cols=4):
    import matplotlib.pyplot as plt
    from matplotlib import collections as mc

    if '\n' in lines:
        lines = lines.splitlines()

    fig = plt.figure()

    for i, line in enumerate(lines, start=1):
        word1, word2 = line.split(" / ")

        segs, leaves = get_segments(word1, word2)
        segs = mc.LineCollection(segs, colors='k', linewidths=1)
        ax1 = fig.add_subplot(rows, cols, i)
        ax1.add_collection(segs)
        for L in leaves:
            ax1.plot(*L, 'r.')
        ax1.autoscale()

    fig.show()