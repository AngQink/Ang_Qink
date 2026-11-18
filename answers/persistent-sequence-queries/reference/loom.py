"""Private reference: immutable AVL rope with rank-dependent lazy transforms."""
import json
import sys

P = 1000000007
BASE = 911382323
INV = pow(BASE - 1, -1, P)


class Node:
    __slots__ = ('l', 'r', 'h', 'n', 'pw', 's', 'q', 'm', 'f', 'z', 'a', 'b', 'c', 'rev')


def leaf(value):
    x = Node()
    value %= P
    x.l = x.r = None
    x.h = x.n = 1
    x.pw = BASE
    x.s = x.f = x.z = value
    x.q = value * value % P
    x.m = 0
    x.a, x.b, x.c, x.rev = 1, 0, 0, False
    return x


def branch(l, r):
    if l is None:
        return r
    if r is None:
        return l
    x = Node()
    x.l, x.r = l, r
    x.h = max(l.h, r.h) + 1
    x.n = l.n + r.n
    x.pw = l.pw * r.pw % P
    x.s = (l.s + r.s) % P
    x.q = (l.q + r.q) % P
    x.m = (l.m + r.m + l.n * r.s) % P
    x.f = (l.f + l.pw * r.f) % P
    x.z = (r.z + r.pw * l.z) % P
    x.a, x.b, x.c, x.rev = 1, 0, 0, False
    return x


def clone(x):
    y = Node()
    for field in Node.__slots__:
        setattr(y, field, getattr(x, field))
    return y


def transform(x, a, b, c):
    if x is None:
        return None
    a, b, c = a % P, b % P, c % P
    if (a, b, c) == (1, 0, 0):
        return x
    if x.n == 1:
        return leaf(a * x.s + b)
    y = clone(x)
    n = x.n
    i1 = n * (n - 1) // 2 % P
    i2 = n * (n - 1) * (2 * n - 1) // 6 % P
    g = (x.pw - 1) * INV % P
    j = ((n - 1) * x.pw - g + 1) * INV % P
    y.s = (a * x.s + b * n + c * i1) % P
    y.q = (a * a * x.q + 2 * a * b * x.s + 2 * a * c * x.m
           + b * b * n + 2 * b * c * i1 + c * c * i2) % P
    y.m = (a * x.m + b * i1 + c * i2) % P
    y.f = (a * x.f + b * g + c * j) % P
    y.z = (a * x.z + b * g + c * ((n - 1) * g - j)) % P
    y.a = a * x.a % P
    y.b = (a * x.b + b) % P
    y.c = (a * x.c + c) % P
    return y


def reverse(x):
    if x is None or x.n == 1:
        return x
    y = clone(x)
    y.l, y.r = x.r, x.l
    y.rev = not x.rev
    y.b = (x.b + x.c * (x.n - 1)) % P
    y.c = -x.c % P
    y.m = ((x.n - 1) * x.s - x.m) % P
    y.f, y.z = x.z, x.f
    return y


def children(x):
    l, r = x.l, x.r
    if x.rev:
        l, r = reverse(l), reverse(r)
    if (x.a, x.b, x.c) != (1, 0, 0):
        l = transform(l, x.a, x.b, x.c)
        r = transform(r, x.a, x.b + x.c * l.n, x.c)
    return l, r


def balance(l, r):
    if l.h > r.h + 1:
        a, b = children(l)
        if a.h >= b.h:
            return branch(a, branch(b, r))
        c, d = children(b)
        return branch(branch(a, c), branch(d, r))
    if r.h > l.h + 1:
        a, b = children(r)
        if b.h >= a.h:
            return branch(branch(l, a), b)
        c, d = children(a)
        return branch(branch(l, c), branch(d, b))
    return branch(l, r)


def join(l, r):
    if l is None:
        return r
    if r is None:
        return l
    if l.h > r.h + 1:
        a, b = children(l)
        return balance(a, join(b, r))
    if r.h > l.h + 1:
        a, b = children(r)
        return balance(join(l, a), b)
    return branch(l, r)


