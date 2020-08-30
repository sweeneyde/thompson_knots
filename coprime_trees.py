from functools import lru_cache
from math import comb as binom


def catalan(n):
    return binom(n + n, n) // (n + 1)


@lru_cache(maxsize=None)
def total_treepairs(n):
    return catalan(n - 1) ** 2


@lru_cache(maxsize=None)
def valid_partitions(n, maxlen=None):
    if maxlen is None:
        maxlen = n - 1

    if maxlen < 0:
        return ()
    if n == 0:
        return ((),)
    if maxlen < 1:
        return ()
    if n == 1:
        return ()
    if n == 2:
        return ((2,),)

    result = []
    for first in range(n + 1):
        for rest in valid_partitions(n - first, maxlen - 1):
            p = (first,) + rest
            if n > len(p):
                result.append(p)
    return result


# @lru_cache(maxsize=None)
# def ordered_partitions(n):
#     if n == 0:
#         return ((),)
#     result = []
#     for first in range(1, n + 1):
#         for rest in ordered_partitions(n - first):

#
# def nontrivial_ordered_partitions(n):
#     # exclude (n,)
#     return ordered_partitions(n)[:-1]

@lru_cache(maxsize=None)
def g0(N):
    if N == 1:
        return 0
    if N == 2:
        return 1
    partitions = valid_partitions(N)
    others = sum(g(*p)
                 for p in partitions
                 if len(p) >= 2)
    return total_treepairs(N) - others


@lru_cache(maxsize=1_000_000)
def g(*squaredepths):
    try:
        *rest, M, N = squaredepths
    except ValueError:
        (N,) = squaredepths
        return g0(N)

    s = 0
    for q in range(2, N + 1):
        existing_deepest = N - q
        if existing_deepest:
            prev_states = g(*rest, M + 1, existing_deepest)
        else:
            prev_states = g(*rest, M + 1)
        if not prev_states:
            continue

        locations_to_insert = M + 1
        treepairs_to_insert = g0(q)
        leaves_to_distinguish = q
        s += (prev_states
              * locations_to_insert
              * treepairs_to_insert
              * leaves_to_distinguish)

    assert s % N == 0
    return s // N


if __name__ == "__main__":
    assert g(1, 2) == 2
    assert g(0, 3) == 0

    for i in range(2, 20):
        # print(i, g0(i))
        print(i, len(valid_partitions(i)))
