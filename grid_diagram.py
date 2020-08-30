import thompson


def normalized(segments):
    """Quantize the values to land on integers"""
    xs = sorted(set(x for seg in segments for (x, y) in seg))
    ys = sorted(set(y for seg in segments for (x, y) in seg))
    x_map = {x: i for i, x in enumerate(xs)}
    y_map = {y: i for i, y in enumerate(ys)}

    def map_point(point):
        x, y = point
        return (x_map[x], y_map[y])

    return [(map_point(p1), map_point(p2))
            for (p1, p2) in segments]


def vertex_placement(tree: thompson.Vertex):
    # q = deque()
    leaves = [v for v in tree.in_order_vertices() if v.is_leaf()]

    big = 1_000_000
    placements = {x: [i, None] for i, x in enumerate(leaves, start=1)}

    for i, v in enumerate(tree.breadth_first_vertices()):
        y = big - i

        if v.is_leaf():
            placements[v][1] = y
            continue

        predecessor = v.left
        while not predecessor.is_leaf():
            predecessor = predecessor.right
        (pred_x, pred_y) = placements[predecessor]

        successor = v.right
        while not successor.is_leaf():
            successor = successor.left
        (succ_x, succ_y) = placements[successor]

        x = (pred_x + succ_x) / 2

        placements[v] = [x, y]

    for node in tree.breadth_first_vertices():
        if node.is_leaf():
            continue
        left_x, left_y = left = placements[node.left]
        right_x, right_y = right = placements[node.right]
        left[1] = right[1] = max(left_y, right_y)

    return placements


def get_segments(word1, word2):
    tree1, tree2, label_to_vertex = \
        thompson.construct_trees(word1, word2)

    placements = vertex_placement(tree1)
    bottom_placements = {v: (x, -y) for v, (x, y) in
                         vertex_placement(tree2).items()}
    placements.update(bottom_placements)

    (top_x, max_y) = placements[tree1]
    (bottom_x, min_y) = placements[tree2]
    vertical1 = []
    vertical2 = [((0, min_y), (0, max_y))]
    horizontal_segments = [((0, min_y), (bottom_x, min_y)),
                           ((0, max_y,), (top_x, max_y))]

    for v_top, v_bottom in zip(tree1.in_order_vertices(),
                               tree2.in_order_vertices()):
        assert v_top.corresponding is v_bottom
        if not v_top.is_leaf():
            horizontal_segments.append((
                placements[v_top.left],
                placements[v_top.right],
            ))
            horizontal_segments.append((
                placements[v_bottom.left],
                placements[v_bottom.right],
            ))

        (vertical1 if v_top.is_leaf() else vertical2).append((
            placements[v_top],
            placements[v_bottom]
        ))

    segments = horizontal_segments + vertical1 + vertical2
    segments = normalized(segments)
    n1 = len(horizontal_segments)
    n2 = n1 + len(vertical1)
    horizontal_segments, vertical1, vertical2 = segments[:n1], segments[n1:n2], segments[n2:]
    return horizontal_segments, vertical1, vertical2


def plot_grid_diagram(word1, word2=None):
    if word2 is None:
        word1, word2 = word1.split(' / ')
    import matplotlib.pyplot as plt
    from matplotlib import collections as mc

    horizontals, verticals1, verticals2 = get_segments(word1, word2)

    v1_segs = mc.LineCollection(verticals1, colors='r', linewidths=4)
    v2_segs = mc.LineCollection(verticals2, colors='pink', linewidth=4)
    h1_segs = mc.LineCollection(horizontals, colors='w', linewidths=10)
    h2_segs = mc.LineCollection(horizontals, colors='b', linewidths=4)

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.add_collection(v1_segs)
    ax1.add_collection(v2_segs)
    ax1.add_collection(h1_segs)
    ax1.add_collection(h2_segs)
    ax1.autoscale()

    plt.savefig(f"{word1}-{word2}.png")
    fig.show()
