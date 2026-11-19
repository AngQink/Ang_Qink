"""Independent exact-count, linear-time tree DP and subset enumeration models."""


def best(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a[0] > b[0]:
        return a
    if b[0] > a[0]:
        return b
    return a[0], a[1]+b[1]


class TreeModel:
    def __init__(self, weights, edges, modulus):
        self.w = weights[:]
        self.g = [set() for _ in weights]
        self.mod = modulus
        for u, v in edges:
            self.g[u].add(v)
            self.g[v].add(u)

    def component(self, start):
        order, parents = [start], {start: None}
        for u in order:
            for v in self.g[u]:
                if v != parents[u]:
                    assert v not in parents, 'fixture introduced a cycle'
                    parents[v] = u
                    order.append(v)
        return order, parents

    def _dp(self, start, pins):
        order, parents = self.component(start)
        values = {}
        for u in reversed(order):
            a, b = (0, 1), (self.w[u], 1)
            if pins.get(u) == 0:
                b = None
            elif pins.get(u) == 1:
                a = None
            for v in self.g[u]:
                if parents[u] == v:
                    continue
                x, y = values[v]
                z = best(x, y)
                a = None if a is None or z is None else (a[0]+z[0], a[1]*z[1])
                b = None if b is None or x is None else (b[0]+x[0], b[1]*x[1])
            values[u] = a, b
        return values[start], len(order)

    def execute(self, cmd):
        op = cmd['op']
        u = cmd['u']
        if op == 'set':
            self.w[u] = cmd['w']
        elif op == 'link':
            v = cmd['v']
            assert v not in self.component(u)[1] and u != v
            self.g[u].add(v)
            self.g[v].add(u)
        elif op == 'cut':
            v = cmd['v']
            assert v in self.g[u]
            self.g[u].remove(v)
            self.g[v].remove(u)
        elif op == 'ask':
            (a, b), count = self._dp(u, {})
            z = best(a, b)
            pack = lambda value: dict(weight=value[0], ways=value[1] % self.mod)
            return {'n': count, 'best': pack(z), 'out': pack(a), 'in': pack(b)}
        elif op == 'pair':
            v = cmd['v']
            if v not in self.component(u)[1]:
                return dict(connected=False)
            if u == v and cmd['su'] != cmd['sv']:
                return dict(connected=True, possible=False)
            (a, b), _ = self._dp(u, {u: cmd['su'], v: cmd['sv']})
            z = best(a, b)
            if z is None:
                return dict(connected=True, possible=False)
            return dict(connected=True, possible=True, weight=z[0], ways=z[1] % self.mod)
        else:
            raise ValueError(op)
        return dict(ok=True)

    def enumerate_query(self, cmd):
        u = cmd['u']
        order, members = self.component(u)
        index = {v:i for i,v in enumerate(order)}
        pins = {}
        if cmd['op'] == 'pair':
            v = cmd['v']
            if v not in members:
                return dict(connected=False)
            if u == v and cmd['su'] != cmd['sv']:
                return dict(connected=True, possible=False)
            pins = {u:cmd['su'], v:cmd['sv']}
        answers = [None, None]
        edges = [(index[v], index[w]) for v in order for w in self.g[v] if v < w]
        for mask in range(1 << len(order)):
            if any(((mask>>index[v]) & 1) != state for v,state in pins.items()):
                continue
            if any((mask>>a)&1 and (mask>>b)&1 for a,b in edges):
                continue
            score = sum(self.w[v] for v in order if (mask>>index[v]) & 1)
            state = (mask>>index[u]) & 1
            answers[state] = best(answers[state], (score, 1))
        if cmd['op'] == 'ask':
            a, b = answers
            z = best(a, b)
            pack = lambda value: dict(weight=value[0], ways=value[1] % self.mod)
            return {'n':len(order), 'best':pack(z), 'out':pack(a), 'in':pack(b)}
        z = best(*answers)
        if z is None:
            return dict(connected=True, possible=False)
        return dict(connected=True, possible=True, weight=z[0], ways=z[1] % self.mod)
