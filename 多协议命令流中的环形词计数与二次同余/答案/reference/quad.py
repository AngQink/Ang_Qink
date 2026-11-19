"""QUAD. Each command is routed to one independently initialized module."""
import hashlib
import heapq
import json
import math
import sys
from array import array
from collections import deque


def divisors(factors):
    values = [1]
    for prime, exponent in factors:
        values = [base * prime**power for base in values for power in range(exponent + 1)]
    return sorted(values)


def remember(cache, key, value, limit):
    if len(cache) >= limit:
        cache.pop(next(iter(cache)))
    cache[key] = value
    return value


class Module:
    def __init__(self, state):
        self.state = state
        self.snapshots = {}
        self.cache = {}

    def replace(self, state):
        if state != self.state:
            self.state = state
            self.cache.clear()

    def command(self, op, request):
        if op == 'save':
            self.snapshots[request['slot']] = self.state
        elif op == 'load':
            self.replace(self.snapshots[request['slot']])
        else:
            return self.run(op, request)
        return {'ok': True}


def tree_minor(edges, root, degrees):
    active = [i for i, d in enumerate(degrees)
              if i != root and (d or any(row[i] for row in edges))]
    matrix = [[degrees[u] - edges[u][u] if u == v else -edges[u][v]
               for v in active] for u in active]
    previous = 1
    # A nonsingular rooted graph Laplacian has positive leading principal minors.
    # A zero pivot therefore implies a zero determinant for these matrices.
    for k in range(len(matrix) - 1):
        pivot = matrix[k][k]
        if pivot == 0:
            return 0
        for i in range(k + 1, len(matrix)):
            row = matrix[i]
            for j in range(k + 1, len(matrix)):
                row[j] = (pivot * row[j] - row[k] * matrix[k][j]) // previous
        previous = pivot
    return matrix[-1][-1] if matrix else 1


class PrimeFactorials:
    def __init__(self, prime, power):
        self.prime = prime
        self.modulus = prime**power
        bound = 1
        while bound * prime <= 200000:
            bound *= prime
        self.lift = self.modulus * bound
        self.valuation = array('I', [0])
        self.units = array('Q', [1])

    def grow(self, limit):
        unit = self.units[-1]
        valuation = self.valuation[-1]
        p, lift = self.prime, self.lift
        for k in range(len(self.units), limit + 1):
            integer = k
            while integer % p == 0:
                integer //= p
                valuation += 1
            unit = unit * integer % lift
            self.valuation.append(valuation)
            self.units.append(unit)

    def ratio(self, scalar, top, bottom):
        if scalar == 0:
            return 0
        self.grow(max(max(top, default=0), max(bottom, default=0)))
        valuation = sum(self.valuation[x] for x in top) - sum(self.valuation[x] for x in bottom)
        while scalar % self.prime == 0:
            scalar //= self.prime
            valuation += 1
        assert valuation >= 0
        lift = self.lift
        multiplier = pow(self.prime, valuation, lift)
        if multiplier == 0:
            return 0
        numerator, denominator = scalar % lift, 1
        for x in top:
            numerator = numerator * self.units[x] % lift
        for x in bottom:
            denominator = denominator * self.units[x] % lift
        return numerator * pow(denominator, -1, lift) * multiplier % lift

    def divide(self, residue, divisor):
        power = 1
        while divisor % self.prime == 0:
            divisor //= self.prime
            power *= self.prime
        assert residue % power == 0
        return residue // power * pow(divisor, -1, self.modulus) % self.modulus


