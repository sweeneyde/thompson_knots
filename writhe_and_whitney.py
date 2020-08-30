from thompson import construct_trees, CrossingType, HalfPlane
from collections import defaultdict

def words_to_whitney(word1: str, word2: str):
    """
    >>> words_to_whitney("(o(oo))", "((oo)o)")
    1
    >>> words_to_whitney("((o(oo))o)", "((oo)(oo))")
    3
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)
    seen = set()
    directions_taken = defaultdict(list)  # Vertex --> {direction, direction}
    LEFT, RIGHT, CORRESPONDING, PARENT = "left right corresponding parent".split()

    def traverse(start_node, start_direction):
        direction = start_direction
        node = start_node
        while True:
            # leaves aren't crossings.
            assert not node.is_leaf()

            if direction in (LEFT, RIGHT):
                over_under = CrossingType.OVER
            else:
                over_under = CrossingType.UNDER
            pair = (node, over_under)
            if pair in seen:
                return
            seen.add(pair)
            yield pair

            directions_taken[node].append(direction)
            next_node = getattr(node, direction)

            if direction == PARENT:
                if next_node is None:
                    node = tree2 if node is tree1 else tree1
                    direction = CORRESPONDING
                else:
                    direction = LEFT if node is next_node.right else RIGHT
                    node = next_node
            elif direction == CORRESPONDING:
                node = next_node
                direction = PARENT
            else:
                assert direction in (LEFT, RIGHT)
                if next_node.is_leaf():
                    other_leaf = next_node.corresponding
                    node = other_leaf.parent
                    direction = LEFT if other_leaf is node.right else RIGHT
                else:
                    node = next_node
                    direction = CORRESPONDING


    positive = {
        (HalfPlane.TOP, LEFT, PARENT),
        (HalfPlane.TOP, PARENT, RIGHT),
        (HalfPlane.TOP, RIGHT, CORRESPONDING),
        (HalfPlane.TOP, CORRESPONDING, LEFT),
        (HalfPlane.BOTTOM, LEFT, CORRESPONDING),
        (HalfPlane.BOTTOM, CORRESPONDING, RIGHT),
        (HalfPlane.BOTTOM, RIGHT, PARENT),
        (HalfPlane.BOTTOM, PARENT, LEFT),
    }

    vertex = tree2
    start_direction = CORRESPONDING
    _ = list(traverse(vertex, start_direction))
    assert len(directions_taken) % 2 == 0
    assert set(directions_taken.keys()) == set(label_to_vertex.values())

    whitney = 1
    for v, (first, second) in directions_taken.items():
        if (v.half_plane, first, second) in positive:
            whitney += 1
        else:
            whitney -= 1

    return whitney

def words_to_writhe(word1: str, word2: str):
    """
    >>> words_to_writhe("(o((oo)(oo)))", "(((oo)(oo))o)")
    4
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)
    seen = set()
    directions_taken = defaultdict(list)  # Vertex --> {direction, direction}
    LEFT, RIGHT, CORRESPONDING, PARENT = "left right corresponding parent".split()

    def traverse(start_node, start_direction):
        direction = start_direction
        node = start_node
        while True:
            # leaves aren't crossings.
            assert not node.is_leaf()

            if direction in (LEFT, RIGHT):
                over_under = CrossingType.OVER
            else:
                over_under = CrossingType.UNDER
            pair = (node, over_under)
            if pair in seen:
                return
            seen.add(pair)
            yield pair

            directions_taken[node].append(direction)
            next_node = getattr(node, direction)

            if direction == PARENT:
                if next_node is None:
                    node = tree2 if node is tree1 else tree1
                    direction = CORRESPONDING
                else:
                    direction = LEFT if node is next_node.right else RIGHT
                    node = next_node
            elif direction == CORRESPONDING:
                node = next_node
                direction = PARENT
            else:
                assert direction in (LEFT, RIGHT)
                if next_node.is_leaf():
                    other_leaf = next_node.corresponding
                    node = other_leaf.parent
                    direction = LEFT if other_leaf is node.right else RIGHT
                else:
                    node = next_node
                    direction = CORRESPONDING


    positive = {
        (HalfPlane.TOP, RIGHT, PARENT),
        (HalfPlane.TOP, PARENT, RIGHT),
        (HalfPlane.TOP, LEFT, CORRESPONDING),
        (HalfPlane.TOP, CORRESPONDING, LEFT),
        (HalfPlane.BOTTOM, RIGHT, CORRESPONDING),
        (HalfPlane.BOTTOM, CORRESPONDING, RIGHT),
        (HalfPlane.BOTTOM, LEFT, PARENT),
        (HalfPlane.BOTTOM, PARENT, LEFT),
    }

    vertex = tree2
    start_direction = CORRESPONDING
    _ = list(traverse(vertex, start_direction))
    assert len(directions_taken) % 2 == 0
    assert set(directions_taken.keys()) == set(label_to_vertex.values())

    writhe = 0
    for v, (first, second) in directions_taken.items():
        if (v.half_plane, first, second) in positive:
            writhe += 1
        else:
            writhe -= 1

    return writhe

