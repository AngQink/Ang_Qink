import gzip
import itertools
import json
from pathlib import Path
from types import SimpleNamespace

from generate import Trace,MODULI,random_trace,hub_pressure,line_pressure

CASES=[]


def case(name):
    def register(fn):
        CASES.append((name,fn))
        return fn
    return register


def inspect(t):
    n=len(t.commands[0]['weights'])
    for u in range(n):t.add('ask',u=u)
    for u in range(n):
        for v in range(n):
            for su,sv in itertools.product(range(2),repeat=2):
                t.add('pair',u=u,v=v,su=su,sv=sv)


@case('singletons_negative_and_same_vertex')
def singletons():
    t=Trace([0,-7,11],[],6)
    inspect(t)
    t.add('link',u=0,v=2);t.add('link',u=1,v=2)
    inspect(t)
    t.add('set',u=2,w=-2**63);t.add('set',u=1,w=2**63-1)
    inspect(t)
    return t


@case('zero_count_is_still_possible')
def zero_possible():
    t=Trace([0,0,0],[(0,1),(0,2)],4)
    inspect(t)
    for u in [2,1,0,1,2,0]*10:t.add('ask',u=u)
    t.add('cut',u=2,v=0);inspect(t)
    t.add('link',u=1,v=2);inspect(t)
    return t


@case('nonunit_products_recover_from_zero')
def nonunit():
    t=Trace([-1,0,0,0],[(0,1),(0,2),(2,3)],6)
    for _ in range(10):
        inspect(t)
        t.add('set',u=3,w=1);inspect(t)
        t.add('cut',u=0,v=2);inspect(t)
        t.add('set',u=3,w=0);t.add('link',u=2,v=0)
    return t


@case('score_beyond_signed64_and_float_precision')
def wide_weights():
    t=Trace([2**63-1,2**62-1,2**62-1,-2**63,-1],[(0,1),(0,2),(2,3),(3,4)],2147483647)
    inspect(t)
    for u in range(5):t.add('set',u=u,w=-2**63)
    inspect(t)
    for u in range(5):t.add('set',u=u,w=2**63-1)
    inspect(t)
    return t


@case('off_path_branches_count_for_pair')
def branches():
    t=Trace([4,1,4,100,0,0,0],[(0,1),(1,2),(1,3),(3,4),(3,5),(5,6)],12)
    inspect(t)
    for edge in [(1,3),(1,2),(5,6)]:
        t.add('cut',u=edge[1],v=edge[0]);inspect(t)
        t.add('link',u=edge[0],v=edge[1]);inspect(t)
    return t


