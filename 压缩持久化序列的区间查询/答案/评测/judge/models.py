"""Independent models: literal lists and closed-form periodic ramp pieces."""
P = 1000000007
BASE = 911382323


def literal_stats(values):
    s = q = m = f = z = 0
    power = 1
    for i, value in enumerate(values):
        s += value
        q += value * value
        m += i * value
        f = (f + power * value) % P
        power = power * BASE % P
    power = 1
    for value in reversed(values):
        z = (z + power * value) % P
        power = power * BASE % P
    return dict(n=len(values), sum=s % P, square=q % P, moment=m % P, forward=f, backward=z)


class ListModel:
    def __init__(self):
        self.roots = {0: []}
        self.serial = 0

    def execute(self, cmd):
        op, roots = cmd['op'], self.roots
        if op == 'new':
            out = [v % P for v in cmd['values']]
        elif op == 'concat':
            out = roots[cmd['left']] + roots[cmd['right']]
        elif op == 'repeat':
            out = roots[cmd['v']] * cmd['times']
        elif op == 'slice':
            out = roots[cmd['v']][cmd['l']:cmd['r']]
        elif op == 'splice':
            old, source = roots[cmd['v']], roots[cmd['src']]
            out = old[:cmd['l']] + source[cmd['sl']:cmd['sr']] + old[cmd['r']:]
        elif op in ('edit', 'reverse'):
            old = roots[cmd['v']]
            middle = old[cmd['l']:cmd['r']]
            middle = (middle[::-1] if op == 'reverse' else
                      [(cmd['a'] * x + cmd['b'] + cmd['c'] * j) % P for j, x in enumerate(middle)])
            out = old[:cmd['l']] + middle + old[cmd['r']:]
        elif op == 'query':
            return literal_stats(roots[cmd['v']][cmd['l']:cmd['r']])
        elif op == 'at':
            return {'value': roots[cmd['v']][cmd['i']]}
        elif op == 'drop':
            del roots[cmd['v']]
            return {'ok': True}
        else:
            raise ValueError(op)
        self.serial += 1
        roots[self.serial] = out
        return {'v': self.serial, 'n': len(out)}


# A piece (n, pattern, phase, stride, a, b, c) represents
# a*pattern[(phase+stride*i)%len(pattern)] + b+c*i, modulo P.
def subpiece(piece, l, r):
    _, pat, phase, stride, a, b, c = piece
    return (r-l, pat, (phase+stride*l) % len(pat), stride, a, (b+c*l) % P, c)


def part(pieces, l, r):
    result, pos = [], 0
    for piece in pieces:
        end = pos + piece[0]
        if end > l and pos < r:
            result.append(subpiece(piece, max(0, l-pos), min(piece[0], r-pos)))
        pos = end
        if pos >= r:
            break
    return result


def geometric(z, count):
    if z == 1:
        return count % P, count*(count-1)//2 % P
    zn = pow(z, count, P)
    inv = pow(1-z, -1, P)
    g = (1-zn)*inv % P
    j = (z-count*zn+(count-1)*zn*z)*inv*inv % P
    return g, j


def piece_stats(piece):
    n, pat, phase, stride, a, b, c = piece
    period = len(pat)
    s = q = m = f = z = 0
    jump = pow(BASE, period, P)
    inv_jump = pow(jump, -1, P)
    for r in range(min(n, period)):
        count = (n-1-r)//period+1
        d = (a*pat[(phase+stride*r) % period]+b+c*r) % P
        e = c*period % P
        t1 = count*(count-1)//2 % P
        t2 = count*(count-1)*(2*count-1)//6 % P
        s += count*d+e*t1
        q += count*d*d+2*d*e*t1+e*e*t2
        m += r*d*count+(r*e+period*d)*t1+period*e*t2
        g, j = geometric(jump, count)
        f += pow(BASE, r, P)*(d*g+e*j)
        g, j = geometric(inv_jump, count)
        z += pow(BASE, n-1-r, P)*(d*g+e*j)
    return dict(n=n, sum=s % P, square=q % P, moment=m % P, forward=f % P, backward=z % P)


def merge_stats(l, r):
    n, nn = l['n'], r['n']
    return dict(n=n+nn, sum=(l['sum']+r['sum']) % P,
                square=(l['square']+r['square']) % P,
                moment=(l['moment']+r['moment']+n*r['sum']) % P,
                forward=(l['forward']+pow(BASE, n, P)*r['forward']) % P,
                backward=(r['backward']+pow(BASE, nn, P)*l['backward']) % P)


class PieceModel:
    def __init__(self):
        self.roots, self.serial = {0: []}, 0

    def length(self, v):
        return sum(piece[0] for piece in self.roots[v])

    def execute(self, cmd):
        op, roots = cmd['op'], self.roots
        if op == 'new':
            pat = tuple(x % P for x in cmd['values'])
            out = [(len(pat), pat, 0, 1, 1, 0, 0)] if pat else []
        elif op == 'concat':
            out = roots[cmd['left']] + roots[cmd['right']]
        elif op == 'slice':
            out = part(roots[cmd['v']], cmd['l'], cmd['r'])
        elif op == 'repeat':
            old, times = roots[cmd['v']], cmd['times']
            if times == 0 or not old:
                out = []
            elif len(old) == 1 and old[0][6] == 0 and old[0][0] % len(old[0][1]) == 0:
                out = [(old[0][0]*times, *old[0][1:])]
            else:
                assert times <= 8, 'model fixture must not expand a huge repeat'
                out = old*times
        elif op == 'splice':
            old = roots[cmd['v']]
            out = (part(old, 0, cmd['l']) + part(roots[cmd['src']], cmd['sl'], cmd['sr'])
                   + part(old, cmd['r'], self.length(cmd['v'])))
        elif op in ('edit', 'reverse'):
            old = roots[cmd['v']]
            middle = part(old, cmd['l'], cmd['r'])
            changed, position = [], 0
            for piece in (reversed(middle) if op == 'reverse' else middle):
                n, pat, phase, stride, a, b, c = piece
                if op == 'reverse':
                    changed.append((n, pat, (phase+stride*(n-1)) % len(pat), -stride,
                                    a, (b+c*(n-1)) % P, -c % P))
                else:
                    aa, bb, cc = cmd['a'], cmd['b'], cmd['c']
                    changed.append((n, pat, phase, stride, aa*a % P,
                                    (aa*b+bb+cc*position) % P, (aa*c+cc) % P))
                position += n
            out = part(old, 0, cmd['l']) + changed + part(old, cmd['r'], self.length(cmd['v']))
        elif op == 'query':
            result = literal_stats([])
            for piece in part(roots[cmd['v']], cmd['l'], cmd['r']):
                result = merge_stats(result, piece_stats(piece))
            return result
        elif op == 'at':
            piece = part(roots[cmd['v']], cmd['i'], cmd['i']+1)[0]
            _, pat, phase, _, a, b, _ = piece
            return {'value': (a*pat[phase]+b) % P}
        elif op == 'drop':
            del roots[cmd['v']]
            return {'ok': True}
        else:
            raise ValueError(op)
        self.serial += 1
        roots[self.serial] = out
        return {'v': self.serial, 'n': sum(piece[0] for piece in out)}
