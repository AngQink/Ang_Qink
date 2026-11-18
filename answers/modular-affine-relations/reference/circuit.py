"""Affine relations represented by cosets of full-rank integer lattices.

All arithmetic is exact.  No factorization, floating point, or external code.
"""
import json
import sys
from math import gcd, prod


def bezout(a, b):
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q*r1
        s0, s1 = s1, s0 - q*s1
        t0, t1 = t1, t0 - q*t1
    return r0, s0, t0


def lattice(generators, dim, mod):
    """Upper row HNF of span_Z(generators) + mod*Z^dim.

    Retaining the modulus lattice during every insertion is essential: a
    nonunit pivot can generate another row through its annihilator.
    """
    basis = [[mod if i == j else 0 for j in range(dim)] for i in range(dim)]
    for values in generators:
        row = [value % mod for value in values]
        for i in range(dim):
            b = row[i]
            if not b:
                continue
            old = basis[i]
            a = old[i]
            if b % a == 0:
                q = b // a
                row[i] = 0
                for j in range(i+1, dim):
                    row[j] = (row[j] - q*old[j]) % mod
            else:
                g, s, t = bezout(a, b)
                ag, bg = a//g, b//g
                new = old[:]
                new[i] = g
                row[i] = 0
                for j in range(i+1, dim):
                    x, y = old[j], row[j]
                    new[j] = (s*x + t*y) % mod
                    row[j] = (ag*y - bg*x) % mod
                basis[i] = new
    for i in range(dim-1, -1, -1):
        row = basis[i]
        for j in range(i+1, dim):
            other = basis[j]
            q = row[j] // other[j]
            if q:
                row[j] -= q*other[j]
                for k in range(j+1, dim):
                    row[k] = (row[k] - q*other[k]) % mod
    return tuple(map(tuple, basis))


def reduce_point(point, basis, mod):
    point = [x % mod for x in point]
    for i, row in enumerate(basis):
        q, point[i] = divmod(point[i], row[i])
        if q:
            for j in range(i+1, len(point)):
                point[j] = (point[j] - q*row[j]) % mod
    return tuple(point)


class Relation:
    __slots__ = ('m', 'd', 'c', 'B', 'count', '_dual')

    def __init__(self, mod, dim, center=None, basis=None):
        self.m, self.d, self._dual = mod, dim, None
        if center is None:
            self.c = self.B = None
            self.count = 0
        else:
            self.B = basis
            self.c = reduce_point(center, basis, mod)
            self.count = mod**dim // prod(basis[i][i] for i in range(dim))

    @classmethod
    def universal(cls, mod, dim):
        return cls(mod, dim, [0]*dim, tuple(tuple(int(i == j) for j in range(dim)) for i in range(dim)))

    def answer(self):
        return {'dim': self.d, 'count': self.count, 'first': None if self.c is None else list(self.c)}

    def project(self, keep):
        if self.c is None:
            return Relation(self.m, len(keep))
        rows = [[row[j] for j in keep] for row in self.B]
        return Relation(self.m, len(keep), [self.c[j] for j in keep], lattice(rows, len(keep), self.m))

    def image(self, matrix, bias):
        out = len(bias)
        if self.c is None:
            return Relation(self.m, out)
        m = self.m
        matrix = [[x % m for x in row] for row in matrix]
        rows = [[sum(x*y for x, y in zip(row, a)) % m for a in matrix] for row in self.B]
        center = [(b + sum(x*y for x, y in zip(self.c, a))) % m for a, b in zip(matrix, bias)]
        return Relation(m, out, center, lattice(rows, out, m))

    def pin(self, matrix, rhs):
        if self.c is None:
            return self
        d, m = self.d, self.m
        constraints = []
        seen = set()
        for row, value in zip(matrix, rhs):
            row = tuple(x % m for x in row)
            value %= m
            if not any(row):
                if value:
                    return Relation(m, d)
                continue
            item = row, value
            if item not in seen:
                seen.add(item)
                constraints.append(item)
        if not constraints:
            return self
        r = len(constraints)
        lift = []
        for row in self.B:
            lift.append([sum(x*y for x, y in zip(row, a)) % m for a, _ in constraints] + list(row))
        basis = lattice(lift, r+d, m)
        center = [sum(x*y for x, y in zip(self.c, a)) % m for a, _ in constraints] + list(self.c)
        for i, (_, value) in enumerate(constraints):
            delta = value - center[i]
            pivot = basis[i][i]
            if delta % pivot:
                return Relation(m, d)
            q = delta // pivot
            if q:
                for j in range(i+1, r+d):
                    center[j] = (center[j] + q*basis[i][j]) % m
            center[i] = value
        return Relation(m, d, center[r:], tuple(row[r:] for row in basis[r:]))

    def dual(self):
        if self._dual is None:
            d, m, B = self.d, self.m, self.B
            rows = []
            for j in range(d):
                v = [0]*d
                for i in range(d-1, -1, -1):
                    value = (m if i == j else 0) - sum(B[i][k]*v[k] for k in range(i+1, d))
                    assert value % B[i][i] == 0
                    v[i] = value // B[i][i]
                rows.append(tuple(x % m for x in v))
            self._dual = tuple(rows)
        return self._dual

    def meet(self, other):
        if self.c is None:
            return self
        if other.c is None:
            return other
        rows = other.dual()
        rhs = [sum(x*y for x, y in zip(row, other.c)) % self.m for row in rows]
        return self.pin(rows, rhs)

    def has(self, point):
        return self.c is not None and not any(reduce_point([x-y for x, y in zip(point, self.c)], self.B, self.m))


