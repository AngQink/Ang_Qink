"""Private oracle: dynamic tree boundary DP with cancellable composite products."""
import gc
import json
import sys

NEG = -(1 << 200)


class Forest:
    def __init__(self, weights, edges, modulus):
        self.mod = modulus
        self.w = [0] + weights[:]
        n = len(weights)
        self.l = [0]*(n+1)
        self.r = [0]*(n+1)
        self.p = [0]*(n+1)
        self.rev = bytearray(n+1)
        self.f = [None]*(n+1)
        self.b = [None]*(n+1)
        self.size = [0]+[1]*n
        self.virtual_size = [0]*(n+1)
        self.score0 = [0]*(n+1)
        self.score1 = [0]*(n+1)
        self.count0 = [1]*(n+1)
        self.count1 = [1]*(n+1)
        factors = []
        remaining = modulus
        d = 2
        while d*d <= remaining:
            if remaining % d == 0:
                factors.append(d)
                while remaining % d == 0:
                    remaining //= d
            d = 3 if d == 2 else d+2
        if remaining > 1:
            factors.append(remaining)
        self.primes = factors
        self.prod0 = [[1, 0]+[0]*len(factors) for _ in range(n+1)]
        self.prod1 = [[1, 0]+[0]*len(factors) for _ in range(n+1)]

        adjacent = [[] for _ in range(n+1)]
        for u, v in edges:
            u, v = u+1, v+1
            adjacent[u].append(v)
            adjacent[v].append(u)
        order, seen = [], bytearray(n+1)
        for start in range(1, n+1):
            if seen[start]:
                continue
            seen[start] = 1
            stack = [start]
            while stack:
                u = stack.pop()
                order.append(u)
                for v in adjacent[u]:
                    if v != self.p[u]:
                        self.p[v] = u
                        seen[v] = 1
                        stack.append(v)
        for u in reversed(order):
            self._pull(u)
            if self.p[u]:
                self._virtual(self.p[u], u, 1)
        self.edges = n-len([u for u in range(1, n+1) if self.p[u] == 0])

    def _best(self, a, ca, b, cb):
        if a > b:
            return a, ca
        if b > a:
            return b, cb
        return a, (ca+cb) % self.mod

    def _join(self, x, y):
        if x is None:
            return y
        if y is None:
            return x
        # First multiply by the symmetric independent-set edge constraint.
        a0, ac0 = self._best(x[0], x[1], x[2], x[3])
        a1, ac1 = x[0], x[1]
        a2, ac2 = self._best(x[4], x[5], x[6], x[7])
        a3, ac3 = x[4], x[5]
        result = []
        mod = self.mod
        for aa, ca, ab, cb in [(a0, ac0, a1, ac1), (a2, ac2, a3, ac3)]:
            for col in (0, 2):
                s0 = NEG if aa == NEG or y[col] == NEG else aa+y[col]
                s1 = NEG if ab == NEG or y[col+4] == NEG else ab+y[col+4]
                if s0 > s1:
                    result.extend((s0, ca*y[col+1] % mod))
                elif s1 > s0:
                    result.extend((s1, cb*y[col+5] % mod))
                elif s0 == NEG:
                    result.extend((NEG, 0))
                else:
                    result.extend((s0, (ca*y[col+1]+cb*y[col+5]) % mod))
        return tuple(result)

    def _pull(self, x):
        l, r = self.l[x], self.r[x]
        own = (self.score0[x], self.count0[x], NEG, 0,
               NEG, 0, self.w[x]+self.score1[x], self.count1[x])
        self.f[x] = self._join(self._join(self.f[l], own), self.f[r])
        f = self.f[x]
        self.b[x] = (f[0], f[1], f[4], f[5], f[2], f[3], f[6], f[7])
        self.size[x] = self.size[l]+self.size[r]+self.virtual_size[x]+1

    def _product(self, state, value, direction):
        mod = self.mod
        if value == 0:
            state[1] += direction
        else:
            for i, prime in enumerate(self.primes, 2):
                exponent = 0
                while value % prime == 0:
                    value //= prime
                    exponent += 1
                state[i] += direction*exponent
            if direction == 1:
                state[0] = state[0]*value % mod
            else:
                state[0] = state[0]*pow(value, -1, mod) % mod
        if state[1]:
            return 0
        result = state[0]
        for prime, exponent in zip(self.primes, state[2:]):
            result = result*pow(prime, exponent, mod) % mod
        return result

    def _dp(self, x):
        f = self.f[x]
        a, ca = self._best(f[0], f[1], f[2], f[3])
        b, cb = self._best(f[4], f[5], f[6], f[7])
        return a, ca, b, cb

    def _virtual(self, parent, child, direction):
        a, ca, b, cb = self._dp(child)
        best, ways = self._best(a, ca, b, cb)
        self.score0[parent] += direction*best
        self.score1[parent] += direction*a
        self.count0[parent] = self._product(self.prod0[parent], ways, direction)
        self.count1[parent] = self._product(self.prod1[parent], ca, direction)
        self.virtual_size[parent] += direction*self.size[child]

    def _flip(self, x):
        if x:
            self.l[x], self.r[x] = self.r[x], self.l[x]
            self.f[x], self.b[x] = self.b[x], self.f[x]
            self.rev[x] ^= 1

    def _push(self, x):
        if self.rev[x]:
            self._flip(self.l[x])
            self._flip(self.r[x])
            self.rev[x] = 0

    def _aux_root(self, x):
        p = self.p[x]
        return p == 0 or self.l[p] != x and self.r[p] != x

    def _rotate(self, x):
        y = self.p[x]
        z = self.p[y]
        if not self._aux_root(y):
            if self.l[z] == y:
                self.l[z] = x
            else:
                self.r[z] = x
        self.p[x] = z
        if self.r[y] == x:
            middle = self.l[x]
            self.r[y] = middle
            self.l[x] = y
        else:
            middle = self.r[x]
            self.l[y] = middle
            self.r[x] = y
        if middle:
            self.p[middle] = y
        self.p[y] = x
        self._pull(y)
        self._pull(x)

    def _splay(self, x):
        stack = [x]
        u = x
        while not self._aux_root(u):
            u = self.p[u]
            stack.append(u)
        for u in reversed(stack):
            self._push(u)
        while not self._aux_root(x):
            y = self.p[x]
            if not self._aux_root(y):
                z = self.p[y]
                if (self.l[y] == x) == (self.l[z] == y):
                    self._rotate(y)
                else:
                    self._rotate(x)
            self._rotate(x)

    def access(self, x):
        last, original = 0, x
        while x:
            self._splay(x)
            old = self.r[x]
            if old != last:
                if old:
                    self._virtual(x, old, 1)
                if last:
                    self._virtual(x, last, -1)
            self.r[x] = last
            self._pull(x)
            last = x
            x = self.p[x]
        self._splay(original)

    def makeroot(self, x):
        self.access(x)
        self._flip(x)

    def root(self, x):
        self.access(x)
        while True:
            self._push(x)
            if not self.l[x]:
                break
            x = self.l[x]
        self._splay(x)
        return x

    def execute(self, cmd):
        op = cmd['op']
        if op == 'set':
            u = cmd['u']+1
            self.access(u)
            self.w[u] = cmd['w']
            self._pull(u)
            return {'ok': True}
        if op == 'link':
            u, v = cmd['u']+1, cmd['v']+1
            self.makeroot(u)
            self.access(v)
            self.p[u] = v
            self._virtual(v, u, 1)
            self._pull(v)
            return {'ok': True}
        if op == 'cut':
            u, v = cmd['u']+1, cmd['v']+1
            self.makeroot(u)
            self.access(v)
            assert self.l[v] == u and self.r[u] == 0
            self.l[v] = 0
            self.p[u] = 0
            self._pull(v)
            return {'ok': True}
        if op == 'ask':
            u = cmd['u']+1
            self.makeroot(u)
            a, ca, b, cb = self._dp(u)
            best, ways = self._best(a, ca, b, cb)
            return {'n': self.size[u], 'best': dict(weight=best, ways=ways),
                    'out': dict(weight=a, ways=ca), 'in': dict(weight=b, ways=cb)}
        if op == 'pair':
            u, v = cmd['u']+1, cmd['v']+1
            self.makeroot(u)
            if self.root(v) != u:
                return {'connected': False}
            self.access(v)
            if u == v and cmd['su'] != cmd['sv']:
                return dict(connected=True, possible=False)
            index = 4*cmd['su']+2*cmd['sv']
            score, ways = self.f[v][index:index+2]
            if score == NEG:
                return dict(connected=True, possible=False)
            return dict(connected=True, possible=True, weight=score, ways=ways)
        raise ValueError(op)


def main():
    gc.disable()
    engine = None
    for line in sys.stdin.buffer:
        cmd = json.loads(line)
        if engine is None:
            engine = Forest(cmd['weights'], cmd['edges'], cmd['mod'])
            result = {'ok': True}
        else:
            result = engine.execute(cmd)
        sys.stdout.buffer.write((json.dumps(result, separators=(',', ':'))+'\n').encode())
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
