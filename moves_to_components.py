from moves import TreePair, all_move_functions
from collections import defaultdict


with open("trefoil_trees8.txt") as f:
    data = f.read()

f = open("trefoil_component8.txt", 'w')

nodes = [TreePair(line) for line in data.splitlines()]

connections = defaultdict(list)

for node in nodes:
    assert isinstance(node, TreePair)
    for func in all_move_functions:
        for neighbor in func(node):
            assert isinstance(neighbor, TreePair), func
            connections[node].append(
                (func.__name__, neighbor)
            )
            connections[neighbor].append(
                ("inverse " + func.__name__, node)
            )

assert set(nodes) == set(connections.keys())

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

for arr in components:
    for pair in arr:
        print(pair, file=f)
    print("\n" + "-"*50 + "\n", file=f)
# for arr in label_to_list.values():
#     pprint(arr)
#     print()

lengths = sorted(len(arr) for arr in label_to_list.values())
print(lengths, f"sum={sum(lengths)}")



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