def words_to_whitneys(word1: str, word2: str):
    """
    >>> words_to_whitneys("(o(oo))", "((oo)o)")
    (1,)
    >>> words_to_whitneys("((o(oo))o)", "((oo)(oo))")
    (3,)
    >>> words_to_whitneys("((o(oo))(o(oo)))", "((o((o(oo))o))o)")
    (-2, 2)
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)
    seen = set()
    directions_taken = defaultdict(list)  # Vertex --> {direction, direction}
    LEFT, RIGHT, CORRESPONDING, PARENT = "left right corresponding parent".split()

    def traverse(start_node, start_direction):
        direction = start_direction
        node = start_node
        half_turns = 0
        halfplane_dir_to_half_turn1 = {
            (HalfPlane.TOP, LEFT): 1,
            (HalfPlane.TOP, RIGHT): -1,
            (HalfPlane.BOTTOM, LEFT): -1,
            (HalfPlane.BOTTOM, RIGHT): 1
        }
        while True:
            # leaves aren't crossings.
            assert not node.is_leaf()

            if direction in (LEFT, RIGHT):
                over_under = CrossingType.OVER
            else:
                over_under = CrossingType.UNDER
            pair = (node, over_under)
            if pair in seen:
                assert half_turns % 2 == 0
                return half_turns // 2
            seen.add(pair)
            yield pair

            directions_taken[node].append(direction)
            if direction in (LEFT, RIGHT):
                half_turns += halfplane_dir_to_half_turn1[node.half_plane, direction]
            next_node = getattr(node, direction)

            if direction == PARENT:
                if next_node is None:
                    node = tree2 if node is tree1 else tree1
                    direction = CORRESPONDING
                    half_turns += 2
                else:
                    direction = LEFT if node is next_node.right else RIGHT
                    node = next_node
            elif direction == CORRESPONDING:
                node = next_node
                direction = PARENT
            else:
                assert direction in (LEFT, RIGHT)
                if next_node.is_leaf():
                    other_leaf = next_node.corresponding
                    node = other_leaf.parent
                    direction = LEFT if other_leaf is node.right else RIGHT
                else:
                    node = next_node
                    direction = CORRESPONDING


    whitneys = []
    for vertex in tree2.breadth_first_vertices():
        if vertex.is_leaf():
            continue
        empty = True
        try:
            traversal = traverse(vertex, CORRESPONDING)
            while True:
                next(traversal)
                empty = False
        except StopIteration as exc:
            if not empty:
                whitneys.append(exc.value)

    assert len(directions_taken) % 2 == 0
    assert set(directions_taken.keys()) == set(label_to_vertex.values())
    return tuple(sorted(whitneys))

def words_to_writhes_and_whitneys(word1: str, word2: str):
    """
    >>> words_to_writhes_and_whitneys("((o(oo))(o(oo)))", "((o((o(oo))o))o)")
    ((-1, -2), (-1, 2))
    >>> words_to_writhes_and_whitneys("(((o(oo))(oo))o)", "(o((o(oo))(oo)))")
    ((-1, 0), (-1, 0))
    >>> words_to_writhes_and_whitneys("(o(o((o((o(oo))o))o)))", "((o((o(oo))o))(o(oo)))")
    ((-1, 0), (-1, 0))
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)
    seen = set()
    directions_taken = defaultdict(list)  # Vertex --> {direction, direction}
    LEFT, RIGHT, CORRESPONDING, PARENT = "left right corresponding parent".split()

    face_twin_mapping = {
        RIGHT: PARENT,
        PARENT: RIGHT,
        LEFT: CORRESPONDING,
        CORRESPONDING: LEFT
    }

    todo = {(tree2, CORRESPONDING)}
    done = set()

    def traverse(start_node, start_direction):
        direction = start_direction
        node = start_node
        half_turns = 0
        halfplane_dir_to_half_turn1 = {
            (HalfPlane.TOP, LEFT): 1,
            (HalfPlane.TOP, RIGHT): -1,
            (HalfPlane.BOTTOM, LEFT): -1,
            (HalfPlane.BOTTOM, RIGHT): 1
        }
        while True:
            # leaves aren't crossings.
            assert not node.is_leaf()

            if direction in (LEFT, RIGHT):
                over_under = CrossingType.OVER
            else:
                over_under = CrossingType.UNDER
            pair = (node, over_under)
            if pair in seen:
                assert half_turns % 2 == 0
                return half_turns // 2
            seen.add(pair)
            done.add((node, direction))
            todo.add((node, face_twin_mapping[direction]))
            yield (node, direction)

            directions_taken[node].append(direction)
            if direction in (LEFT, RIGHT):
                half_turns += halfplane_dir_to_half_turn1[node.half_plane, direction]
            next_node = getattr(node, direction)

            if direction == PARENT:
                if next_node is None:
                    node = tree2 if node is tree1 else tree1
                    assert node == tree2
                    direction = CORRESPONDING
                    half_turns += 2
                else:
                    direction = LEFT if node is next_node.right else RIGHT
                    node = next_node
            elif direction == CORRESPONDING:
                node = next_node
                direction = PARENT
            else:
                assert direction in (LEFT, RIGHT)
                if next_node.is_leaf():
                    other_leaf = next_node.corresponding
                    node = other_leaf.parent
                    direction = LEFT if other_leaf is node.right else RIGHT
                else:
                    node = next_node
                    direction = CORRESPONDING


    positive = {
        (HalfPlane.TOP, RIGHT, PARENT),
        (HalfPlane.TOP, PARENT, RIGHT),
        (HalfPlane.TOP, LEFT, CORRESPONDING),
        (HalfPlane.TOP, CORRESPONDING, LEFT),
        (HalfPlane.BOTTOM, RIGHT, CORRESPONDING),
        (HalfPlane.BOTTOM, CORRESPONDING, RIGHT),
        (HalfPlane.BOTTOM, LEFT, PARENT),
        (HalfPlane.BOTTOM, PARENT, LEFT),
    }


    writhe_whitneys = []
    while todo:
        vertex, direction = todo.pop()
        if vertex.is_leaf():
            continue
        if (vertex, direction) in done:
            continue
        empty = True
        traversal = traverse(vertex, direction)

        try:
            node_dirs = []
            while True:
                node_dirs.append(next(traversal))
                empty = False
        except StopIteration as exc:
            if empty:
                continue
            whitney = exc.value

        node_to_dirs = defaultdict(list)
        for node, dir in node_dirs:
            node_to_dirs[node].append(dir)
        self_intersections = [(node, dirs) for node, dirs in node_to_dirs.items()
                              if len(dirs) == 2]

        writhe = 0
        for v, (dir1, dir2) in self_intersections:
            if (v.half_plane, dir1, dir2) in positive:
                writhe += 1
            else:
                writhe -= 1

        writhe_whitneys.append((writhe, whitney))

    assert len(directions_taken) % 2 == 0
    assert set(directions_taken.keys()) == set(label_to_vertex.values())
    return tuple(sorted(writhe_whitneys))

if __name__ == '__main__':

    # with open("oriented mirrored hopf trees up to 10.txt") as f:
    #     for line in map(str.strip, f):
    #         pair = line.split(' / ')
    #         print(line)
    #         print('   ', *words_to_writhes_and_whitneys(*pair))

    data = []
    while True:
        line = input()
        if not line:
            break
        data.append(line.strip())

    unique = set()
    for line in data:
        pair = line.split(' / ')
        pairs = words_to_writhes_and_whitneys(*pair)
        print(line)
        print('   ', *pairs)
        unique.add(pairs)
    print("=== Unique ===")
    for pairs in unique:
        print(*pairs)

    # import oriented
    #
    # for pair in oriented.oriented_pairs(7):
    #     pairset = words_to_writhes_and_whitneys(*pair)
    #     unique_writhes = set(x[0] for x in pairset)
    #     if len(unique_writhes) > 1:
    #         print()
    #         print(pair)
    #         print(pairset)
    #         print(unique_writhes)