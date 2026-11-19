from generate import Trace, random_trace, giant_trace, COEFFICIENTS
from models import ListModel, PieceModel, P

CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


@case('empty_versions_and_monotone_ids')
def empty():
    t = Trace(ListModel())
    a = t.add('new', values=[])
    b = t.add('repeat', v=a, times=2**60)
    c = t.add('concat', left=a, right=b)
    d = t.add('edit', v=c, l=0, r=0, a=-1, b=4, c=999)
    e = t.add('reverse', v=d, l=0, r=0)
    t.add('drop', v=d)
    f = t.add('slice', v=e, l=0, r=0)
    t.add('splice', v=f, l=0, r=0, src=0, sl=0, sr=0)
    for v in list(t.model.roots):
        t.add('query', v=v, l=0, r=0)
    return t


@case('rank_locality_reverse_and_old_versions')
def rank_locality():
    t = Trace(ListModel())
    a = t.add('new', values=[2, 5, 7, 11, 13, 17, 19, 23])
    b = t.add('edit', v=a, l=1, r=7, a=2, b=3, c=4)
    c = t.add('reverse', v=b, l=0, r=8)
    d = t.add('edit', v=c, l=0, r=8, a=-3, b=-5, c=-7)
    e = t.add('reverse', v=d, l=1, r=7)
    for v in [a, b, c, d, e]:
        for l in range(9):
            for r in range(l, 9):
                t.add('query', v=v, l=l, r=r)
    return t


@case('self_aliasing_splice_and_shared_drops')
def self_alias():
    t = Trace(ListModel())
    root = t.add('new', values=list(range(17)))
    originals = [root]
    for i in range(8):
        new = t.add('concat', left=root, right=root)
        root = t.add('edit', v=new, l=i, r=t.length(new)-i, a=-i, b=7, c=i+1)
        t.add('drop', v=new)
        originals.append(root)
    n = t.length(root)
    new = t.add('splice', v=root, l=13, r=n-17, src=root, sl=11, sr=n-19)
    t.add('drop', v=root)
    for v in originals[:-1]+[new]:
        t.add('query', v=v, l=0, r=t.length(v))
    return t


@case('composed_tags_and_zero_multiplier')
def tag_composition():
    t = Trace(ListModel())
    root = t.add('new', values=list(range(-37, 38)))
    for a in COEFFICIENTS:
        root = t.add('edit', v=root, l=0, r=75, a=a, b=-11, c=23)
        root = t.add('reverse', v=root, l=0, r=75)
        root = t.add('edit', v=root, l=1, r=74, a=2, b=P-1, c=-3)
        t.add('query', v=root, l=0, r=75)
        t.add('query', v=root, l=7, r=68)
    return t


@case('non_power_of_two_shapes')
def awkward_shapes():
    t = Trace(ListModel())
    for size in [1, 2, 3, 7, 15, 17, 31, 33, 127, 129, 255, 257, 1023, 1025, 4095, 4096]:
        root = t.add('new', values=[i*i-17 for i in range(size)])
        twin = t.add('concat', left=root, right=root)
        cut = t.add('slice', v=twin, l=size//2, r=size+size//2)
        rev = t.add('reverse', v=cut, l=0, r=size)
        edited = t.add('edit', v=rev, l=0, r=size, a=-1, b=2**63-1, c=-2**63)
        for v in [root, twin, cut, rev, edited]:
            t.add('query', v=v, l=0, r=t.length(v))
        for v in [root, twin, cut, rev, edited]:
            t.add('drop', v=v)
    return t


def giant_boundary(length):
    t = Trace(PieceModel())
    seed = t.add('new', values=[7])
    root = t.add('repeat', v=seed, times=length)
    edited = t.add('edit', v=root, l=0, r=length, a=-3, b=2**63-1, c=-2**63)
    reversed_v = t.add('reverse', v=edited, l=0, r=length)
    pasted = t.add('splice', v=reversed_v, l=1, r=3, src=reversed_v, sl=length-3, sr=length-1)
    for v in [root, edited, reversed_v, pasted]:
        t.add('query', v=v, l=0, r=length)
        t.add('query', v=v, l=length//2, r=length//2)
        t.add('query', v=v, l=length//2-1, r=length//2+3)
        for i in [0, 1, length//2, length-1]:
            t.add('at', v=v, i=i)
    return t


for length in [P-2, P-1, P, P+1, P*(P-1), 2**53+17, 2**60]:
    case(f'huge_length_{length}')(lambda n=length: giant_boundary(n))

for seed in [1017, 2026, 314159, 65537]:
    case(f'giant_fragmented_seed_{seed}')(lambda seed=seed: giant_trace(seed, 650))

for seed in [3, 7, 11, 17, 29, 47, 71, 97, 127, 193, 257, 383, 521, 769, 1017, 1543,
             2026, 3079, 4093, 6151, 8191, 12289, 16381, 24593, 32749, 49157, 65537,
             98317, 131071, 196613, 262139, 393241, 524287, 786433, 1048573, 1572869]:
    case(f'array_model_random_{seed}')(lambda seed=seed: random_trace(seed, 900))


@case('pressure_6000_live_giant_forks')
def fork_storm():
    t = Trace(PieceModel())
    seed = t.add('new', values=[i*i-37 for i in range(16)])
    base = t.add('repeat', v=seed, times=2**36)
    n = t.length(base)
    forks = []
    for i in range(6000):
        l = (i*999983) % (n-257)
        v = t.add('edit', v=base, l=l, r=l+257, a=i-3000, b=-i, c=2*i+1)
        forks.append((v, l))
        t.add('at', v=v, i=l+131)
        t.add('at', v=base, i=l+131)
        if i % 97 == 0:
            t.add('query', v=v, l=0, r=n)
    for v, l in reversed(forks):
        t.add('query', v=v, l=l+117, r=l+133)
    return t


@case('pressure_dropped_giant_versions')
def drop_churn():
    t = Trace(PieceModel())
    seed = t.add('new', values=[1, 2, 3, 5, 8, 13, 21, 34])
    base = t.add('repeat', v=seed, times=2**56)
    n = t.length(base)
    for i in range(22000):
        l = (i*1000003) % (n//3)
        r = n//2 + i*101
        v = t.add('edit', v=base, l=l, r=r, a=i-11000, b=7*i, c=-31*i-1)
        if i % 31 == 0:
            t.add('at', v=v, i=l+19)
        if i % 503 == 0:
            t.add('query', v=v, l=0, r=n)
        t.add('drop', v=v)
    t.add('query', v=base, l=0, r=n)
    return t


@case('pressure_deep_history_both_ends')
def deep_history():
    t = Trace(ListModel())
    root = 0
    archived = []
    for i in range(12000):
        v = t.add('new', values=[i*7-17])
        new = t.add('concat', left=root if i % 2 else v, right=v if i % 2 else root)
        t.add('drop', v=v)
        if root:
            if i % 97 == 0:
                archived.append(root)
            else:
                t.add('drop', v=root)
        root = new
        if i % 13 == 0:
            n = t.length(root)
            t.add('at', v=root, i=n//2)
            t.add('query', v=root, l=max(0, n//2-5), r=min(n, n//2+7))
    for v in archived+[root]:
        t.add('query', v=v, l=0, r=t.length(v))
    return t


@case('pressure_fragmented_huge_edits')
def fragmentation():
    return giant_trace(999983, 2500)
