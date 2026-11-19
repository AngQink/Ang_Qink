import random
from models import TreeModel
from large_models import HubModel,LineModel


class Trace:
    def __init__(self,weights,edges,modulus,model=None):
        assert 1<=len(weights)<=100000 and 2<=modulus<=2147483647
        assert all(type(w) is int and -2**63<=w<2**63 for w in weights)
        self.commands=[dict(op='init',weights=weights,edges=[list(e) for e in edges],mod=modulus)]
        self.expected=[dict(ok=True)]
        self.model=model if model is not None else TreeModel(weights,edges,modulus)

    def add(self,op,**fields):
        n=len(self.commands[0]['weights'])
        assert 0<=fields['u']<n
        if op=='set':assert -2**63<=fields['w']<2**63
        if op in ('link','cut','pair'):assert 0<=fields['v']<n
        if op=='pair':assert fields['su'] in (0,1) and fields['sv'] in (0,1)
        cmd=dict(op=op,**fields)
        self.expected.append(self.model.execute(cmd))
        self.commands.append(cmd)
        assert len(self.commands)<=60000


WEIGHTS=[0,1,-1,2,-7,2**63-1,-2**63]
MODULI=[2,3,4,6,8,12,16,36,72,81,101,257,1000,1009,65536,360360,
        223092870,1073741824,1162261467,2147483646,2147483647]


def random_trace(seed,n=60,steps=650):
    rng=random.Random(seed)
    weights=[rng.choice(WEIGHTS) for _ in range(n)]
    edges=[(i,rng.randrange(i)) for i in range(1,n) if rng.random()<.75]
    t=Trace(weights,edges,rng.choice(MODULI))
    for _ in range(steps):
        u,v=rng.randrange(n),rng.randrange(n)
        k=rng.randrange(10)
        if k<3:
            t.add('set',u=u,w=rng.choice(WEIGHTS))
        elif k<5:
            if t.model.g[u] and rng.random()<.5:
                t.add('cut',u=u,v=rng.choice(sorted(t.model.g[u])))
            elif v not in t.model.component(u)[1]:
                t.add('link',u=u,v=v)
            else:
                t.add('ask',u=u)
        elif k<7:
            t.add('ask',u=u)
        else:
            t.add('pair',u=u,v=v,su=rng.randrange(2),sv=rng.randrange(2))
    return t


def hub_pressure(seed=1017,n=16000,hubs=32,steps=16000):
    rng=random.Random(seed)
    weights=[rng.randrange(-8,9) for _ in range(n)]
    for i in range(hubs,n):
        if i%3:
            weights[i]=0
    edges=[(i-1,i) for i in range(1,hubs)]+[(i,i%hubs) for i in range(hubs,n)]
    mod=360360
    model=HubModel(weights,edges,mod,hubs)
    t=Trace(weights,edges,mod,model)
    for i in range(steps):
        u=rng.randrange(hubs,n)
        if i%7==0:
            h=model.parent[u]
            t.add('cut',u=u,v=h)
            t.add('pair',u=u,v=rng.randrange(hubs),su=i&1,sv=(i>>1)&1)
            t.add('link',u=rng.randrange(hubs),v=u)
        elif i%7==1:
            t.add('set',u=rng.randrange(hubs),w=rng.choice(WEIGHTS))
        elif i%7 in (2,3):
            t.add('set',u=u,w=rng.choice(WEIGHTS))
        elif i%7==4:
            t.add('ask',u=u)
        else:
            t.add('pair',u=u,v=rng.randrange(n),su=rng.randrange(2),sv=rng.randrange(2))
    return t


def line_pressure(seed=271828,n=14000,steps=2400,weight=0,modulus=72):
    rng=random.Random(seed)
    edges=[(i-1,i) for i in range(1,n)]
    model=LineModel(n,weight,modulus)
    t=Trace([weight]*n,edges,modulus,model)
    for i in range(steps):
        edge=n//4+rng.randrange(n//2)
        t.add('cut',u=edge+1,v=edge)
        t.add('ask',u=rng.randrange(n))
        t.add('pair',u=0,v=n-1,su=i&1,sv=(i>>1)&1)
        a,b=sorted(rng.sample(range(edge+1),2))
        t.add('pair',u=a,v=b,su=i&1,sv=(i>>2)&1)
        t.add('link',u=edge,v=edge+1)
        a,b=sorted(rng.sample(range(n),2))
        t.add('pair',u=b,v=a,su=i&1,sv=(i>>1)&1)
        t.add('ask',u=rng.randrange(n))
    return t
