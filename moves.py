from functools import lru_cache, wraps
from thompson import validate
from collections import Counter
import re

cache = lru_cache(maxsize=None)
lru_cache = lru_cache(maxsize=128)

unlink_trees = {tuple(line.split(" / ")) for line in
                open("unlink_trees8.txt").read().splitlines()}


@lru_cache
def paren_pair_indices(word):
    result = set()
    stack = []
    count = 0
    for c in word:
        if c == "(":
            stack.append(count)
        elif c == ")":
            pair = (stack.pop(), count)
            result.add(pair)
        elif c == "o":
            count += 1
    assert not stack
    return frozenset(result)


@lru_cache
def leaf_index(word):
    index = []
    for i, c in enumerate(word):
        if c == 'o':
            index.append(i)
    return tuple(index)


def indexset_to_word(pairs):
    """
    >>> from link_classification import binary_words
    >>> for word in binary_words(7):
    ...     pairs = paren_pair_indices(word)
    ...     assert word == indexset_to_word(pairs)
    """
    pairs = set(pairs)
    lefts = Counter(a for a, b in pairs)
    rights = Counter(b for a, b in pairs)
    n = max(rights)

    builder = ["(" * lefts[0]]
    assert rights[0] == 0
    assert lefts[n] == 0

    for i in range(1, n + 1):
        builder.append("o")
        builder.append(")" * rights[i])
        builder.append("(" * lefts[i])

    return ''.join(builder)


##################################


class TreePair(tuple):
    __slots__ = ()

    def __new__(cls, word1, word2=None):
        if word2 is None:
            word1, word2 = word1.split(" / ")
        validate(word1)
        validate(word2)
        assert word1.count("o") == word2.count("o")
        return tuple.__new__(cls, (word1, word2))

    @classmethod
    def from_sets(cls, set1, set2):
        word1 = indexset_to_word(set1).strip("o")
        word2 = indexset_to_word(set2).strip("o")
        return cls.__new__(cls, word1, word2)

    def __str__(self):
        return " / ".join(self)

    def __repr__(self):
        return f"{type(self).__qualname__}({str(self)!r})"

    @lru_cache
    def paren_pair_sets(self):
        return paren_pair_indices(self[0]), paren_pair_indices(self[1])

    @lru_cache
    def leaf_indexes(self):
        return leaf_index(self[0]), leaf_index(self[1])

    @lru_cache
    def num_leaves(self):
        return self[0].count("o")


##################################


all_move_functions = set()


def mirror_move(func):
    @wraps(func)
    def wrapper(pair: TreePair):
        return (TreePair(x, y) for (y, x) in func(TreePair(*pair[::-1])))

    wrapper.__name__ = func.__name__ + "_mirrored"
    return wrapper


def make_move_function(also_mirror: bool):
    def decorator(func):
        all_move_functions.add(func)
        if also_mirror:
            all_move_functions.add(mirror_move(func))
        return func

    return decorator


reverse_char = {'(': ')', ')': '(', 'o': 'o'}.get


@lru_cache
def reverse_word(word):
    """
    >>> reverse_word('((oo)o)')
    '(o(oo))'
    """
    return ''.join(map(reverse_char, word[::-1]))


##################################


@make_move_function(also_mirror=True)
def move_rotate(pair: TreePair):
    """Rotate by a half-turn."""
    word1, word2 = pair
    yield TreePair(reverse_word(word2), reverse_word(word1))


