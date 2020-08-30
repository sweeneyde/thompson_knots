import enum
import itertools
from collections import defaultdict, deque
from functools import lru_cache

__all__ = ["construct_trees", "words_to_gauss", "HalfPlane"]

class CrossingType(enum.IntEnum):
    OVER = +1
    UNDER = -1

    def opposite(self):
        return CrossingType(-self)


class HalfPlane(enum.Enum):
    TOP = +1
    BOTTOM = -1


def validate(word):
    """
    >>> validate('o')
    >>> validate('(oo)')
    >>> validate('(o(oo))')
    >>> validate('(o(oo))')
    >>> validate('(o(o((oo)o)))')
    >>> validate('oo')
    Traceback (most recent call last):
      ...
    ValueError: Couldn't parse 'oo', stopped at 'oo'.
    """
    if not set(word) <= {"(", "o", ")"}:
        raise ValueError(f"Bad characters in {word!r}")

    reduced = word
    for _ in range(len(word)):
        reduced = reduced.replace("(oo)", "o")
        if reduced == "o":
            break
    else:  # didn't get reduced to one root
        raise ValueError(f"Couldn't parse {word!r}, stopped at {reduced!r}.")


class Vertex:
    __slots__ = "parent", "left", "right", "corresponding", "label", "half_plane"
    __hash__ = object.__hash__

    def __repr__(self):
        if self.is_leaf():
            return f"Leaf {hex(id(self) % 997)[-3:]}"
        else:
            return f"Vertex {self.label}"

    def is_leaf(self):
        return self.left is None

    @classmethod
    def parent_of(cls, left, right):
        parent = cls()
        left.parent = parent
        right.parent = parent
        parent.parent = None
        parent.left = left
        parent.right = right
        return parent

    @classmethod
    def leaf(cls):
        leaf = cls()
        leaf.left = leaf.right = leaf.parent = None
        return leaf

    def in_order_vertices(self):
        if self.is_leaf():
            yield self
        else:
            yield from self.left.in_order_vertices()
            yield self
            yield from self.right.in_order_vertices()

    def breadth_first_vertices(self):
        q = deque([self])
        while q:
            vertex = q.popleft()
            yield vertex
            if not vertex.is_leaf():
                q.append(vertex.left)
                q.append(vertex.right)

def construct_tree(word) -> Vertex:
    """
    >>> root = construct_tree('(o(o((oo)o)))')
    >>> leaves = [root.left, root.right.left, root.right.right.right, \
                  root.right.right.left.left, root.right.right.left.right]
    >>> all(x.is_leaf() for x in leaves)
    True
    """
    validate(word)
    word = [c if c != "o" else Vertex.leaf() for c in word]
    while len(word) > 1:
        for i in range(len(word)):
            if word[i] == '(' and word[i + 3] == ')':
                word[i:i + 4] = [Vertex.parent_of(word[i + 1], word[i + 2])]
                break  # (start over)
    (root,) = word
    return root


def link_trees(tree1, tree2):
    """Zip the trees together."""
    for top, bottom, in zip(tree1.in_order_vertices(),
                            tree2.in_order_vertices()):
        top.corresponding = bottom
        bottom.corresponding = top


def label_trees(tree1, tree2):
    """Label each non-leaf node with a unique integer."""
    label_to_crossing = {}
    label_generator = itertools.count(1)
    for tree in (tree1, tree2):
        for vertex in tree.in_order_vertices():
            if not vertex.is_leaf():
                label = next(label_generator)
                vertex.label = label
                label_to_crossing[label] = vertex
    return label_to_crossing

@lru_cache(maxsize=100)
def construct_trees(word1, word2):
    c1 = word1.count("o")
    c2 = word2.count("o")
    if c1 != c2:
        raise ValueError("Different sized trees.")
    if c1 <= 1:
        raise ValueError("Cannot correctly handle degenerate tree.")

    tree1 = construct_tree(word1)
    tree2 = construct_tree(word2)
    link_trees(tree1, tree2)
    label_to_vertex = label_trees(tree1, tree2)

    for vertex in tree1.in_order_vertices():
        vertex.half_plane = HalfPlane.TOP
    for vertex in tree2.in_order_vertices():
        vertex.half_plane = HalfPlane.BOTTOM

    return tree1, tree2, label_to_vertex


def words_to_gauss(word1: str, word2: str):
    """
    >>> ((comp1, comp2), signs) = words_to_gauss("(o(o((oo)o)))", "(((oo)o)(oo))")
    >>> comp1
    [1, 5, 2, -4, -8, 7, -6, -2]
    >>> comp2
    [-1, -7, -3, 4, 8, 3, 6, -5]
    >>> signs
    [-1, 1, -1, -1, 1, -1, -1, 1]
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)

    seen = set()
    directions_taken = defaultdict(set)  # Vertex --> {direction, direction}
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

            directions_taken[node].add(direction)
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

    gauss_components = []
    for vertex in label_to_vertex.values():
        for start_direction in (LEFT, PARENT):
            pairs = list(traverse(vertex, start_direction))
            if pairs:
                component = [vertex.label * over_under
                             for vertex, over_under in pairs]
                gauss_components.append(component)

    crossing_signs = []
    for label, vertex in label_to_vertex.items():
        taken = directions_taken[vertex]
        booleans = [
            (CORRESPONDING in taken),
            (LEFT in taken),
            (vertex.half_plane == HalfPlane.BOTTOM),
        ]
        sign = (-1) ** sum(booleans)
        crossing_signs.append(sign)

    return [gauss_components, crossing_signs]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
