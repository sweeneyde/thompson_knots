from moves import TreePair, all_move_functions
from collections import defaultdict, Counter
from tqdm import tqdm


with open("unlink_trees9.txt") as f:
    data = f.read()

OUTFILE = "unlink_components9.txt"

# f = open(OUTFILE, 'w')

nodes = [TreePair(line) for line in data.splitlines()]
set_nodes = set(nodes)

connections = defaultdict(list)

for node in tqdm(nodes):
    assert isinstance(node, TreePair)
    for func in all_move_functions:
        for neighbor in func(node):
            assert isinstance(neighbor, TreePair), func
            if neighbor not in set_nodes:
                breakpoint()
            connections[node].append(
                (func.__name__, neighbor)
            )
            connections[neighbor].append(
                ("inverse " + func.__name__, node)
            )

# expected = set(nodes)
actual = set(connections.keys())
assert set_nodes == actual, (set_nodes-actual, actual-set_nodes)
# assert set(nodes) == set(connections.keys()), (set(nodes) - set(connections.keys()))

from pprint import pprint
# print("===== connections =====")
# pprint(dict(connections))


label_to_list = defaultdict(list)
seen = dict()

for i, node in enumerate(nodes):
    stack = [node]
    while stack:
        node = stack.pop()
        if node not in seen:
            label_to_list[i].append(node)
            seen[node] = i
            stack += [pair for move, pair in connections[node]]

components = sorted(label_to_list.values(), key=len)

with open(OUTFILE, 'w') as f:
    for arr in components:
        for pair in arr:
            print(pair, file=f)
        print("\n" + "-"*50 + "\n", file=f)
# for arr in label_to_list.values():
#     pprint(arr)
#     print()

lengths = sorted(len(arr) for arr in label_to_list.values())
print(lengths)
print(Counter(lengths))
print(f"sum={sum(lengths)}")


for n in range(3, 100):

    lengths = (sum(t.num_leaves() == n for t in arr)
               for arr in label_to_list.values())
    lengths = sorted(filter(None, lengths))
    if sum(lengths) == 0:
        break
    print(n)
    print(lengths)
    print()



from itertools import combinations, product
from text_compare import ratio

results = []

for a, b in combinations(components, 2):
    for x, y in product(a, b):
        x, y = str(x), str(y)
        r = ratio(x, y) + ratio(y, x)
        if r > 1.9:
            # print('.', end='')
            print(r, x, y)

print()

results.sort()
pprint(results)