@make_move_function(also_mirror=True)
def move_local1(pair: TreePair):
    """Turn 4 leaves into 3."""
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()
    for i in range(n):
        top_required = {(i, i + 4), (i, i + 3), (i + 1, i + 3)}
        bottom_required = {(i, i + 2), (i + 2, i + 4)}

        if top_required <= set1 and bottom_required <= set2:
            # We can do the move.
            word1, word2 = map(list, pair)
            leaf_index1, leaf_index2 = pair.leaf_indexes()

            li1 = leaf_index1[i]
            assert word1[li1 - 1:li1 + 6] == list("(o(oo))")
            word1[li1 - 1:li1 + 6] = list("(oo)")

            li2 = leaf_index2[i]
            assert word2[li2 - 1:li2 + 3] == list("(oo)")
            word2[li2 - 1:li2 + 3] = list("o")

            yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_outside1(pair: TreePair):
    """Move a slat from bottom to top."""
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()
    if (0, 2) in set1 and (1, n) in set2:
        # We can do the move
        word1, word2 = map(list, pair)
        leaf_index1, leaf_index2 = pair.leaf_indexes()

        li1 = leaf_index1[0]
        assert word1[li1 - 1:li1 + 3] == list("(oo)")
        word1[li1 - 1:li1 + 3] = list("o")
        word1 = list("(o") + word1 + list(")")

        assert word2[:3] == list("(o(") and word2[-2:] == list("))")
        word2 = word2[2:-1]
        li2 = word2.index('o')
        word2[li2:li2 + 1] = list("(oo)")

        yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_local2(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()

    for i in range(n):
        top_required = {(i + 1, i + 4), (i + 2, i + 4)}
        bottom_required = {(i, i + 4), (i, i + 3), (i + 1, i + 3)}

        if top_required <= set1 and bottom_required <= set2:
            # We can do the move.
            word1, word2 = map(list, pair)
            leaf_index1, leaf_index2 = pair.leaf_indexes()

            li1 = leaf_index1[i + 1]
            assert word1[li1 - 1:li1 + 6] == list("(o(oo))")
            word1[li1 - 1:li1 + 6] = list("o")

            li2 = leaf_index2[i]
            assert word2[li2 - 2:li2 + 8] == list("((o(oo))o)")
            word2[li2 - 2:li2 + 8] = list("(oo)")

            yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_local2_improved(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()
    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for i in range(n):
        li1, li2 = leaf_index1[i], leaf_index2[i]
        word1, word2 = pair
        if word1[li1 - 1:li1 + 6] != "(o((oo)":
            continue
        if word2[li2 - 2:li2 + 5] != "((oo)o)":
            continue

        rest = word1[li1 + 6:]
        leaves_in_sub = 1
        while not rest.startswith('o)'):
            rest = rest.replace('(oo)', 'o', 1)
            leaves_in_sub += 1
        last_leaf_in_sub = i + 2 + leaves_in_sub
        li_last = leaf_index1[last_leaf_in_sub]

        word1, word2 = map(list, pair)

        # good thing parentheses are fungible
        # top: (o((oo)?)) --> (o?)
        assert word1[li_last + 1] == ')'
        del word1[li_last + 1]
        assert word1[li1 - 1:li1 + 6] == list("(o((oo)")
        word1[li1 - 1:li1 + 6] = list("(o")

        assert word2[li2 - 2:li2 + 5] == list("((oo)o)")
        word2[li2 - 2:li2 + 5] = list("o")

        yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_local2_improved2(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()
    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for i in range(n):
        li1, li2 = leaf_index1[i], leaf_index2[i]
        word1, word2 = pair
        if word2[li2 - 2:li2 + 5] != "((oo)o)":
            continue

        if word1[li1 - 1:li1 + 1] != "(o":
            continue
        for depth, c in enumerate(word1[li1 + 1:]):
            if c != "(":
                break

        assert word1[li1 + 1:][:depth] == "(" * depth

        if word1[li1 + 1 + depth - 1:][:4] != "(oo)":
            continue

        # top: (o(((((oo)?)?)?)?) --> ((((o?)?)?)?)
        # bottom: ((oo)o)         -->     o

        assert word1[li1 + 1:].startswith("(" * depth + "oo)")
        rest = word1[li1 + 1:][depth + 3:]
        leaves_in_subs = 0
        for j in range(depth - 1):
            leaves_in_subs += 1
            while not rest.startswith('o)'):
                rest = rest.replace('(oo)', 'o', 1)
                leaves_in_subs += 1
            rest = rest[2:]

        last_leaf_in_sub = i + 2 + leaves_in_subs
        li_last = leaf_index1[last_leaf_in_sub]

        word1, word2 = map(list, pair)
        # good thing parentheses are fungible
        assert word1[li_last + 1] == ')'
        del word1[li_last + 1]
        chunk = f"(o{'(' * depth}oo)"
        replacement_chunk = f"{'(' * (depth - 1)}o"
        assert word1[li1 - 1:li1 + len(chunk) - 1] == list(chunk)
        word1[li1 - 1:li1 + len(chunk) - 1] = list(replacement_chunk)

        assert word2[li2 - 2:li2 + 5] == list("((oo)o)")
        word2[li2 - 2:li2 + 5] = list("o")

        if len(word1) > 1:
            yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_local3(pair: TreePair):
    """Jake's thing"""
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()

    for i in range(n):
        top_required = {(i, i + 4), (i + 1, i + 4), (i + 2, i + 4)}
        bottom_required = {(i, i + 2), (i, i + 3)}

        if top_required <= set1 and bottom_required <= set2:
            # We can do the move.
            word1, word2 = map(list, pair)
            leaf_index1, leaf_index2 = pair.leaf_indexes()

            li1 = leaf_index1[i]
            assert word1[li1 - 1:li1 + 9] == list("(o(o(oo)))")
            word1[li1 - 1:li1 + 9] = list("((oo)o)")

            li2a = leaf_index2[i + 3]
            assert word2[li2a:li2a + 1] == list("o")
            word2[li2a:li2a + 1] = list("(oo)")

            li2b = leaf_index2[i]
            assert word2[li2b - 2:li2b + 5] == list("((oo)o)")
            word2[li2b - 2:li2b + 5] = list("o")
            yield TreePair(''.join(word1), ''.join(word2))


# # (o((o?)(?o)))
# outside2_top_pattern = re.compile(
#     re.escape("(o((o")
#     + "(.+)"  # 1
#     + re.escape(")(")
#     + "(.+)"  # 2
#     + re.escape("o)))")
# )
#
# # (((o(o?))?)o)
# outside_bottom_pattern = re.compile(
#     re.escape("(((o(o")
#     + "(.+)"  # 1
#     + re.escape("))")
#     + "(.+)"  # 2
#     + re.escape(")o)")
# )
#
#

@make_move_function(also_mirror=True)
def move_outside2(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()

    for bottom_i in range(n):
        bottom_required = {(0, n), (0, n-1), (0, bottom_i), (1, bottom_i)}
        if len(bottom_required) < 4 or not (bottom_required <= set2):
            continue
        if {(1, i) for i in range(bottom_i)} & set2:
            continue
        if {(0, i) for i in range(bottom_i+1, n-1)} & set2:
            continue
        for top_i in range(n):
            top_required = {(0, n), (1, n), (1, top_i), (top_i, n)}
            if len(top_required) < 4 or not (top_required <= set1):
                continue
            if {(i, n) for i in range(top_i+1, n)} & set1:
                continue
            if {(1, i) for i in range(2, top_i)} & set1:
                continue
            word1, word2 = map(list, pair)
            leaf_index1, leaf_index2 = pair.leaf_indexes()

            assert word1[:2] == list("(o")
            assert word1[-1:] == list(")")
            del word1[:2]
            del word1[-1:]

            li2b = leaf_index2[bottom_i-1]
            assert word2[li2b:li2b+2] == list("o)")
            del word2[li2b+1:li2b+2]

            li2a = leaf_index2[0]
            assert word2[li2a-1:li2a+1] == list("(o")
            del word2[li2a-1:li2a+1]

            yield TreePair("".join(word1), "".join(word2))




    #
    # match1 = outside2_top_pattern.fullmatch(word1)
    # if match1 is None:
    #     return
    #
    # match2 = outside_bottom_pattern.fullmatch(word2)
    # if match2 is None:
    #     return
    #
    # top_a, top_b = match1.groups()
    # bottom_a, bottom_b = match2.groups()
    #
    # new_top = f"((o{top_a})({top_b}o))"
    # new_bottom = f"(((o{bottom_a}){bottom_b})o)"
    # yield TreePair(new_top, new_bottom)


@make_move_function(also_mirror=True)
def move_insert_block(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()
    intersection = set1 & set2 - {(0, n)}

    if not intersection:
        return

    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for lo, hi in intersection:
        subset1 = {(a, b) for (a, b) in set1 if lo <= a and b <= hi}
        subset2 = {(a, b) for (a, b) in set2 if lo <= a and b <= hi}
        sub1, sub2 = subpair = TreePair.from_sets(subset1, subset2)

        word1, word2 = pair
        top_search_start = 0 if lo == 0 else max(0, leaf_index1[lo - 1] + 1)
        top_start = word1.index(sub1, top_search_start)
        bottom_search_start = 0 if lo == 0 else max(0, leaf_index2[lo - 1] + 1)
        bottom_start = word2.index(sub2, bottom_search_start)
        assert word1[:top_start].count("o") == word2[:bottom_start].count("o")

        word1, word2 = map(list, pair)
        assert word1[top_start:top_start + len(sub1)] == list(sub1)
        word1[top_start:top_start + len(sub1)] = ["o"]
        assert word2[bottom_start:bottom_start + len(sub2)] == list(sub2)
        word2[bottom_start:bottom_start + len(sub2)] = ["o"]

        outer_pair = TreePair("".join(word1), "".join(word2))

        if tuple(subpair) in unlink_trees:
            yield outer_pair

        if tuple(outer_pair) in unlink_trees:
            yield subpair


@make_move_function(also_mirror=True)
def move_local4(pair: TreePair):
    """delete 3 slabs"""
    word1, word2 = pair
    n = pair.num_leaves()
    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for i in range(n):
        li1, li2 = leaf_index1[i], leaf_index2[i]
        if not word1[li1 - 1:].startswith("(o(o(o(o"):
            continue
        if not word2[li2 - 3:].startswith("(((oo)o)o)"):
            continue

        word1list = list(word1)
        word2list = list(word2)

        rest = word1[li1 + 7:]
        leaves_in_sub = 1
        while not rest.startswith("o"):
            rest = rest.replace("(oo)", "o", 1)
            leaves_in_sub += 1

        assert rest.startswith("o))))")
        last_in_sub = i + 3 + leaves_in_sub
        last_in_sub_index = leaf_index1[last_in_sub]

        assert word1list[last_in_sub_index + 1:last_in_sub_index + 5] == list("))))")
        word1list[last_in_sub_index + 1:last_in_sub_index + 5] = list(")")
        assert word1list[li1 - 1:li1 + 7] == list("(o(o(o(o")
        word1list[li1 - 1:li1 + 7] = list("(o")

        assert word2list[li2 - 3:li2 + 7] == list("(((oo)o)o)")
        word2list[li2 - 3:li2 + 7] = list("o")

        yield TreePair("".join(word1list), "".join(word2list))


@make_move_function(also_mirror=True)
def move_local5(pair: TreePair):
    """Delete 1.5 slabs"""
    word1, word2 = pair
    n = pair.num_leaves()
    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for i in range(n):
        li1, li2 = leaf_index1[i], leaf_index2[i]
        if not word1[li1 - 1:].startswith("(o((oo)"):
            continue
        if not word2[li2 - 2:].startswith("((oo)o)"):
            continue

        word1list = list(word1)
        word2list = list(word2)

        rest = word1[li1 + 6:]
        leaves_in_sub = 1
        while not rest.startswith("o"):
            rest = rest.replace("(oo)", "o", 1)
            leaves_in_sub += 1

        assert rest.startswith("o))")
        last_in_sub = i + 2 + leaves_in_sub
        last_in_sub_index = leaf_index1[last_in_sub]

        assert word1list[last_in_sub_index + 1:last_in_sub_index + 3] == list("))")
        word1list[last_in_sub_index + 1:last_in_sub_index + 3] = list(")")
        assert word1list[li1 - 1:li1 + 6] == list("(o((oo)")
        word1list[li1 - 1:li1 + 6] = list("(o")

        assert word2list[li2 - 2:li2 + 5] == list("((oo)o)")
        word2list[li2 - 2:li2 + 5] = list("o")

        yield TreePair("".join(word1list), "".join(word2list))

@make_move_function(also_mirror=True)
def move_local6(pair: TreePair):
    """Delete 2.5 slabs"""
    word1, word2 = pair
    n = pair.num_leaves()
    leaf_index1, leaf_index2 = pair.leaf_indexes()

    for i in range(n):
        li1, li2 = leaf_index1[i], leaf_index2[i]
        if not word1[li1 - 1:].startswith("(o(o((oo)"):
            continue
        if not word2[li2 - 3:].startswith("(((oo)o)o)"):
            continue

        word1list = list(word1)
        word2list = list(word2)

        rest = word1[li1 + 8:]
        leaves_in_sub = 1
        while not rest.startswith("o"):
            rest = rest.replace("(oo)", "o", 1)
            leaves_in_sub += 1

        assert rest.startswith("o)))")
        last_in_sub = i + 3 + leaves_in_sub
        last_in_sub_index = leaf_index1[last_in_sub]

        assert word1list[last_in_sub_index + 1:last_in_sub_index + 4] == list(")))")
        word1list[last_in_sub_index + 1:last_in_sub_index + 4] = list(")")
        assert word1list[li1 - 1:li1 + 8] == list("(o(o((oo)")
        word1list[li1 - 1:li1 + 8] = list("(o")

        assert word2list[li2 - 3:li2 + 7] == list("(((oo)o)o)")
        word2list[li2 - 3:li2 + 7] = list("o")

        yield TreePair("".join(word1list), "".join(word2list))

@make_move_function(also_mirror=True)
def move_local_twist(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()

    for i in range(n):
        top_required = {(i, i+3), (i+1, i+3), (i+3, i+5)}
        bottom_required = {(i, i+2), (i+2, i+4), (i+2, i+5)}

        if top_required <= set1 and bottom_required <= set2:
            # We can do the move.
            word1, word2 = map(list, pair)
            leaf_index1, leaf_index2 = pair.leaf_indexes()

            li1b = leaf_index1[i+3]
            assert word1[li1b - 1 : li1b + 3] == list("(oo)")
            word1[li1b - 1: li1b + 3] = list("o")

            li1a = leaf_index1[i]
            assert word1[li1a-1:li1a+6] == list("(o(oo))")
            word1[li1a - 1:li1a + 6] = list("o")

            li2b = leaf_index2[i+2]
            assert word2[li2b - 2: li2b + 5] == list("((oo)o)")
            word2[li2b - 2: li2b + 5] = list("o")

            li2a = leaf_index2[i]
            assert word2[li2a - 1:li2a + 3] == list("(oo)")
            word2[li2a - 1:li2a + 3] = list("o")

            yield TreePair(''.join(word1), ''.join(word2))


@make_move_function(also_mirror=True)
def move_local_shufflebights(pair: TreePair):
    set1, set2 = pair.paren_pair_sets()
    n = pair.num_leaves()

    for i in range(n):
        top_required = {(i, i+2), (i, i+3)}
        if not top_required <= set1:
            continue

        j1s = [j for j in range(n + 1) if (j, i + 2) in set2]
        if len(j1s) != 1:
            continue
        [j1] = j1s
        if (j1, i+1) not in set2:
            continue
        j1s_1 = [j for j in range(n + 1) if (j, i + 1) in set2]
        if len(j1s_1) != 1:
            continue
        assert j1s == j1s_1

        j2s = [j for j in range(n+1) if (i+2, j) in set2]
        if len(j2s) != 1:
            continue
        [j2] = j2s

        assert (j1, j2) in set2

        word1, word2 = map(list, pair)
        leaf_index1, leaf_index2 = pair.leaf_indexes()

        li1 = leaf_index1[i]
        assert word1[li1-2:li1+5] == list("((oo)o)")
        word1[li1 - 2:li1 + 5] = list("(o(oo))")

        # (((?o)o)(o?)) --> ((?o)(o(o?)))
        li2 = leaf_index2[i]
        li_j2 = leaf_index2[j2-1]
        li_j1 = leaf_index2[j1]
        assert li_j1 < li2 < li_j2

        # Part 1: ?)) --> ?)))
        assert word2[li_j2:li_j2+3] == list("o))")
        word2[li_j2:li_j2 + 3] = list("o)))")

        # Part 2: o)o)(o --> o)(o(o
        try:
            assert word2[li2:li2+6] == list("o)o)(o")
        except AssertionError:
            breakpoint()
        word2[li2:li2 + 6] = list("o)(o(o")

        # Part 3: (((? --> ((?
        assert word2[li_j1-3:li_j1+1] == list("(((o")
        word2[li_j1 - 3:li_j1+1] = list("((o")

        yield TreePair(''.join(word1), ''.join(word2))