class Euler(Module):
    def __init__(self, request):
        super().__init__(tuple(map(tuple, request['edges'])))
        self.tables = [PrimeFactorials(*factor) for factor in request['mod_factors']]
        self.mod = math.prod(t.modulus for t in self.tables)
        self.crt = []
        for table in self.tables:
            complement = self.mod // table.modulus
            self.crt.append(complement * pow(complement, -1, table.modulus))

    def combine(self, residues):
        return sum(value * weight for value, weight in zip(residues, self.crt)) % self.mod

    def prepare(self, factors):
        edges = self.state
        degrees = list(map(sum, edges))
        n = sum(degrees)
        active = [i for i, degree in enumerate(degrees) if degree]
        root = active[0]
        tree = tree_minor(edges, root, degrees)
        counts, exact, periods = {}, {}, []
        repeats = divisors(factors)[::-1]
        nonzero = [x for row in edges for x in row if x]
        for r in repeats:
            top = [degrees[i] // r - 1 for i in active]
            bottom = [x // r for x in nonzero]
            scalar = n // r * (tree // (r ** (len(active) - 1)))
            counts[r] = [table.ratio(scalar, top, bottom) for table in self.tables]
            exact[r] = [
                (value - sum(exact[s][j] for s in exact if s % r == 0)) % table.lift
                for j, (table, value) in enumerate(zip(self.tables, counts[r]))
            ]
            period = n // r
            periods.append({'period': period, 'words': self.combine(exact[r]),
                            'necklaces': self.combine(table.divide(x, period)
                                                      for table, x in zip(self.tables, exact[r]))})
        core = {'possible': bool(tree), 'length': n, 'words': self.combine(counts[1]),
                'necklaces': sum(item['necklaces'] for item in periods) % self.mod,
                'periods': periods}
        word, digest = None, None
        if tree:
            remaining = [list(row) for row in edges]
            pointers = [0] * len(edges)
            stack, postorder = [root], bytearray()
            while stack:
                u = stack[-1]
                v = pointers[u]
                while v < len(edges) and remaining[u][v] == 0:
                    v += 1
                pointers[u] = v
                if v == len(edges):
                    postorder.append(stack.pop())
                else:
                    remaining[u][v] -= 1
                    stack.append(v)
            postorder.reverse()
            word = bytes(postorder[:-1])
            digest = hashlib.sha256(b'EULER1' + n.to_bytes(8, 'little') + word).hexdigest()
        data = core, {r: self.combine(values) for r, values in counts.items()}, word, digest
        self.cache['prepared'] = data
        return data

    def prefix(self, prefix, core):
        if not prefix:
            return core['words']
        if len(prefix) > core['length'] or not core['possible']:
            return 0
        tag = tuple(prefix)
        if tag in self.cache:
            return self.cache[tag]
        edges = [list(row) for row in self.state]
        for u, v in zip(prefix, prefix[1:]):
            if edges[u][v] == 0:
                return 0
            edges[u][v] -= 1
        root = prefix[0]
        degrees = list(map(sum, edges))
        tree = tree_minor(edges, root, degrees)
        if tree == 0:
            return 0
        top = [degrees[root]] + [d - 1 for i, d in enumerate(degrees) if i != root and d]
        bottom = [x for row in edges for x in row if x]
        result = self.combine(table.ratio(tree, top, bottom) for table in self.tables)
        self.cache[tag] = result
        return result

    def run(self, op, request):
        if op == 'cycle':
            path, delta = request['vertices'], request['delta']
            if delta:
                edges = [list(row) for row in self.state]
                for u, v in zip(path, path[1:] + path[:1]):
                    edges[u][v] += delta
                self.replace(tuple(map(tuple, edges)))
            return {'ok': True}
        assert op == 'count'
        data = self.cache.get('prepared')
        if data is None:
            data = self.prepare(request['gcd_factors'])
        core, rotations, word, digest = data
        length = core['length']
        return dict(core,
                    fixed_rotations=[rotations.get(length // math.gcd(k, length), 0) for k in request['rotations']],
                    prefix_counts=[self.prefix(p, core) for p in request['prefixes']],
                    witness=None if word is None else {'sha256': digest,
                                                         'at': [word[k] if k < length else None for k in request['at']]})


class TreeStore:
    def __init__(self):
        self.ids = {}
        self.nodes = []

    def intern(self, key, size):
        if key in self.ids:
            return self.ids[key]
        rule, kids = key
        raw = b'DERIVE1' + rule.to_bytes(4, 'little') + bytes([len(kids)])
        raw += b''.join(self.nodes[k][3] for k in kids)
        index = len(self.nodes)
        self.nodes.append((rule, kids, size, hashlib.sha256(raw).digest()))
        self.ids[key] = index
        return index

    def less(self, key, old):
        # Root identifiers determine arity. Preorder encodings of whole trees
        # are prefix-free, so descend into the first distinct child pair.
        while True:
            if key[0] != old[0]:
                return key[0] < old[0]
            for a, b in zip(key[1], old[1]):
                if a != b:
                    key, old = self.nodes[a], self.nodes[b]
                    break
            else:
                return False

    def at(self, root, index):
        if index >= self.nodes[root][2]:
            return None
        while index:
            index -= 1
            for child in self.nodes[root][1]:
                size = self.nodes[child][2]
                if index < size:
                    root = child
                    break
                index -= size
        return self.nodes[root][0]


class InkChart:
    def __init__(self, count, rules, weights, mod, word):
        end = len(word)
        intervals = [(i, j) for i in range(end + 1) for j in range(i, end + 1)]
        lookup = {pair: i for i, pair in enumerate(intervals)}
        span = len(intervals)
        items = count * span
        empty = [lookup[i, i] for i in range(end + 1)]
        letters = {ch: [lookup[i, i+1] for i, c in enumerate(word) if c == ch] for ch in 'abcd'}
        splits = [[(lookup[i, k], lookup[k, j]) for k in range(i, j + 1)] for i, j in intervals]
        outgoing = [[] for _ in range(items)]
        heads, left, right, costs, sizes, waiting, ids = [], [], [], [], [], [], []
        best = [None] * items
        keys = [None] * items
        roots = [-1] * items
        heap = []
        store = TreeStore()

        def offer(head, cost, size, key):
            pair = (cost, size)
            previous = best[head]
            if previous is None or pair < previous:
                best[head], keys[head] = pair, key
                heapq.heappush(heap, (cost, size, head))
            elif pair == previous and store.less(key, keys[head]):
                keys[head] = key

        def edge(head, a, b, cost, rule):
            idx = len(heads)
            heads.append(head)
            left.append(a)
            right.append(b)
            costs.append(cost)
            sizes.append(1)
            ids.append(rule)
            if a < 0:
                waiting.append(0)
                offer(head, cost, 1, (rule, ()))
            else:
                outgoing[a].append(idx)
                if b < 0:
                    waiting.append(1)
                else:
                    outgoing[b].append(idx)
                    waiting.append(2)

        for (rule, parent, rhs), (cost, enabled) in zip(rules, weights):
            if not enabled:
                continue
            start = parent * span
            if not rhs or isinstance(rhs[0], str):
                for t in empty if not rhs else letters[rhs[0]]:
                    edge(start+t, -1, -1, cost, rule)
            elif len(rhs) == 1:
                child = rhs[0] * span
                for t in range(span):
                    edge(start+t, child+t, -1, cost, rule)
            else:
                a, b = (x*span for x in rhs)
                for t, options in enumerate(splits):
                    for i, j in options:
                        edge(start+t, a+i, b+j, cost, rule)

        # Every production adds one node, making each child strictly smaller
        # than the parent under the (cost, size) distance.
        while heap:
            cost, size, item = heapq.heappop(heap)
            if roots[item] >= 0 or best[item] != (cost, size):
                continue
            roots[item] = store.intern(keys[item], size)
            for idx in outgoing[item]:
                costs[idx] += cost
                waiting[idx] -= 1
                parent = heads[idx]
                if roots[parent] >= 0:
                    continue
                sizes[idx] += size
                if waiting[idx] == 0:
                    a, b = left[idx], right[idx]
                    kids = (roots[a],) if b < 0 else (roots[a], roots[b])
                    offer(parent, costs[idx], sizes[idx], (ids[idx], kids))

        # Consider all minimal-cost choices, including taller derivations.
        # Productive items surviving leaf elimination reach a pumpable cycle.
        uses = [[] for _ in range(items)]
        choices = [[] for _ in range(items)]
        depend = [0] * items
        for idx, parent in enumerate(heads):
            if waiting[idx] or costs[idx] != best[parent][0]:
                continue
            a, b = left[idx], right[idx]
            choices[parent].append(idx)
            if a >= 0:
                uses[a].append(parent)
                depend[parent] += 1
            if b >= 0:
                uses[b].append(parent)
                depend[parent] += 1
        ready = deque(i for i in range(items) if roots[i] >= 0 and depend[i] == 0)
        ways = [None] * items
        while ready:
            item = ready.popleft()
            value = 0
            for idx in choices[item]:
                a, b = left[idx], right[idx]
                value += 1 if a < 0 else ways[a] if b < 0 else ways[a] * ways[b]
            ways[item] = value % mod
            for parent in uses[item]:
                depend[parent] -= 1
                if depend[parent] == 0:
                    ready.append(parent)
        self.span, self.end = span, lookup[0, end]
        self.best, self.roots, self.ways, self.store = best, roots, ways, store

    def assess(self, start, indices):
        item = start * self.span + self.end
        if self.roots[item] < 0:
            return {'possible': False}
        cost, size = self.best[item]
        root, ways = self.roots[item], self.ways[item]
        return {'possible': True, 'cost': cost, 'infinite': ways is None, 'ways': ways,
                'witness': {'nodes': size, 'sha256': self.store.nodes[root][3].hex(),
                            'at': [self.store.at(root, index) for index in indices]}}


class Ink(Module):
    def __init__(self, request):
        rules = request['rules']
        super().__init__(tuple((r['cost'], r['enabled']) for r in rules))
        self.rules = [(r['id'], r['lhs'], tuple(r['rhs'])) for r in rules]
        self.indices = {r['id']: i for i, r in enumerate(rules)}
        self.nonterminals = request['nonterminals']
        self.mod = request['mod']

    def run(self, op, request):
        if op == 'parse':
            word = request['word']
            chart = self.cache.get(word)
            if chart is None:
                chart = remember(self.cache, word,
                                 InkChart(self.nonterminals, self.rules, self.state, self.mod, word), 3)
            return chart.assess(request['start'], request['at'])
        idx = self.indices[request['id']]
        cost, enabled = self.state[idx]
        new = (request['cost'], enabled) if op == 'weight' else (cost, request['value'])
        self.replace(self.state[:idx] + (new,) + self.state[idx+1:])
        return {'ok': True}



class CyclicCoefficients:
    """Coefficient arithmetic in (Z/modulus)[z]/(z**degree - 1)."""
    def __init__(self, degree, modulus, width):
        self.degree = degree
        self.modulus = modulus
        self.bits = 2 * modulus.bit_length() + (width * degree).bit_length() + 1
        self.mask = (1 << self.bits) - 1
        self.cut = self.bits * degree
        self.low = (1 << self.cut) - 1

    def mono(self, exponent):
        return 1 << (self.bits * (exponent % self.degree))

    def unpack(self, value):
        return [(value >> (i * self.bits)) & self.mask for i in range(self.degree)]

    def pack(self, coefficients):
        out = 0
        for i, value in enumerate(coefficients):
            out |= (value % self.modulus) << (i * self.bits)
        return out

    def reduce(self, value):
        folded = (value & self.low) + (value >> self.cut)
        out = 0
        for i in range(self.degree):
            out |= ((folded & self.mask) % self.modulus) << (i * self.bits)
            folded >>= self.bits
        return out

    def doubled(self, packed):
        out = [0] * self.degree
        for i, value in enumerate(self.unpack(packed)):
            out[2*i % self.degree] += value
        return self.pack(out)


class MatrixRecurrence:
    """Compute scalar forms of A**n via the characteristic polynomial of A."""
    def __init__(self, weights, edges, degree, lift, tau):
        self.order = len(edges)
        c = self.order
        # Small powers only. Every coefficient is bounded by c**c, so 2**32
        # recovers exact integer coefficients for the Newton identities.
        small = CyclicCoefficients(degree, 1 << 32, c)
        matrix = [[small.mono(weights[j]) if edges[i][j] else 0 for j in range(c)]
                  for i in range(c)]
        columns = list(zip(*matrix))
        seed = [[int(i == j) for j in range(c)] for i in range(c)]
        traces, mirror_seeds = [], []
        vertices = [i for i in range(c) if tau[i] == i]
        seams = [i for i in range(c) if edges[i][tau[i]]]
        self.ring = ring = CyclicCoefficients(degree, lift, c)
        first = [ring.mono(w) for w in weights]
        twice = [ring.mono(2*w) for w in weights]
        end = [ring.reduce(sum(first[j] for j in vertices if edges[i][j])) for i in range(c)]
        for exponent in range(c+1):
            traces.append(small.unpack(small.reduce(sum(seed[i][i] for i in range(c)))))
            if exponent == c:
                break
            paired = [[ring.doubled(ring.pack(small.unpack(x))) for x in row] for row in seed]
            odd = ring.reduce(sum(first[i] * paired[i][j] for i in vertices for j in seams))
            vertex_start = [ring.reduce(sum(first[i] * paired[i][j] for i in vertices)) for j in range(c)]
            even_v = ring.reduce(sum(x * y for x, y in zip(vertex_start, end)))
            even_e = ring.reduce(sum(twice[i] * paired[i][j] for i in seams for j in seams))
            mirror_seeds.append((odd, even_v, even_e))
            seed = [[small.reduce(sum(x*y for x, y in zip(row, col))) for col in columns]
                    for row in seed]
        characteristic = [[1] + [0]*(degree-1)]
        for k in range(1, c+1):
            out = [0] * degree
            for j in range(1, k+1):
                for r, a in enumerate(characteristic[k-j]):
                    for s, b in enumerate(traces[j]):
                        out[(r+s) % degree] -= a*b
            assert all(value % k == 0 for value in out)
            characteristic.append([x//k for x in out])
        self.replacement = [ring.pack([-x for x in a]) for a in characteristic[:0:-1]]
        self.trace = [ring.pack(a) for a in traces[:-1]]
        self.mirror_seeds = list(zip(*mirror_seeds))
        one = [1] + [0]*(c-1)
        variable = [0, 1] + [0]*(c-2) if c > 1 else self.replacement[:]
        self.identity = one
        self.binary = [variable]
        self.remainders = {0: one}

    def multiply(self, a, b):
        c, ring = self.order, self.ring
        raw = [0] * (2*c-1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    raw[i+j] += x*y
        # Each target degree receives up to c contributions from this
        # convolution and each subsequent reduction together. Reduce pending
        # sums before adding more than c products into one packed value.
        reduced = list(map(ring.reduce, raw))
        for i in range(2*c-2, c-1, -1):
            value = reduced[i]
            if value:
                for j, coefficient in enumerate(self.replacement, i-c):
                    if coefficient:
                        reduced[j] = ring.reduce(reduced[j] + value*coefficient)
        return reduced[:c]

    def power(self, exponent):
        old = self.remainders.get(exponent)
        if old is not None:
            return old
        while len(self.binary) < exponent.bit_length():
            self.binary.append(self.multiply(self.binary[-1], self.binary[-1]))
        num = exponent
        result = None
        while num:
            bit = num & -num
            value = self.binary[bit.bit_length()-1]
            result = value if result is None else self.multiply(result, value)
            num ^= bit
        self.remainders[exponent] = result
        return result

    def closed(self, length):
        return self.ring.unpack(self.ring.reduce(sum(x*y for x,y in zip(self.power(length), self.trace))))

    def reflected(self, length):
        half = (length-1)//2 if length & 1 else length//2-1
        coeff = [self.ring.doubled(x) for x in self.power(half)]
        def evaluate(seed):
            return self.ring.unpack(self.ring.reduce(sum(x*y for x,y in zip(coeff, seed))))
        if length & 1:
            odd = evaluate(self.mirror_seeds[0])
            return odd, odd
        return evaluate(self.mirror_seeds[1]), evaluate(self.mirror_seeds[2])


class Mirror(Module):
    def __init__(self, request):
        super().__init__((tuple(request['weights']), tuple(map(tuple, request['edges']))))
        self.tau = request['mirror'][:]
        self.mod = request['mod']
        self.degree = request['inventory_mod']

    def prepare(self, factors):
        ds = divisors(factors)
        n = ds[-1]
        weights, edges = self.state
        rec = MatrixRecurrence(weights, edges, self.degree, 2*n*self.mod, self.tau)
        values = [(d, rec.closed(d), *rec.reflected(d)) for d in ds]
        return remember(self.cache, factors, values, 4)

    def orbit(self, request):
        factors = tuple(map(tuple, request['factors']))
        values = self.cache.get(factors)
        if values is None:
            values = self.prepare(factors)
        n = values[-1][0]
        lift = 2*n*self.mod
        words, exact, reflected = {}, {}, {}
        periods = []
        target = request['residue']
        for d, profile, v_profile, e_profile in values:
            indices = [i for i in range(self.degree) if i*(n//d) % self.degree == target]
            v_count = sum(v_profile[i] for i in indices)
            e_count = sum(e_profile[i] for i in indices)
            words[d] = sum(profile[i] for i in indices)
            paired = d * v_count if d & 1 else d//2*(v_count + e_count)
            smaller = [p for p in exact if d % p == 0]
            exact[d] = (words[d] - sum(exact[p] for p in smaller)) % lift
            reflected[d] = (paired - sum(d//p*reflected[p] for p in smaller)) % lift
            double_orbit = (exact[d]+reflected[d]) % lift
            assert exact[d] % d == 0 and double_orbit % (2*d) == 0
            periods.append({'period': d, 'words': exact[d] % self.mod,
                            'necklaces': exact[d]//d % self.mod,
                            'bracelets': double_orbit//(2*d) % self.mod})
        mirrors = v_count % self.mod, e_count % self.mod
        return {'length': n, 'words': words[n] % self.mod,
                'necklaces': sum(row['necklaces'] for row in periods) % self.mod,
                'bracelets': sum(row['bracelets'] for row in periods) % self.mod, 'periods': periods,
                'fixed': {'rotations': [words[math.gcd(n, k)] % self.mod for k in request['rotations']],
                          'mirrors': [mirrors[k & 1] for k in request['mirrors']]}}

    def run(self, op, request):
        if op == 'orbit':
            return self.orbit(request)
        weights, edges = self.state
        value = request['value']
        if op == 'edge':
            u, v = request['u'], request['v']
            a, b = self.tau[u], self.tau[v]
            updated = [list(row) for row in edges]
            for i,j in ((u,v), (v,u), (a,b), (b,a)):
                updated[i][j] = value
            self.replace((weights, tuple(map(tuple, updated))))
        else:
            assert op == 'weight'
            color = request['color']
            updated = list(weights)
            updated[color] = updated[self.tau[color]] = value
            self.replace((tuple(updated), edges))
        return {'ok': True}



def separate_form(bits, q, linear, offset):
    """Separate the polynomial into unary and binary blocks over Z/2**bits."""
    whole = (1 << bits) - 1
    scale, free, uniform = 0, 0, None
    blocks = []
    while linear:
        active = [i for i in range(len(linear)) if linear[i] or any(q[i])]
        free += len(linear) - len(active)
        if not active:
            break
        if len(active) != len(linear):
            q = [[q[i][j] for j in active] for i in active]
            linear = [linear[i] for i in active]
        length = len(linear)
        union = 0
        for i in range(length):
            union |= linear[i]
            for j in range(i, length):
                union |= q[i][j]
        level = (union & -union).bit_length() - 1
        if level:
            scale += level
            q = [[x >> level for x in row] for row in q]
            linear = [x >> level for x in linear]
        modulus = 1 << (bits-scale)
        mask = modulus - 1
        pair = next(((i,j) for i in range(length) for j in range(i+1,length) if q[i][j]&1), None)
        if pair is None and any(x&1 for x in linear):
            # Without odd cross terms, parity determines the image modulo 2.
            # An odd derivative makes every compatible parity class lift uniformly.
            even_image = all((q[i][i] + linear[i]) % 2 == 0 for i in range(length))
            uniform = (length, scale + int(even_image))
            break
        if pair is None:
            i = next(i for i in range(length) if q[i][i]&1)
            remaining = [t for t in range(length) if t != i]
            unit = q[i][i]
            inverse = pow(unit, -1, modulus)
            shifts = [((x//2)*inverse) & mask for x in [linear[i]] + [q[i][t] for t in remaining]]
            h0 = shifts[0]
            offset -= (unit*h0*h0) << scale
            linear = [(linear[t]-2*unit*h0*shifts[k+1]) & mask for k,t in enumerate(remaining)]
            q = [[(q[s][t] - (1 if i==j else 2)*unit*shifts[i+1]*shifts[j+1]) & mask
                  for j,t in enumerate(remaining)] for i,s in enumerate(remaining)]
            blocks.append((scale, 1, unit & 7))
        else:
            i, j = pair
            remaining = [t for t in range(length) if t not in pair]
            a, b, c = q[i][i], q[i][j], q[j][j]
            inv = pow(4*a*c-b*b, -1, modulus)
            shifts = []
            for x,y in [(linear[i],linear[j])] + [(q[i][t],q[j][t]) for t in remaining]:
                shifts.append(((inv*(2*c*x-b*y))&mask, (inv*(2*a*y-b*x))&mask))

            def quadratic(u):
                x,y = shifts[u]
                return a*x*x + b*x*y + c*y*y

            def polar(u,v):
                x,y = shifts[u]
                s,t = shifts[v]
                return 2*a*x*s + b*(x*t+y*s) + 2*c*y*t

            offset -= quadratic(0) << scale
            linear = [(linear[t]-polar(0,k+1)) & mask for k,t in enumerate(remaining)]
            q = [[(q[s][t] - (quadratic(i+1) if i==j else polar(i+1,j+1))) & mask
                  for j,t in enumerate(remaining)] for i,s in enumerate(remaining)]
            blocks.append((scale, 2, -1 if a&c&1 else 1))
    return offset & whole, blocks, free, uniform


def root_shift(coefs, shift):
    """Multiply by the indicated power of a primitive eighth root of unity."""
    result = [0,0,0,0]
    for i, value in enumerate(coefs):
        j = (i + shift) & 7
        result[j & 3] += value if j < 4 else -value
    return result


def quadratic_count(bits, matrix, linear, offset, target):
    dimension = len(linear)
    constant, blocks, free, uniform = separate_form(bits, matrix, linear, offset)
    difference = (target - constant) & ((1<<bits)-1)
    if uniform:
        count, valuation = uniform
        free += count
        last = min(bits, valuation)
    else:
        last = bits
    numerator = 1 << (bits * dimension)
    # Group additive characters by exact order. Unary sums use only eighth
    # roots, so the odd units at higher orders collapse into eight residues.
    for order in range(1, last+1):
        fold = max(0, order-3)
        if difference & ((1<<fold)-1):
            continue
        exponent = bits*free
        sign = 1
        phases = []
        for scale, kind, unit in blocks:
            effective = order-scale
            if effective <= 0:
                exponent += kind*bits
            elif kind == 2:
                exponent += 2*bits-effective
                if unit < 0 and effective&1:
                    sign = -sign
            elif effective == 1:
                break
            elif effective&1:
                exponent += bits-(effective-1)//2
                phases.append((unit, False))
            else:
                exponent += bits-effective//2
                phases.append((2*unit, True))
        else:
            trace = [0,0,0,0]
            phase = difference >> fold if order >= 3 else difference << (3-order)
            for odd in range(1, 1<<min(order,3), 2):
                polynomial = [1,0,0,0]
                for power, add_identity in phases:
                    shifted = root_shift(polynomial, odd*power)
                    polynomial = [x+y for x,y in zip(polynomial, shifted)] if add_identity else shifted
                for i, value in enumerate(root_shift(polynomial, -phase*odd)):
                    trace[i] += value
            assert trace[1:] == [0,0,0]
            numerator += sign * (trace[0] << (exponent+fold))
    assert numerator >= 0 and numerator % (1<<bits) == 0
    return numerator >> bits


class Dyadic(Module):
    def __init__(self, request):
        self.bits = request['bits']
        self.dimension = request['variables']
        self.mask = (1<<self.bits)-1
        q = request['q']
        matrix = tuple(tuple(q[min(i,j)][max(i,j)] & self.mask for j in range(self.dimension))
                       for i in range(self.dimension))
        super().__init__((matrix, tuple(x & self.mask for x in request['linear']),
                          request['constant'] & self.mask))

    def count(self, target, locks):
        tag = target, tuple(map(tuple, locks))
        old = self.cache.get(tag)
        if old is not None:
            return old
        q,b,c = self.state
        base = [value for _,value in locks]
        active = [i for i,(r,_) in enumerate(locks) if r < self.bits]
        c += sum((b[i]+q[i][i]*x)*x for i,x in enumerate(base))
        c += sum(q[i][j]*x*base[j] for i,x in enumerate(base) for j in range(i+1,len(base)))
        linear = []
        matrix = []
        for i in active:
            ri = locks[i][0]
            derivative = b[i]+2*q[i][i]*base[i]+sum(q[i][j]*x for j,x in enumerate(base) if j != i)
            linear.append((derivative<<ri)&self.mask)
            matrix.append([(q[i][j] << (ri+locks[j][0])) & self.mask for j in active])
        raw = quadratic_count(self.bits, matrix, linear, c, target)
        redundant = sum(locks[i][0] for i in active)
        assert raw % (1<<redundant) == 0
        return remember(self.cache, tag, raw>>redundant, 1024)

    def solve(self, request):
        locks = [list(lock) for lock in request['locks']]
        target = request['target']
        count = self.count(target, locks)
        witness = None
        if count and request['witness']:
            for bit in range(self.bits):
                for pair in locks:
                    if pair[0] > bit:
                        continue
                    pair[0] = bit+1
                    if self.count(target, locks) == 0:
                        pair[1] |= 1<<bit
            values = [a for _,a in locks]
            width = (self.bits+7)//8
            raw = b'DYAD1'+bytes([self.dimension,self.bits])+b''.join(x.to_bytes(width,'little') for x in values)
            witness = {'values': values, 'sha256': hashlib.sha256(raw).hexdigest()}
        return {'possible': count>0, 'count': count, 'witness': witness}

    def run(self, op, request):
        if op == 'solve':
            return self.solve(request)
        q, b, c = self.state
        value = request['value'] & self.mask
        if op == 'quad':
            i, j = request['i'], request['j']
            mutable = list(map(list, q))
            mutable[i][j] = mutable[j][i] = value
            q = tuple(map(tuple, mutable))
        elif op == 'linear':
            i = request['i']
            b = b[:i] + (value,) + b[i+1:]
        else:
            assert op == 'constant'
            c = value
        self.replace((q,b,c))
        return {'ok': True}


def main():
    constructors = {'euler': Euler, 'ink': Ink, 'mirror': Mirror, 'dyadic': Dyadic}
    modules = {}
    output = sys.stdout.buffer
    for raw in sys.stdin.buffer:
        if not raw.strip():
            continue
        command = json.loads(raw)
        module, op = command['op'].split('_',1)
        if op == 'init':
            modules[module] = constructors[module](command)
            reply = {'ok': True}
        else:
            reply = modules[module].command(op, command)
        output.write(json.dumps(reply, separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
