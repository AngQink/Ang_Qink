"""Fixture builders use the independent models, never the private rope."""
import random
from models import ListModel, PieceModel, P


class Trace:
    def __init__(self, model):
        self.model = model
        self.commands, self.expected = [], []
        self.literal_count = 0

    def add(self, op, **fields):
        cmd = dict(op=op, **fields)
        if op == 'new':
            assert len(fields['values']) <= 4096
            assert all(type(v) is int and -2**63 <= v < 2**63 for v in fields['values'])
            self.literal_count += len(fields['values'])
            assert self.literal_count <= 100000
        elif op == 'concat':
            assert self.length(fields['left']) + self.length(fields['right']) <= 2**60
        else:
            n = self.length(fields['v'])
            if op in ('edit', 'reverse', 'slice', 'query', 'splice'):
                assert 0 <= fields['l'] <= fields['r'] <= n
            if op == 'edit':
                assert all(-2**63 <= fields[k] < 2**63 for k in ('a', 'b', 'c'))
            if op == 'splice':
                sn = self.length(fields['src'])
                assert 0 <= fields['sl'] <= fields['sr'] <= sn
                assert n-fields['r']+fields['l']+fields['sr']-fields['sl'] <= 2**60
            if op == 'at':
                assert 0 <= fields['i'] < n
            if op == 'repeat':
                assert 0 <= fields['times'] <= 2**60 and n*fields['times'] <= 2**60
            if op == 'drop':
                assert fields['v'] != 0
        result = self.model.execute(cmd)
        assert len(self.model.roots) <= 12000
        if 'n' in result:
            assert result['n'] <= 2**60
        self.commands.append(cmd)
        self.expected.append(result)
        assert len(self.commands) <= 60000
        return result.get('v')

    def length(self, v):
        if isinstance(self.model, ListModel):
            return len(self.model.roots[v])
        return self.model.length(v)


COEFFICIENTS = [0, 1, -1, 2, -7, P, P+1, -P-1, 2**63-1, -2**63]


def random_trace(seed, steps=600):
    rng = random.Random(seed)
    t = Trace(ListModel())
    t.add('new', values=[rng.randrange(-P, P) for _ in range(23)])
    for _ in range(steps):
        active = list(t.model.roots)
        v = rng.choice(active)
        n = t.length(v)
        l, r = sorted([rng.randrange(n+1), rng.randrange(n+1)])
        op = rng.choice(['edit']*3 + ['reverse']*2 + ['query']*3 + ['slice', 'splice', 'concat', 'repeat', 'new', 'at', 'drop'])
        if len(active) > 75 and op not in ('query', 'at'):
            op = 'drop'
        if op == 'new':
            t.add(op, values=[rng.choice(COEFFICIENTS) for _ in range(rng.randrange(25))])
        elif op == 'drop':
            if v:
                t.add(op, v=v)
        elif op in ('query', 'reverse', 'slice'):
            t.add(op, v=v, l=l, r=r)
        elif op == 'edit':
            t.add(op, v=v, l=l, r=r, a=rng.choice(COEFFICIENTS),
                  b=rng.choice(COEFFICIENTS), c=rng.choice(COEFFICIENTS))
        elif op == 'at':
            if n:
                t.add(op, v=v, i=rng.randrange(n))
        elif op == 'repeat':
            times = rng.randrange(5)
            if n*times <= 3000:
                t.add(op, v=v, times=times)
        elif op == 'concat':
            other = rng.choice(active)
            if n+t.length(other) <= 3000:
                t.add(op, left=v, right=other)
        else:
            src = rng.choice(active)
            sn = t.length(src)
            sl, sr = sorted([rng.randrange(sn+1), rng.randrange(sn+1)])
            if n-(r-l)+(sr-sl) <= 3000:
                t.add(op, v=v, l=l, r=r, src=src, sl=sl, sr=sr)
    for v in list(t.model.roots):
        n = t.length(v)
        t.add('query', v=v, l=0, r=n)
    return t


def giant_trace(seed=1017, steps=650):
    rng = random.Random(seed)
    t = Trace(PieceModel())
    base = t.add('new', values=[3, -5, 8, 13, 21, 0, -1])
    root = t.add('repeat', v=base, times=2**46)
    archived = []
    for step in range(steps):
        n = t.length(root)
        positions = [0, 1, n//2, n-1, n]
        if step % 3 == 0:
            l = rng.choice(positions)
            r = min(n, l+rng.randrange(0, 1000))
            new = t.add('edit', v=root, l=l, r=r, a=rng.choice(COEFFICIENTS),
                        b=rng.choice(COEFFICIENTS), c=rng.choice(COEFFICIENTS))
        elif step % 3 == 1:
            l, r = sorted(rng.sample(positions, 2))
            new = t.add('reverse', v=root, l=l, r=r)
        else:
            src = root if not archived or step % 2 else rng.choice(archived)
            sn = t.length(src)
            sl = rng.randrange(sn)
            sr = min(sn, sl+rng.randrange(1, 24))
            l = rng.randrange(n)
            r = min(n, l+rng.randrange(24))
            new = t.add('splice', v=root, l=l, r=r, src=src, sl=sl, sr=sr)
        if step % 20 == 0:
            archived.append(root)
        else:
            t.add('drop', v=root)
        root = new
        for i in [0, t.length(root)//2, t.length(root)-1]:
            t.add('at', v=root, i=i)
        if step % 45 == 0:
            t.add('query', v=root, l=0, r=t.length(root))
    for v in archived+[root]:
        n = t.length(v)
        t.add('query', v=v, l=max(0, n//2-19), r=min(n, n//2+21))
    t.add('query', v=root, l=0, r=t.length(root))
    return t
