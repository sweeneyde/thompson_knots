from link_classification import pairs_of_binary_words
from oriented import oriented_pairs, is_oriented, word_to_bipartition

def pair_is_oriented(pair):
    return is_oriented(*pair)

def iter_len(pair):
    return sum(1 for x in pair)

def test_found_all():
    for n in range(2, 7):
        expected = iter_len(pairs_of_binary_words(n, pair_is_oriented))
        actual = iter_len(oriented_pairs(n))
        assert actual == expected

def test_all_good():
    for n in range(2, 7):
        for pair in oriented_pairs(n):
            assert is_oriented(*pair)

def test_bipartition():
    assert word_to_bipartition('((oo)(oo))') == 'ABBA'
    assert word_to_bipartition('(o(o(((oo)(oo))o)))') == 'ABABBAB'