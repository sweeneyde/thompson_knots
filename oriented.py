from link_classification import binary_words, is_irreducible
from collections import defaultdict, Counter
from thompson import construct_tree, construct_trees
from itertools import product

def is_bipartite(adj_list):
    """adj_list must not be directed"""
    A, B = -123, +123
    colors = {}
    v = next(iter(adj_list))
    stack = [(A, v)]
    while stack:
        color, v = stack.pop()
        if v in colors:
            continue
        colors[v] = color
        for w in adj_list[v]:
            if w not in colors:
                stack += [(-color, w)]
            elif colors[w] == color:
                return False
    assert colors.keys() == adj_list.keys(), "must be connected"
    return True

def is_oriented(word1: str, word2: str):
    """
    >>> is_oriented("((o(oo))o)", "(o(o(oo)))")
    True
    >>> is_oriented("(o(oo))", "((oo)o)")
    False
    """
    tree1, tree2, label_to_vertex = construct_trees(word1, word2)
    OUT = "OUT"
    pairs = set()

    index = {OUT: 0}

    verts_1 = (v for v in tree1.in_order_vertices() if not v.is_leaf())
    verts_2 = (v for v in tree2.in_order_vertices() if not v.is_leaf())
    for i, (a, b) in enumerate(zip(verts_1, verts_2), start=1):
        index[a] = index[b] = i

    for root in tree1, tree2:
        hill_children = defaultdict(list)
        # hill_children[OUT] = root
        hill_parent = {root: OUT}

        for v in root.breadth_first_vertices():
            if v.is_leaf():
                continue
            left, right = v.left, v.right
            if not right.is_leaf():
                # hill_children[v].append(right)
                hill_parent[right] = v
            if not left.is_leaf():
                my_parent = hill_parent[v]
                # hill_children[my_parent].append(left)
                hill_parent[left] = my_parent

        for child, parent in hill_parent.items():
            a, b = index[child], index[parent]
            pairs |= {(a, b), (b, a)}

    adj_list = defaultdict(list)
    for a, b in pairs:
        adj_list[a].append(b)

    return is_bipartite(adj_list)


def word_to_bipartition(word):
    root = construct_tree(word)
    OUT = "OUT"
    index = {OUT: 0}

    verts = (v for v in root.in_order_vertices() if not v.is_leaf())
    for i, v in enumerate(verts, start=1):
        index[v] = i
    n = i + 1

    hill_parent = {root: OUT}
    for v in root.breadth_first_vertices():
        if v.is_leaf():
            continue
        left, right = v.left, v.right
        if not right.is_leaf():
            hill_parent[right] = v
        if not left.is_leaf():
            my_parent = hill_parent[v]
            hill_parent[left] = my_parent

    result = [None] * n
    result[0] = -1
    for child, parent in hill_parent.items():
        # dicts are ordered, so this shouldn't fail.
        result[index[child]] = -result[index[parent]]
    assert None not in result
    return ''.join(map({-1:'A', 1:'B'}.get, result))

def number_of_oriented_pairs(n):
    counts = Counter(map(word_to_bipartition, binary_words(n)))
    return sum(x**2 for x in counts.values())

def oriented_pairs(n, filterfunc=None):
    bipartition_to_words = defaultdict(list)
    for word in binary_words(n):
        bipartition = word_to_bipartition(word)
        bipartition_to_words[bipartition].append(word)

    for arr in bipartition_to_words.values():
        yield from filter(filterfunc, product(arr, repeat=2))

if __name__ == '__main__':
    def iter_len(x):
        return sum(1 for y in x)

    for n in range(2, 20):
        print(n, iter_len(oriented_pairs(n, is_irreducible)))
