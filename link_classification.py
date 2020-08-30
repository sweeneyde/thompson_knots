import itertools
from functools import lru_cache
from thompson import words_to_gauss
from collections import defaultdict


@lru_cache(maxsize=None)
def binary_words(num_leaves):
    if num_leaves == 1:
        return ('o',)
    all_words = []
    for k1 in range(1, num_leaves):
        k2 = num_leaves - k1
        possible_lefts = binary_words(k1)
        possible_rights = binary_words(k2)
        possible_pairs = itertools.product(possible_lefts, possible_rights)
        all_words += [f"({left}{right})" for left, right in possible_pairs]
    return tuple(all_words)


def is_irreducible(pair):
    word1, word2 = pair

    def indices_of_carats(word):
        return {word.count("o", 0, i)
                for i in range(len(word))
                if word[i:i + 4] == "(oo)"}

    set1 = indices_of_carats(word1)
    set2 = indices_of_carats(word2)
    return set1.isdisjoint(set2)


@lru_cache(maxsize=1000)
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


def is_prime(pair):
    word1, word2 = pair
    n = word1.count("o")
    assert word2.count("o") == n
    set1 = set(paren_pair_indices(word1))
    set2 = set(paren_pair_indices(word2))
    default = (0, n)
    set1.remove(default)
    set2.remove(default)
    return set1.isdisjoint(set2)


reverse_map = {'(': ')', ')': '(', 'o': 'o'}

@lru_cache(maxsize=1000)
def reverse_word(word):
    """
    >>> reverse_word('((oo)o)')
    '(o(oo))'
    """
    return ''.join(reverse_map[c] for c in reversed(word))

@lru_cache(maxsize=1000)
def get_symmetries(pair):
    """
    >>> s, n = get_symmetries((')))', '()()()('))
    >>> s
    ((')))', '()()()('), ('()()()(', ')))'), ('(((', ')()()()'), (')()()()', '((('))
    """
    word1, word2 = pair
    n = word1.count("o")
    assert n == word2.count("o")

    symmetries = (
        (word1, word2),
        (word2, word1),
        (reverse_word(word1), reverse_word(word2)),
        (reverse_word(word2), reverse_word(word1))
    )

    return symmetries, n

def reached_through_move1(pair):
    """
    >>> reached_through_move1(("(((oo)o)((o(oo))o))", "(o((o(o(oo)))(oo)))"))
    True
    >>> reached_through_move1(("(((oo)o)((oo)o))", "(o((o(oo))(oo)))"))
    False
    """
    symmetries, n = get_symmetries(pair)

    for a, b in symmetries:
        top_set = paren_pair_indices(a)
        bottom_set = paren_pair_indices(b)
        for i in range(n):
            top_required = {(i, i + 3), (i + 1, i + 3), (i, i + 4)}
            bottom_required = {(i, i + 2), (i + 2, i + 4)}
            if top_required <= top_set and bottom_required <= bottom_set:
                return True
    return False

def reached_through_move2(pair):
    """
    Move2 moves a slat from top to bottom.
    >>> reached_through_move2(("((oo)o)", "(o(oo))"))
    True
    >>> reached_through_move2(("(o(oo))", "((oo)o)"))
    True
    >>> reached_through_move2(("(o(((oo)o)((oo)o)))", "((oo)((o(oo))(oo)))")) # slat is on top
    False
    >>> reached_through_move2(("((((oo)o)o)((oo)o))", "(o(o((o(oo))(oo))))")) # slat is on bottom
    True
    """
    symmetries, n = get_symmetries(pair)

    for a, b in [symmetries[0], symmetries[2]]:
        top_set = paren_pair_indices(a)
        bottom_set = paren_pair_indices(b)
        if ((0, 2) in top_set and (1, n) in bottom_set):
            return True
    return False

@lru_cache(maxsize=1000)
def _move3_locations(word):
    result = set()
    for i in range(len(word)):
        if word[i:].startswith('(o(o'):
            result.add(word[:i].count('o'))
    return frozenset(result)


def reached_through_move3(pair):
    """
    >>> reached_through_move3(('((((oo)o)o)o)', '(o(((oo)o)o))'))
    True
    >>> reached_through_move3(('(((oo)o)o)', '(o((oo)o))'))
    True
    >>> reached_through_move3(('((oo)o)', '(o(oo))'))
    False
    """
    symmetries, n = get_symmetries(pair)
    for a, b in symmetries:
        set1 = _move3_locations(a)
        set2 = _move3_locations(b)
        if (set1 & set2):
            return True
    return False

    # tree1, tree2, label_to_vertex = construct_trees(*pair)
    # for v in label_to_vertex.values():
    #     assert not v.is_leaf()
    #     cor = v.corresponding
    #     if (v.left.corresponding is cor.left
    #         and v.right.corresponding is cor.right
    #     ):
    #         return True
    # return False

def reached_through_move4(pair):
    """
    >>> reached_through_move4(("(o(o(oo)))", "((o(oo))o)"))
    True
    """
    symmetries, n = get_symmetries(pair)
    for a, b in symmetries:
        for i in range(n):
            top_set = paren_pair_indices(a)
            bottom_set = paren_pair_indices(b)
            top_pairs = {(i+2, i+4), (i+1, i+4)}
            bottom_pairs = {(i+1, i+3), (i, i+3), (i, i+4)}
            if top_pairs <= top_set and bottom_pairs <= bottom_set:
                return True
    return False

def is_first_of_flip(pair):
    symmetries, n = get_symmetries(pair)
    rev = symmetries[-1]
    return pair <= rev


def very_filtered(pair):
    return (
        is_prime(pair)
        and is_first_of_flip(pair)
        and not reached_through_move1(pair)
        and not reached_through_move2(pair)
        and not reached_through_move3(pair)
        and not reached_through_move4(pair)
    )

def pairs_of_binary_words(leaves, filterfunc=None):
    pairs = itertools.product(binary_words(leaves), repeat=2)
    return filter(filterfunc, pairs)


def words_to_link(word1, word2=None):
    from sage.knots.all import Link
    if word2 is None:
        word1, word2 = word1.split(" / ")
    return Link(words_to_gauss(word1, word2))


def main(n):
    key_to_pairs = defaultdict(list)
    from oriented import oriented_pairs as pairs_of_binary_words
    from time import time
    for i in range(2, n + 1):
        print(f"======== {i} =========" )
        t0 = time()
        for j, (top, bottom) in enumerate(pairs_of_binary_words(i, filterfunc=is_irreducible)):
            L = words_to_link(top, bottom)
            key = (L.number_of_components(), L.homfly_polynomial())
            key_to_pairs[key].append((top, bottom))
            if j % 1000 == 0:
                print(round(time() - t0, 1), j // 100)
    def sort_key(item):
        (comp, homfly), strings = item
        return (comp, len(strings))
    return dict(sorted(key_to_pairs.items(), key=sort_key))


# if __name__ == '__main__':
#     import doctest
#
#     doctest.testmod()

if __name__ == '__main__':

    print([len(list(pairs_of_binary_words(i, is_prime)))
           for i in range(2, 7)])

    for i in range(3, 20):
        x = len(list(pairs_of_binary_words(i, filterfunc=None)))
        y = len(list(pairs_of_binary_words(i, filterfunc=is_prime)))
        print(i, y, x, y/x, sep='\t')


    # for filterfunc in [None, is_irreducible, is_prime, very_filtered]:
    #     nums = [len(list(pairs_of_binary_words(N, filterfunc=filterfunc)))
    #             for N in range(2, 10)]
    #     print(filterfunc, nums)