def split(x, k):
    if x is None:
        return None, None
    if k == 0:
        return None, x
    if k == x.n:
        return x, None
    l, r = children(x)
    if k < l.n:
        a, b = split(l, k)
        return a, join(b, r)
    if k == l.n:
        return l, r
    a, b = split(r, k - l.n)
    return join(l, a), b


def section(x, l, r):
    prefix, _ = split(x, r)
    _, middle = split(prefix, l)
    return middle


def repeat(x, count):
    result = None
    while count and x is not None:
        if count & 1:
            result = join(result, x)
        count >>= 1
        if count:
            x = branch(x, x)
    return result


def build(values):
    level = [leaf(x) for x in values]
    while len(level) > 1:
        level = [join(level[i], level[i + 1]) if i + 1 < len(level) else level[i]
                 for i in range(0, len(level), 2)]
    return level[0] if level else None


EMPTY = (0, 1, 0, 0, 0, 0, 0)


def stats(x):
    return EMPTY if x is None else (x.n, x.pw, x.s, x.q, x.m, x.f, x.z)


def combine(l, r):
    n, pw, s, q, m, f, z = l
    nn, pp, ss, qq, mm, ff, zz = r
    return (n + nn, pw * pp % P, (s + ss) % P, (q + qq) % P,
            (m + mm + n * ss) % P, (f + pw * ff) % P, (zz + pp * z) % P)


def query(x, start, end):
    if start == end:
        return EMPTY
    if start == 0 and end == x.n:
        return stats(x)
    l, r = children(x)
    if end <= l.n:
        return query(l, start, end)
    if start >= l.n:
        return query(r, start - l.n, end - l.n)
    return combine(query(l, start, l.n), query(r, 0, end - l.n))


class Loom:
    def __init__(self):
        self.roots = {0: None}
        self.serial = 0

    def execute(self, cmd):
        op = cmd['op']
        roots = self.roots
        if op == 'new':
            result = build(cmd['values'])
        elif op == 'concat':
            result = join(roots[cmd['left']], roots[cmd['right']])
        elif op == 'repeat':
            result = repeat(roots[cmd['v']], cmd['times'])
        elif op == 'slice':
            result = section(roots[cmd['v']], cmd['l'], cmd['r'])
        elif op == 'splice':
            source = section(roots[cmd['src']], cmd['sl'], cmd['sr'])
            l, tail = split(roots[cmd['v']], cmd['l'])
            _, r = split(tail, cmd['r'] - cmd['l'])
            result = join(join(l, source), r)
        elif op in ('edit', 'reverse'):
            l, tail = split(roots[cmd['v']], cmd['l'])
            middle, r = split(tail, cmd['r'] - cmd['l'])
            middle = (reverse(middle) if op == 'reverse' else
                      transform(middle, cmd['a'], cmd['b'], cmd['c']))
            result = join(join(l, middle), r)
        elif op == 'query':
            n, _, s, q, m, f, z = query(roots[cmd['v']], cmd['l'], cmd['r'])
            return dict(n=n, sum=s, square=q, moment=m, forward=f, backward=z)
        elif op == 'at':
            x, i = roots[cmd['v']], cmd['i']
            while x.n != 1:
                l, r = children(x)
                if i < l.n:
                    x = l
                else:
                    x, i = r, i - l.n
            return {'value': x.s}
        elif op == 'drop':
            del roots[cmd['v']]
            return {'ok': True}
        else:
            raise ValueError(op)
        self.serial += 1
        roots[self.serial] = result
        return {'v': self.serial, 'n': 0 if result is None else result.n}


def main():
    engine = Loom()
    for line in sys.stdin.buffer:
        cmd = json.loads(line.decode('utf-8'))
        result = engine.execute(cmd)
        sys.stdout.buffer.write((json.dumps(result, separators=(',', ':')) + '\n').encode('utf-8'))
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
