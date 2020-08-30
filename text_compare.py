from difflib import SequenceMatcher


def ratio(a, b):
    if a == b:
        return 0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()

if __name__ == '__main__':


    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    d = {(a, b): ratio(a, b) for a in lines for b in lines}
    arr = sorted(d.items(), key=lambda x: x[1], reverse=True)

    from pprint import pprint
    pprint(arr[:20])


# [(('((o(o(((oo)o)o)))o) / ((o((oo)o))(o(oo)))', '((o(o(o((oo)o))))o) / ((o((oo)o))(o(oo)))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / (o((oo)(o(o(oo)))))', '((o((o((oo)o))o))o) / (o((oo)((o(oo))o)))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / (o((oo)((o(oo))o)))', '((o((o((oo)o))o))o) / (o((oo)(o(o(oo)))))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / ((oo)(o((oo)(oo))))', '((((o((oo)o))o)o)o) / ((oo)(o((oo)(oo))))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / ((o(oo))(o((oo)o)))', '((o((o((oo)o))o))o) / (((oo)o)(o((oo)o)))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / (((oo)o)(o((oo)o)))', '((o((o((oo)o))o))o) / ((o(oo))(o((oo)o)))'), 0.975609756097561),
#  (('((o((o((oo)o))o))o) / ((o((oo)o))(o(oo)))', '((o(o(o((oo)o))))o) / ((o((oo)o))(o(oo)))'), 0.975609756097561),
#  (('(((o((oo)o))(oo))o) / (o((o((o(oo))o))o))', '(((((oo)o)o)(oo))o) / (o((o((o(oo))o))o))'), 0.975609756097561),
#  (('(((((oo)o)o)(oo))o) / (o((o((o(oo))o))o))', '(((o((oo)o))(oo))o) / (o((o((o(oo))o))o))'), 0.975609756097561),
#  (('((((o((oo)o))o)o)o) / ((oo)(o((oo)(oo))))', '((o((o((oo)o))o))o) / ((oo)(o((oo)(oo))))'), 0.975609756097561)]


# '(o(((oo)o)((oo)o))) / (((oo)(o((oo)o)))o)', '(o(((oo)o)((oo)o))) / (((oo)((o(oo))o))o)'