@case('counts_change_while_optimum_weight_stays')
def count_only_changes():
    t=Trace([10,0,0,0,0,-10],[(0,1),(1,2),(1,3),(3,4),(0,5)],8)
    for i in range(40):
        t.add('set',u=2,w=0 if i%2 else -1)
        t.add('set',u=4,w=0 if i%3 else -1)
        for u in [0,4,2,5,1,3]:t.add('ask',u=u)
        t.add('pair',u=2,v=4,su=i%2,sv=(i//2)%2)
    return t


def all_forests(weights,modulus):
    n=len(weights);pairs=list(itertools.combinations(range(n),2))
    t=Trace(weights,[],modulus);old=set()
    for mask in range(1<<len(pairs)):
        edges=[edge for i,edge in enumerate(pairs) if mask>>i&1]
        parent=list(range(n))
        def root(u):
            while parent[u]!=u:u=parent[u]
            return u
        valid=True
        for u,v in edges:
            a,b=root(u),root(v)
            if a==b:valid=False;break
            parent[a]=b
        if not valid:continue
        current=set(edges)
        for u,v in sorted(old-current):t.add('cut',u=v,v=u)
        for u,v in sorted(current-old):t.add('link',u=u,v=v)
        inspect(t);old=current
    return t


case('every_five_vertex_forest_zero_mod6')(lambda:all_forests([0]*5,6))
case('every_five_vertex_forest_mixed_mod1000')(lambda:all_forests([-3,0,2,2,0],1000))


@case('all_small_weight_assignments')
def weights_cube():
    t=Trace([0]*5,[(i-1,i) for i in range(1,5)],12)
    for values in itertools.product([-1,0,1],repeat=5):
        for u,w in enumerate(values):t.add('set',u=u,w=w)
        for u in range(5):t.add('ask',u=u)
        t.add('pair',u=0,v=4,su=1,sv=1)
        t.add('pair',u=1,v=3,su=1,sv=1)
    return t


@case('zero_factor_subtree_repeatedly_moved')
def zero_subtree():
    # The eight-leaf zero-weight star has exactly 257 independent sets.
    edges=[(0,1)]+[(1,i) for i in range(2,10)]+[(0,10),(10,11)]
    t=Trace([-5]+[0]*11,edges,257)
    for i in range(60):
        for u in [0,1,7,10,11]:t.add('ask',u=u)
        t.add('cut',u=0,v=1)
        t.add('pair',u=7,v=10,su=1,sv=1)
        t.add('link',u=1,v=11)
        t.add('pair',u=0,v=7,su=i%2,sv=(i//2)%2)
        t.add('cut',u=11,v=1);t.add('link',u=1,v=0)
    return t


@case('high_degree_virtual_child_turnover')
def high_degree():
    n=320;t=Trace([-1]+[0]*(n-1),[(0,u) for u in range(1,n)],1024)
    for i in range(900):
        u=1+(i*137)%(n-1)
        t.add('ask',u=u)
        t.add('set',u=u,w=0 if i%3 else 1)
        t.add('pair',u=u,v=1+(u*73)%(n-1),su=i%2,sv=(i//2)%2)
    return t


@case('broom_and_path_orientation')
def broom():
    n=150;edges=[(u-1,u) for u in range(1,75)]+[(74,u) for u in range(75,n)]
    t=Trace([i%5-2 for i in range(n)],edges,360360)
    for i in range(350):
        u,v=(i*71)%n,(i*97+13)%n
        t.add('pair',u=u,v=v,su=i%2,sv=(i//3)%2)
        t.add('set',u=u,w=i%7-3)
        t.add('ask',u=v)
    return t


for mod in MODULI:
    def modulus_case(m=mod):
        n=96;t=Trace([0]*n,[(u-1,u) for u in range(1,n)],m)
        for i in range(120):
            u,v=(i*37)%n,(i*71+3)%n
            t.add('pair',u=u,v=v,su=i%2,sv=(i//2)%2)
            t.add('set',u=u,w=0 if i%3 else -1)
            t.add('ask',u=v)
        return t
    case(f'modulus_{mod}')(modulus_case)

for seed in [3,7,11,17,29,47,71,97,127,193,257,383,521,769,1017,1543,
             2026,3079,4093,6151,8191,12289,16381,24593,32749,49157,
             65537,98317,131071,196613,262139,393241,524287,786433,1048573,1572869]:
    case(f'independent_tree_dp_random_{seed}')(lambda seed=seed:random_trace(seed,n=80,steps=900))


case('pressure_hub_forest')(lambda:hub_pressure())
case('pressure_100000_zero_path')(lambda:line_pressure(n=100000,steps=500,modulus=72))
case('pressure_60000_positive_path')(lambda:line_pressure(n=60000,steps=1200,weight=1,modulus=1000))
case('pressure_30000_negative_path')(lambda:line_pressure(n=30000,steps=1400,weight=-1,modulus=360360))


def fixture(name):
    path=Path(__file__).parent/'fixtures'/(name+'.json.gz')
    data=json.loads(gzip.decompress(path.read_bytes()))
    assert len(data['commands'])<=60000
    return SimpleNamespace(**data)


case('pressure_scrambled_tree')(lambda:fixture('scrambled-tree'))
case('pressure_scrambled_tree_large')(lambda:fixture('scrambled-tree-large'))


@case('nine_prime_factors_and_cancellable_zero')
def many_factors():
    weights=[-1];edges=[];roots=[]
    for length in [1,2,3,6,7,16,22]:
        start=len(weights);roots.append(start)
        weights.extend([0]*length);edges.append((0,start))
        edges.extend((u-1,u) for u in range(start+1,start+length))
    for leaves in [5,6]:
        start=len(weights);roots.append(start)
        weights.extend([0]*(leaves+1));edges.append((0,start))
        edges.extend((start,u) for u in range(start+1,start+leaves+1))
    t=Trace(weights,edges,223092870)
    for i in range(80):
        for u in [0]+roots:t.add('ask',u=u)
        child=roots[i%len(roots)]
        t.add('cut',u=child,v=0)
        t.add('ask',u=0)
        t.add('pair',u=child,v=0,su=0,sv=1)
        t.add('set',u=child,w=(i%3)-1)
        t.add('link',u=0,v=child)
        t.add('pair',u=roots[(i+1)%len(roots)],v=child,su=i%2,sv=(i//2)%2)
    return t


@case('pressure_max_nodes_commands_and_factor_width')
def maximal_combination():
    import random
    from large_models import LineModel
    n=100000;mod=223092870;rng=random.Random(424242)
    t=Trace([0]*n,[(i-1,i) for i in range(1,n)],mod,LineModel(n,0,mod))
    for _ in range(59999):
        t.add('pair',u=rng.randrange(n),v=rng.randrange(n),su=rng.randrange(2),sv=rng.randrange(2))
    return t