def join(left, right, ties, keep):
    m, p, q = left.m, left.d, right.d
    if left.c is None or right.c is None:
        return Relation(m, len(keep))
    basis = tuple(row + (0,)*q for row in left.B) + tuple((0,)*p + row for row in right.B)
    both = Relation(m, p+q, left.c + right.c, basis)
    rows = []
    for i, j in ties:
        row = [0]*(p+q)
        row[i] = 1
        row[p+j] = -1
        rows.append(row)
    return both.pin(rows, [0]*len(rows)).project(keep)


class Engine:
    def __init__(self, mod):
        self.m, self.slots = mod, {}

    def execute(self, cmd):
        op, slots = cmd['op'], self.slots
        if op == 'ask':
            return slots[cmd['src']].answer()
        if op == 'has':
            return {'contains': slots[cmd['src']].has(cmd['point'])}
        if op == 'probe':
            return slots[cmd['src']].pin(cmd['a'], cmd['b']).project(cmd['keep']).answer()
        if op == 'make':
            value = Relation.universal(self.m, cmd['dim']).pin(cmd['a'], cmd['b'])
        elif op == 'map':
            value = slots[cmd['src']].image(cmd['a'], cmd['b'])
        elif op == 'pin':
            value = slots[cmd['src']].pin(cmd['a'], cmd['b'])
        elif op == 'copy':
            value = slots[cmd['src']]
        elif op == 'meet':
            value = slots[cmd['left']].meet(slots[cmd['right']])
        elif op == 'join':
            value = join(slots[cmd['left']], slots[cmd['right']], cmd['ties'], cmd['keep'])
        else:
            raise AssertionError(op)
        slots[cmd['dst']] = value
        return {'ok': True}


def main():
    engine = None
    out = sys.stdout.buffer
    for line in sys.stdin.buffer:
        cmd = json.loads(line)
        if cmd['op'] == 'init':
            engine = Engine(cmd['mod'])
            result = {'ok': True}
        else:
            result = engine.execute(cmd)
        out.write(json.dumps(result, separators=(',', ':')).encode('ascii') + b'\n')
        out.flush()


if __name__ == '__main__':
    main()
