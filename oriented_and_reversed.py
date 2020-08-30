

with open("oriented11.txt") as f:
    pairs = {tuple(line.strip().split(' / '))
             for line in f if ' / ' in line}



from link_classification import reverse_word

def doubly_oriented():
    for a, b in pairs:
        aa, bb = reverse_word(a), reverse_word(b)
        if (aa, bb) in pairs:
            yield ' / '.join([a, b])

pairs = sorted(doubly_oriented(), key=lambda x: (len(x), x) )
for pair in pairs:
    print(pair)
# print(pairs)