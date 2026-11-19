"""PENTA: five independent states on one NDJSON stream."""
import hashlib
import heapq
import json
import math
import sys
from array import array
from collections import deque

OK = {'ok': True}
IMPOSSIBLE = {'possible': False}


def divisors(factors):
    out = [1]
    for prime, power in factors:
        powers = [prime**i for i in range(power+1)]
        out = [d*p for d in out for p in powers]
    return sorted(out)


def put(cache, key, value, limit):
    if len(cache) >= limit:
        cache.pop(next(iter(cache)))
    cache[key] = value
    return value


class StateMachine:
    def __init__(self, data):
        self.data = data
        self.slots = {}
        self.cache = {}

    def update(self, data):
        if data != self.data:
            self.data = data
            self.cache.clear()

    def request(self, op, cmd):
        if op == 'save':
            self.slots[cmd['slot']] = self.data
        elif op == 'load':
            self.update(self.slots[cmd['slot']])
        else:
            return self.command(op, cmd)
        return OK


# Euler inventories: exact arborescence counts followed by factorial quotients.

def laplacian_minor(graph, degree, root):
    vertices = [u for u,d in enumerate(degree) if u != root and (d or any(row[u] for row in graph))]
    minor = [[degree[u]-graph[u][u] if u == v else -graph[u][v] for v in vertices] for u in vertices]
    order = len(minor)
    previous = 1
    for i in range(order-1):
        diagonal = minor[i][i]
        # Nonsingular reduced Laplacians have positive principal minors.
        if not diagonal:
            return 0
        for j in range(i+1,order):
            row = minor[j]
            factor = row[i]
            for k in range(i+1,order):
                row[k] = (diagonal*row[k]-factor*minor[i][k])//previous
        previous = diagonal
    return minor[-1][-1] if order else 1


class PrimePower:
    def __init__(self, prime, power):
        self.prime = prime
        self.mod = prime**power
        self.lift = self.mod
        self.precision = power
        bound = prime
        while bound <= 200000:
            self.lift *= prime
            self.precision += 1
            bound *= prime
        self.units = array('Q', [1])
        self.valuations = array('I', [0])

    def prepare(self, limit):
        valuations, units = self.valuations, self.units
        unit, exponent = units[-1], valuations[-1]
        prime, lift = self.prime, self.lift
        for i in range(len(units),limit+1):
            term = i
            while term % prime == 0:
                term //= prime
                exponent += 1
            unit = unit*term % lift
            valuations.append(exponent)
            units.append(unit)

    def quotient(self, leading, top, bottom):
        if not leading:
            return 0
        val = self.valuations
        self.prepare(max(max(top,default=0),max(bottom,default=0)))
        exponent = sum(val[x] for x in top)-sum(val[x] for x in bottom)
        while leading % self.prime == 0:
            leading //= self.prime
            exponent += 1
        assert exponent >= 0
        if exponent >= self.precision:
            return 0
        modulus = self.lift
        units = self.units
        numerator, denominator = leading%modulus, 1
        for x in top:
            numerator = numerator*units[x] % modulus
        for x in bottom:
            denominator = denominator*units[x] % modulus
        return numerator*pow(denominator,-1,modulus)*pow(self.prime,exponent,modulus) % modulus

    def divide_period(self, value, period):
        multiplier = 1
        while period % self.prime == 0:
            multiplier *= self.prime
            period //= self.prime
        assert value % multiplier == 0
        return value//multiplier*pow(period,-1,self.mod) % self.mod


def least_euler_word(graph, root):
    adjacency = [[(v,n) for v,n in reversed(list(enumerate(row))) if n] for row in graph]
    # Consume the numerically first neighbor and splice cycles on backtracking.
    stack, backward = [root], bytearray()
    while stack:
        arcs = adjacency[stack[-1]]
        if not arcs:
            backward.append(stack.pop())
            continue
        neighbor,count = arcs[-1]
        if count == 1:
            arcs.pop()
        else:
            arcs[-1] = neighbor,count-1
        stack.append(neighbor)
    backward.reverse()
    return bytes(backward[:-1])


class Euler(StateMachine):
    def __init__(self, cmd):
        super().__init__(tuple(map(tuple,cmd['edges'])))
        self.powers = [PrimePower(*p) for p in cmd['mod_factors']]
        self.mod = math.prod(p.mod for p in self.powers)
        self.crt = []
        for p in self.powers:
            q = self.mod//p.mod
            self.crt.append(q*pow(q,-1,p.mod))

    def join(self, values):
        return sum(x*c for x,c in zip(values,self.crt)) % self.mod

    def prepare_count(self, factors):
        graph = self.data
        degrees = list(map(sum,graph))
        n = sum(degrees)
        active = [u for u,d in enumerate(degrees) if d]
        tree = laplacian_minor(graph,degrees,active[0])
        values = [x for row in graph for x in row if x]
        divides, exact, rows = {}, {}, []
        for r in reversed(divisors(factors)):
            p = n//r
            top = [degrees[u]//r-1 for u in active]
            bottom = [x//r for x in values]
            leading = p*(tree//r**(len(active)-1))
            count = [q.quotient(leading,top,bottom) for q in self.powers]
            multiples = [exact[s] for s in exact if s%r == 0]
            roots = [(value-sum(row[i] for row in multiples))%q.lift
                     for i,(value,q) in enumerate(zip(count,self.powers))]
            exact[r] = roots
            divides[r] = self.join(count)
            rows.append({'period':p,'words':self.join(roots),
                         'necklaces':self.join(q.divide_period(x,p) for q,x in zip(self.powers,roots))})
        core = {'possible':bool(tree),'length':n,'words':divides[1],
                'necklaces':sum(row['necklaces'] for row in rows)%self.mod,'periods':rows}
        word = least_euler_word(graph,active[0]) if tree else None
        digest = None if word is None else hashlib.sha256(b'EULER1'+n.to_bytes(8,'little')+word).hexdigest()
        return core, divides, word, digest

    def prefix_count(self, prefix, core):
        if not prefix:
            return core['words']
        if len(prefix)>core['length'] or not core['possible']:
            return 0
        key = tuple(prefix)
        if key in self.cache:
            return self.cache[key]
        graph = list(map(list,self.data))
        for u,v in zip(prefix,prefix[1:]):
            if not graph[u][v]:
                return 0
            graph[u][v] -= 1
        end = prefix[0]
        degree = list(map(sum,graph))
        minor = laplacian_minor(graph,degree,end)
        top = [degree[end]]+[d-1 for u,d in enumerate(degree) if u!=end and d]
        bottom = [x for row in graph for x in row if x]
        self.cache[key] = value = self.join(p.quotient(minor,top,bottom) for p in self.powers)
        return value

    def command(self, op, cmd):
        if op == 'cycle':
            if cmd['delta']:
                graph = list(map(list,self.data))
                path = cmd['vertices']
                for u,v in zip(path,path[1:]+path[:1]):
                    graph[u][v] += cmd['delta']
                self.update(tuple(map(tuple,graph)))
            return OK
        assert op == 'count'
        if 'count' not in self.cache:
            self.cache['count'] = self.prepare_count(cmd['gcd_factors'])
        result,rotations,word,digest = self.cache['count']
        n = result['length']
        return dict(result,
                    fixed_rotations=[rotations.get(n//math.gcd(n,k),0) for k in cmd['rotations']],
                    prefix_counts=[self.prefix_count(p,result) for p in cmd['prefixes']],
                    witness=None if word is None else {'sha256':digest,
                                                         'at':[word[i] if i<n else None for i in cmd['at']]})


# Weighted grammar: (cost, size) shortest hyperpaths for the witness,
# then leaf elimination in the minimum-cost dependency graph for counting.

class Trees:
    def __init__(self):
        self.nodes = []
        self.index = {}

    def add(self, key, size):
        if key not in self.index:
            rid,kids = key
            digest = hashlib.sha256(b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(kids)])
                                    +b''.join(self.nodes[k][3] for k in kids)).digest()
            self.index[key] = len(self.nodes)
            self.nodes.append((rid,kids,size,digest))
        return self.index[key]

    def precedes(self, a, b):
        while a[0] == b[0]:
            for u,v in zip(a[1],b[1]):
                if u != v:
                    a,b = self.nodes[u],self.nodes[v]
                    break
            else:
                return False
        return a[0] < b[0]

    def kth(self, tree, position):
        if position >= self.nodes[tree][2]:
            return None
        while position:
            position -= 1
            for child in self.nodes[tree][1]:
                sz = self.nodes[child][2]
                if position < sz:
                    tree = child
                    break
                position -= sz
        return self.nodes[tree][0]


class ChartShape:
    """The nonterminal hyperedges depend on length and enabled rules only."""
    def __init__(self, nonterminals, rules, enabled, end):
        intervals = [(a,b) for a in range(end+1) for b in range(a,end+1)]
        index = {pair:i for i,pair in enumerate(intervals)}
        span = len(index)
        cells = nonterminals*span
        splits = [[(index[a,t],index[t,b]) for t in range(a,b+1)] for a,b in intervals]
        epsilon = [index[i,i] for i in range(end+1)]
        users = [[] for _ in range(cells)]
        heads,left,right,rids,price_index,arity = [],[],[],[],[],[]
        literals,empty = [],[]

        def add(head,a,b,rid,rule):
            n = len(heads)
            heads.append(head)
            left.append(a)
            right.append(b)
            rids.append(rid)
            price_index.append(rule)
            arity.append(int(a>=0)+int(b>=0))
            if a<0:
                empty.append(n)
            else:
                users[a].append(n)
                if b>=0:
                    users[b].append(n)

        for i,(rid,parent,rhs) in enumerate(rules):
            if not enabled[i]:
                continue
            u = parent*span
            if not rhs:
                for cell in epsilon:
                    add(u+cell,-1,-1,rid,i)
            elif isinstance(rhs[0],str):
                literals.append((u,rhs[0],rid,i))
            elif len(rhs) == 1:
                v = rhs[0]*span
                for cell in range(span):
                    add(u+cell,v+cell,-1,rid,i)
            else:
                v,w = rhs[0]*span,rhs[1]*span
                for cell, options in enumerate(splits):
                    for a,b in options:
                        add(u+cell,v+a,w+b,rid,i)
        self.cells,self.span,self.full = cells,span,index[0,end]
        self.literal_cells = [index[i,i+1] for i in range(end)]
        self.literals,self.empty = literals,empty
        self.heads,self.left,self.right,self.rids = heads,left,right,rids
        self.price_index,self.arity,self.users = price_index,arity,users


class Chart:
    def __init__(self, shape, values, word, modulus):
        cells = shape.cells
        heads,left,right,rids,users = shape.heads,shape.left,shape.right,shape.rids,shape.users
        costs = [price for price,_ in values]
        prices = [costs[i] for i in shape.price_index]
        missing = shape.arity[:]
        sizes = [1]*len(heads)
        best, keys, root = [None]*cells,[None]*cells,[-1]*cells
        heap = []
        trees = Trees()

        def offer(u, price, size, key):
            proposed = price,size
            if best[u] is None or proposed < best[u]:
                best[u],keys[u] = proposed,key
                heapq.heappush(heap,(price,size,u))
            elif proposed == best[u] and trees.precedes(key,keys[u]):
                keys[u] = key

        for n in shape.empty:
            offer(heads[n],prices[n],1,(rids[n],()))
        matches = {letter:[] for letter in 'abcd'}
        for letter,cell in zip(word,shape.literal_cells):
            matches[letter].append(cell)
        terminals = []
        for u,letter,rid,i in shape.literals:
            price = costs[i]
            for t in matches[letter]:
                terminals.append((u+t,price))
                offer(u+t,price,1,(rid,()))

        while heap:
            price,size,u = heapq.heappop(heap)
            if root[u]>=0 or best[u]!=(price,size):
                continue
            root[u] = trees.add(keys[u],size)
            for p in users[u]:
                missing[p] -= 1
                prices[p] += price
                v = heads[p]
                if root[v]>=0:
                    continue
                sizes[p] += size
                if not missing[p]:
                    children = (root[left[p]],) if right[p]<0 else (root[left[p]],root[right[p]])
                    offer(v,prices[p],sizes[p],(rids[p],children))

        incoming = [[] for _ in range(cells)]
        productions = [[] for _ in range(cells)]
        terminal_ways = [0]*cells
        for u,cost in terminals:
            if cost==best[u][0]:
                terminal_ways[u] += 1
        need = [0]*cells
        for p,u in enumerate(heads):
            if missing[p] or prices[p] != best[u][0]:
                continue
            a,b = left[p],right[p]
            productions[u].append(p)
            if a>=0:
                incoming[a].append(u)
                need[u] += 1
            if b>=0:
                incoming[b].append(u)
                need[u] += 1
        ways = [None]*cells
        queue = deque(u for u in range(cells) if root[u]>=0 and not need[u])
        while queue:
            u = queue.popleft()
            total = terminal_ways[u]
            for p in productions[u]:
                a,b = left[p],right[p]
                total += 1 if a<0 else ways[a] if b<0 else ways[a]*ways[b]
            ways[u] = total%modulus
            for v in incoming[u]:
                need[v] -= 1
                if not need[v]:
                    queue.append(v)

        self.span, self.full = shape.span,shape.full
        self.best, self.root, self.trees, self.ways = best,root,trees,ways

    def answer(self, start, at):
        cell = start*self.span+self.full
        root = self.root[cell]
        if root<0:
            return IMPOSSIBLE
        price,size = self.best[cell]
        ways = self.ways[cell]
        return {'possible':True,'cost':price,'infinite':ways is None,'ways':ways,
                'witness':{'nodes':size,'sha256':self.trees.nodes[root][3].hex(),
                           'at':[self.trees.kth(root,i) for i in at]}}


class Ink(StateMachine):
    def __init__(self, cmd):
        rules = cmd['rules']
        super().__init__(tuple((r['cost'],r['enabled']) for r in rules))
        self.n, self.mod = cmd['nonterminals'],cmd['mod']
        self.rules = [(r['id'],r['lhs'],tuple(r['rhs'])) for r in rules]
        self.index = {r['id']:i for i,r in enumerate(rules)}
        self.shape_key = None
        self.shape = None

    def command(self, op, cmd):
        if op == 'parse':
            word = cmd['word']
            if word not in self.cache:
                enabled = tuple(on for _,on in self.data)
                key = len(word),enabled
                if key != self.shape_key:
                    self.shape = ChartShape(self.n,self.rules,enabled,len(word))
                    self.shape_key = key
                put(self.cache,word,Chart(self.shape,self.data,word,self.mod),3)
            return self.cache[word].answer(cmd['start'],cmd['at'])
        index = self.index[cmd['id']]
        price,enabled = self.data[index]
        revised = (cmd['cost'],enabled) if op=='weight' else (price,cmd['value'])
        self.update(self.data[:index]+(revised,)+self.data[index+1:])
        return OK



# Mirror: work in the cyclic coefficient ring R[z]/(z**q-1).
# A characteristic recurrence replaces matrix exponentiation per divisor.

class CyclicRing:
    def __init__(self, degree, modulus, fan_in):
        self.degree = degree
        self.modulus = modulus
        self.width = 2*modulus.bit_length()+(degree*fan_in).bit_length()+1
        self.digit = (1<<self.width)-1
        self.offset = self.width*degree
        self.low = (1<<self.offset)-1

    def unpack(self, value):
        return [(value>>(j*self.width))&self.digit for j in range(self.degree)]

    def pack(self, values):
        return sum((x%self.modulus)<<(j*self.width) for j,x in enumerate(values))

    def unit(self, power):
        return 1<<(self.width*(power%self.degree))

    def fold(self, number):
        number = (number&self.low)+(number>>self.offset)
        out = 0
        width,mask,mod = self.width,self.digit,self.modulus
        for j in range(self.degree):
            out |= ((number&mask)%mod)<<(j*width)
            number >>= width
        return out

    def square_weights(self, value):
        out = [0]*self.degree
        for j,x in enumerate(self.unpack(value)):
            out[2*j%self.degree] += x
        return self.pack(out)


class MirrorProfiles:
    def __init__(self, weights, adjacency, tau, q, modulus):
        n = len(weights)
        self.n = n
        ring = self.ring = CyclicRing(q,modulus,n)
        # All entries in A**i for i <= n have at most n**n walks.
        # This small auxiliary ring therefore retains exact trace coefficients.
        exact = CyclicRing(q,1<<32,n)
        transition = [[exact.unit(weights[j]) if adjacency[i][j] else 0
                       for j in range(n)] for i in range(n)]
        columns = list(zip(*transition))
        fixed = [i for i in range(n) if tau[i]==i]
        seam = [i for i in range(n) if adjacency[i][tau[i]]]
        mono = [ring.unit(w) for w in weights]
        both = [ring.unit(2*w) for w in weights]
        last = [ring.fold(sum(mono[j] for j in fixed if adjacency[i][j])) for i in range(n)]
        power = [[int(i==j) for j in range(n)] for i in range(n)]
        traces = []
        odd_pass, even_vertices, even_edges = [],[],[]
        for d in range(n+1):
            traces.append(exact.unpack(exact.fold(sum(power[i][i] for i in range(n)))))
            if d==n:
                break
            doubled = [[ring.square_weights(ring.pack(exact.unpack(x))) for x in row] for row in power]
            fixed_start = [ring.fold(sum(mono[i]*doubled[i][j] for i in fixed)) for j in range(n)]
            odd_pass.append(ring.fold(sum(fixed_start[j] for j in seam)))
            even_vertices.append(ring.fold(sum(x*y for x,y in zip(fixed_start,last))))
            even_edges.append(ring.fold(sum(both[i]*doubled[i][j] for i in seam for j in seam)))
            power = [[exact.fold(sum(x*y for x,y in zip(row,col))) for col in columns] for row in power]

        # Newton identities in integer cyclic polynomials recover det(tI-A)
        # before reducing coefficients modulo the query's lifted modulus.
        characteristic = [[1]+[0]*(q-1)]
        for i in range(1,n+1):
            values = [0]*q
            for j in range(1,i+1):
                for a,x in enumerate(characteristic[i-j]):
                    for b,y in enumerate(traces[j]):
                        values[(a+b)%q] -= x*y
            assert all(x%i==0 for x in values)
            characteristic.append([x//i for x in values])
        self.substitute = [ring.pack([-x for x in row]) for row in characteristic[:0:-1]]
        self.trace = [ring.pack(x) for x in traces[:-1]]
        self.mirror_seeds = odd_pass,even_vertices,even_edges
        self.remainders = {0:[1]+[0]*(n-1)}
        self.bits = [[0,1]+[0]*(n-2) if n>1 else self.substitute]

    def multiply(self, a, b):
        n, ring = self.n,self.ring
        products = [0]*(2*n-1)
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b):
                    products[i+j] += x*y
        products = list(map(ring.fold,products))
        for i in range(2*n-2,n-1,-1):
            value = products[i]
            if value:
                for j,c in enumerate(self.substitute,i-n):
                    if c:
                        products[j] = ring.fold(products[j]+value*c)
        return products[:n]

    def t_power(self, exponent):
        if exponent not in self.remainders:
            while len(self.bits)<exponent.bit_length():
                self.bits.append(self.multiply(self.bits[-1],self.bits[-1]))
            powers = [self.bits[j] for j in range(exponent.bit_length()) if exponent>>j&1]
            value = powers[0]
            for part in powers[1:]:
                value = self.multiply(value,part)
            self.remainders[exponent] = value
        return self.remainders[exponent]

    def dot(self, a, b):
        ring = self.ring
        return ring.unpack(ring.fold(sum(x*y for x,y in zip(a,b))))

    def profiles(self, d):
        words = self.dot(self.t_power(d),self.trace)
        half = (d-1)//2 if d&1 else d//2-1
        coeff = [self.ring.square_weights(x) for x in self.t_power(half)]
        if d&1:
            mirror = self.dot(coeff,self.mirror_seeds[0])
            return words,mirror,mirror
        return words,self.dot(coeff,self.mirror_seeds[1]),self.dot(coeff,self.mirror_seeds[2])


class Mirror(StateMachine):
    def __init__(self, cmd):
        super().__init__((tuple(cmd['weights']),tuple(map(tuple,cmd['edges']))))
        self.q,self.mod = cmd['inventory_mod'],cmd['mod']
        self.tau = tuple(cmd['mirror'])

    def orbit(self, cmd):
        key = tuple(map(tuple,cmd['factors']))
        if key not in self.cache:
            ds = divisors(key)
            n = ds[-1]
            weights,adj = self.data
            recurrence = MirrorProfiles(weights,adj,self.tau,self.q,2*n*self.mod)
            put(self.cache,key,[(d,*recurrence.profiles(d)) for d in ds],4)
        profiles = self.cache[key]
        n = profiles[-1][0]
        lift = 2*n*self.mod
        base,primitive,reflections = {},{},{}
        rows = []
        for d,words,vertex,edge in profiles:
            scale = n//d
            relevant = [r for r in range(self.q) if r*scale%self.q == cmd['residue']]
            base[d] = sum(words[r] for r in relevant)
            fixed_v = sum(vertex[r] for r in relevant)
            fixed_e = sum(edge[r] for r in relevant)
            sum_reflected = d*fixed_v if d&1 else d//2*(fixed_v+fixed_e)
            proper = [e for e in primitive if d%e==0]
            primitive[d] = (base[d]-sum(primitive[e] for e in proper))%lift
            reflections[d] = (sum_reflected-sum(d//e*reflections[e] for e in proper))%lift
            orbit_numerator = (primitive[d]+reflections[d])%lift
            assert primitive[d]%d==0 and orbit_numerator%(2*d)==0
            rows.append({'period':d,'words':primitive[d]%self.mod,
                         'necklaces':primitive[d]//d%self.mod,'bracelets':orbit_numerator//(2*d)%self.mod})
        mirrors = fixed_v,fixed_e
        return {'length':n,'words':base[n]%self.mod,'necklaces':sum(x['necklaces'] for x in rows)%self.mod,
                'bracelets':sum(x['bracelets'] for x in rows)%self.mod,'periods':rows,
                'fixed':{'rotations':[base[math.gcd(k,n)]%self.mod for k in cmd['rotations']],
                         'mirrors':[mirrors[k&1]%self.mod for k in cmd['mirrors']]}}

    def command(self, op, cmd):
        if op=='orbit':
            return self.orbit(cmd)
        weights,adj = self.data
        if op=='weight':
            weights = list(weights)
            i = cmd['color']
            weights[i] = weights[self.tau[i]] = cmd['value']
            self.update((tuple(weights),adj))
        else:
            assert op=='edge'
            u,v = cmd['u'],cmd['v']
            x,y = self.tau[u],self.tau[v]
            adjacency = list(map(list,adj))
            for a,b in ((u,v),(v,u),(x,y),(y,x)):
                adjacency[a][b] = cmd['value']
            self.update((weights,tuple(map(tuple,adjacency))))
        return OK


# Dyadic forms: decompose the polynomial into blocks at each 2-adic scale.
# Count fibers by exact Gauss sums in Z[zeta_8].

def diagonal_blocks(bits, quadratic, linear, constant):
    blocks = []
    scale = free = 0
    max_character = bits
    while linear:
        active = [i for i,x in enumerate(linear) if x or any(quadratic[i])]
        free += len(linear)-len(active)
        if not active:
            break
        if len(active) != len(linear):
            quadratic = [[quadratic[i][j] for j in active] for i in active]
            linear = [linear[i] for i in active]
        size = len(linear)
        content = 0
        for i in range(size):
            content |= linear[i]
            for j in range(i,size):
                content |= quadratic[i][j]
        common = (content&-content).bit_length()-1
        if common:
            scale += common
            quadratic = [[q>>common for q in row] for row in quadratic]
            linear = [v>>common for v in linear]
        mod = 1<<(bits-scale)
        mask = mod-1
        pair = next(((i,j) for i in range(size) for j in range(i+1,size) if quadratic[i][j]&1),None)
        if pair is None and any(v&1 for v in linear):
            # The derivative is odd on some coordinate. Every matching
            # parity class has a uniform image above its first bit.
            even_image = all((quadratic[i][i]+linear[i])&1==0 for i in range(size))
            free += size
            max_character = scale+int(even_image)
            break
        if pair is None:
            i = next(j for j in range(size) if quadratic[j][j]&1)
            survivors = [t for t in range(size) if t!=i]
            a = quadratic[i][i]
            inv = pow(a,-1,mod)
            shift = [(inv*(r//2))&mask for r in [linear[i]]+[quadratic[i][t] for t in survivors]]
            constant -= (a*shift[0]**2)<<scale
            linear = [(linear[t]-2*a*shift[0]*shift[j+1])&mask for j,t in enumerate(survivors)]
            quadratic = [[(quadratic[u][v]-a*shift[j+1]*shift[k+1]*(1 if j==k else 2))&mask
                          for k,v in enumerate(survivors)] for j,u in enumerate(survivors)]
            blocks.append((scale,1,a&7))
        else:
            i,j = pair
            survivors = [t for t in range(size) if t not in pair]
            a,b,c = quadratic[i][i],quadratic[i][j],quadratic[j][j]
            inv = pow(4*a*c-b*b,-1,mod)
            pairs = [(linear[i],linear[j])]+[(quadratic[i][t],quadratic[j][t]) for t in survivors]
            shifts = [((inv*(2*c*u-b*v))&mask,(inv*(2*a*v-b*u))&mask) for u,v in pairs]

            def value(index):
                x,y = shifts[index]
                return a*x*x+b*x*y+c*y*y

            def cross(r,s):
                x,y = shifts[r]
                u,v = shifts[s]
                return 2*a*x*u+b*(x*v+y*u)+2*c*y*v

            constant -= value(0)<<scale
            linear = [(linear[t]-cross(0,r+1))&mask for r,t in enumerate(survivors)]
            quadratic = [[(quadratic[u][v]-(value(r+1) if r==s else cross(r+1,s+1)))&mask
                          for s,v in enumerate(survivors)] for r,u in enumerate(survivors)]
            blocks.append((scale,2,-1 if a&c&1 else 1))
    return constant,free,max_character,blocks


def shift_eighth(values, exponent):
    out = [0]*4
    for j,x in enumerate(values):
        power = (j+exponent)&7
        out[power&3] = x if power<4 else -x
    return out


def quadratic_fiber(bits, q, b, c, target):
    dimension = len(b)
    offset,free,limit,blocks = diagonal_blocks(bits,q,b,c)
    delta = (target-offset)&((1<<bits)-1)
    numerator = 1<<(bits*dimension)
    for order in range(1,min(bits,limit)+1):
        repeated = max(0,order-3)
        if delta&((1<<repeated)-1):
            continue
        cells = []
        scalar = bits*free
        sign = 1
        for scale,rank,kind in blocks:
            effective = order-scale
            if effective<=0:
                scalar += bits*rank
            elif rank==2:
                scalar += 2*bits-effective
                if kind<0 and effective&1:
                    sign = -sign
            elif effective==1:
                break
            elif effective&1:
                scalar += bits-(effective-1)//2
                cells.append((kind,False))
            else:
                scalar += bits-effective//2
                cells.append((2*kind,True))
        else:
            powers = [0]*4
            phase = delta>>repeated if order>=3 else delta<<(3-order)
            for odd in range(1,1<<min(order,3),2):
                values = [1,0,0,0]
                for power,add_one in cells:
                    shifted = shift_eighth(values,odd*power)
                    values = [a+b for a,b in zip(values,shifted)] if add_one else shifted
                for j,x in enumerate(shift_eighth(values,-phase*odd)):
                    powers[j] += x
            assert powers[1:]==[0,0,0]
            numerator += sign*(powers[0]<<(scalar+repeated))
    assert numerator>=0 and numerator% (1<<bits)==0
    return numerator>>bits


class Dyadic(StateMachine):
    def __init__(self, cmd):
        self.d,self.k = cmd['variables'],cmd['bits']
        self.mask = (1<<self.k)-1
        q = cmd['q']
        symmetric = tuple(tuple(q[min(i,j)][max(i,j)]&self.mask for j in range(self.d))
                          for i in range(self.d))
        super().__init__((symmetric,tuple(x&self.mask for x in cmd['linear']),cmd['constant']&self.mask))

    def count(self, target, locks):
        key = target,tuple(map(tuple,locks))
        if key in self.cache:
            return self.cache[key]
        q,linear,c = self.data
        point = [a for r,a in locks]
        free = [i for i,(r,_) in enumerate(locks) if r<self.k]
        c += sum((linear[i]+q[i][i]*point[i])*point[i] for i in range(self.d))
        c += sum(q[i][j]*point[i]*point[j] for i in range(self.d) for j in range(i+1,self.d))
        matrix = [[(q[i][j]<<(locks[i][0]+locks[j][0]))&self.mask for j in free] for i in free]
        b = []
        for i in free:
            gradient = linear[i]+2*q[i][i]*point[i]+sum(q[i][j]*point[j] for j in range(self.d) if i!=j)
            b.append((gradient<<locks[i][0])&self.mask)
        multiplicity = sum(locks[i][0] for i in free)
        count = quadratic_fiber(self.k,matrix,b,c,target)
        assert count%(1<<multiplicity)==0
        return put(self.cache,key,count>>multiplicity,1024)

    def solve(self, cmd):
        locks = [lock[:] for lock in cmd['locks']]
        target = cmd['target']
        count = self.count(target,locks)
        witness = None
        if count and cmd['witness']:
            for bit in range(self.k):
                for requirement in locks:
                    if requirement[0]<=bit:
                        requirement[0] = bit+1
                        if not self.count(target,locks):
                            requirement[1] |= 1<<bit
            values = [a for r,a in locks]
            payload = b'DYAD1'+bytes([self.d,self.k])
            payload += b''.join(x.to_bytes((self.k+7)//8,'little') for x in values)
            witness = {'values':values,'sha256':hashlib.sha256(payload).hexdigest()}
        return {'possible':bool(count),'count':count,'witness':witness}

    def command(self, op, cmd):
        if op=='solve':
            return self.solve(cmd)
        q,b,c = self.data
        value = cmd['value']&self.mask
        if op=='quad':
            rows = list(map(list,q))
            i,j = cmd['i'],cmd['j']
            rows[i][j] = rows[j][i] = value
            q = tuple(map(tuple,rows))
        elif op=='linear':
            i = cmd['i']
            b = b[:i]+(value,)+b[i+1:]
        else:
            assert op=='constant'
            c = value
        self.update((q,b,c))
        return OK



# Tide: bounded maximum flows, epsilon scaling for costs, and zero reduced
# cost circulations for movement within the optimal face.

class FlowGraph:
    def __init__(self, size):
        self.adj = [[] for _ in range(size)]
        self.to = []
        self.cap = []

    def link(self, source, target, amount, reverse=0):
        arc = len(self.cap)
        self.adj[source].append(arc)
        self.adj[target].append(arc+1)
        self.to.extend((target,source))
        self.cap.extend((amount,reverse))
        return arc

    def send(self, source, sink, remaining):
        adj, to, cap = self.adj,self.to,self.cap
        total = 0
        while remaining:
            levels = [-1]*len(adj)
            levels[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for arc in adj[u]:
                    v = to[arc]
                    if cap[arc] and levels[v]<0:
                        levels[v] = levels[u]+1
                        queue.append(v)
            if levels[sink]<0:
                break
            head = [0]*len(adj)

            def dfs(u, limit):
                if u==sink:
                    return limit
                while head[u]<len(adj[u]):
                    arc = adj[u][head[u]]
                    v = to[arc]
                    if cap[arc] and levels[v]==levels[u]+1:
                        delta = dfs(v,min(cap[arc],limit))
                        if delta:
                            cap[arc] -= delta
                            cap[arc^1] += delta
                            return delta
                    head[u] += 1
                return 0

            while remaining:
                delta = dfs(source,remaining)
                if not delta:
                    break
                total += delta
                remaining -= delta
        return total


def feasible_tide(vertices, edges, bounds, balances):
    if sum(balances):
        return None
    graph = FlowGraph(vertices+2)
    changes = list(balances)
    handles = []
    flow = [lo for lo,hi in bounds]
    for i,(u,v) in enumerate(edges):
        lo,hi = bounds[i]
        if u!=v:
            changes[u] -= lo
            changes[v] += lo
            if hi>lo:
                handles.append((i,graph.link(u,v,hi-lo)))
    source,sink = vertices,vertices+1
    need = 0
    for u,amount in enumerate(changes):
        if amount>0:
            graph.link(source,u,amount)
            need += amount
        elif amount<0:
            graph.link(u,sink,-amount)
    if graph.send(source,sink,need)!=need:
        return None
    for i,arc in handles:
        flow[i] += graph.cap[arc^1]
    return flow


def scaled_tide(vertices, edges, bounds, prices, flow):
    residual = FlowGraph(vertices)
    handles = []
    cost = []
    for i,(u,v) in enumerate(edges):
        lo,hi = bounds[i]
        if u==v:
            flow[i] = hi if prices[i]<0 else lo
        elif hi>lo:
            handles.append((i,residual.link(u,v,hi-flow[i],flow[i]-lo)))
            weight = prices[i]*(vertices+1)
            cost.extend((weight,-weight))
    adj, to, cap = residual.adj,residual.to,residual.cap
    potential = [0]*vertices
    epsilon = 1<<max(map(abs,cost),default=0).bit_length()
    while epsilon>1:
        epsilon //= 2
        excess = [0]*vertices
        for arc,w in enumerate(cost):
            u,v = to[arc^1],to[arc]
            if cap[arc] and w+potential[u]-potential[v]<0:
                delta = cap[arc]
                cap[arc] = 0
                cap[arc^1] += delta
                excess[u] -= delta
                excess[v] += delta
        active = deque(u for u,x in enumerate(excess) if x>0)
        while active:
            u = active.popleft()
            while excess[u]>0:
                for arc in adj[u]:
                    v = to[arc]
                    if not cap[arc] or cost[arc]+potential[u]-potential[v]>=0:
                        continue
                    delta = min(cap[arc],excess[u])
                    cap[arc] -= delta
                    cap[arc^1] += delta
                    excess[u] -= delta
                    if excess[v]<=0<excess[v]+delta:
                        active.append(v)
                    excess[v] += delta
                    if excess[u]==0:
                        break
                else:
                    potential[u] = max(potential[to[a]]-cost[a]-epsilon for a in adj[u] if cap[a])
        assert not any(excess)
    # Reduced costs at least -1 after scaling imply no negative original
    # cycle: a simple cycle contains at most vertices edges.
    for i,arc in handles:
        flow[i] = bounds[i][0]+cap[arc^1]

    # Recover exactly feasible potentials for the zero-cost residual graph.
    distance = [0]*vertices
    for _ in range(vertices):
        changed = False
        for i,(u,v) in enumerate(edges):
            lo,hi = bounds[i]
            c = prices[i]
            if flow[i]<hi and distance[v]>distance[u]+c:
                distance[v] = distance[u]+c
                changed = True
            if flow[i]>lo and distance[u]>distance[v]-c:
                distance[u] = distance[v]-c
                changed = True
        if not changed:
            break
    else:
        raise AssertionError('negative residual cycle')
    return [prices[i]+distance[u]-distance[v]==0 for i,(u,v) in enumerate(edges)]


class OptimalFace:
    def __init__(self, vertices, edges, bounds, tight):
        self.vertices, self.edges, self.bounds = vertices,edges,bounds
        self.tight = tight
        self.arcs = [i for i,(u,v) in enumerate(edges) if u!=v and tight[i] and bounds[i][0]!=bounds[i][1]]

    def shift(self, flow, i, direction, first_unlocked=0, commit=False):
        if not self.tight[i]:
            return 0
        lo,hi = self.bounds[i]
        cap = (hi-flow[i]) if direction>0 else (flow[i]-lo)
        if not cap:
            return 0
        u,v = self.edges[i]
        if u==v:
            if commit:
                flow[i] += direction*cap
            return cap
        graph = FlowGraph(self.vertices)
        handles = []
        for other in self.arcs:
            if other<first_unlocked or other==i:
                continue
            x,y = self.edges[other]
            lower,upper = self.bounds[other]
            forward = upper-flow[other]
            index = graph.link(x,y,forward,flow[other]-lower)
            if commit:
                handles.append((other,index,forward))
        # The compensating flow is capped before augmentation. Any excess
        # on the return path would change vertex balances.
        value = graph.send(v,u,cap) if direction>0 else graph.send(u,v,cap)
        if commit:
            for other,index,forward in handles:
                flow[other] += forward-graph.cap[index]
            flow[i] += direction*value
        return value


class Tide(StateMachine):
    def __init__(self, cmd):
        edges = sorted(cmd['edges'],key=lambda row:row['id'])
        self.vertices = cmd['vertices']
        self.ids = [e['id'] for e in edges]
        self.index = {label:i for i,label in enumerate(self.ids)}
        self.edges = [(e['u'],e['v']) for e in edges]
        super().__init__((tuple((e['lo'],e['hi'],e['cost']) for e in edges),tuple(cmd['balance'])))

    def prepare(self, pins):
        table,balance = self.data
        bounds = [(lo,hi) for lo,hi,c in table]
        prices = [c for lo,hi,c in table]
        for label,value in pins:
            i = self.index[label]
            lo,hi = bounds[i]
            if not lo<=value<=hi:
                return None
            bounds[i] = value,value
        flow = feasible_tide(self.vertices,self.edges,bounds,balance)
        if flow is None:
            return None
        tight = scaled_tide(self.vertices,self.edges,bounds,prices,flow)
        face = OptimalFace(self.vertices,self.edges,bounds,tight)
        for i in range(len(flow)):
            face.shift(flow,i,-1,i+1,True)
        return sum(f*c for f,c in zip(flow,prices)),flow,face,{}

    def solve(self, cmd):
        pins = tuple(sorted(map(tuple,cmd['pins'])))
        if pins not in self.cache:
            put(self.cache,pins,self.prepare(pins),8)
        info = self.cache[pins]
        if info is None:
            return IMPOSSIBLE
        cost,flow,face,ranges = info
        requested = []
        for label in cmd['inspect']:
            i = self.index[label]
            if i not in ranges:
                ranges[i] = [flow[i]-face.shift(flow,i,-1),flow[i]+face.shift(flow,i,1)]
            requested.append(ranges[i])
        return {'possible':True,'cost':cost,'flow':list(zip(self.ids,flow)),'ranges':requested}

    def command(self, op, cmd):
        if op=='solve':
            return self.solve(cmd)
        assert op=='patch'
        table,balance = map(list,self.data)
        for label,lo,hi,c in cmd['edges']:
            table[self.index[label]] = lo,hi,c
        for u,value in cmd['balance']:
            balance[u] = value
        self.update((tuple(table),tuple(balance)))
        return OK


def main():
    constructors = {'euler':Euler,'ink':Ink,'mirror':Mirror,'dyadic':Dyadic,'tide':Tide}
    active = {}
    output = sys.stdout.buffer
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        cmd = json.loads(line)
        name,op = cmd['op'].split('_',1)
        if op=='init':
            active[name] = constructors[name](cmd)
            response = OK
        else:
            response = active[name].request(op,cmd)
        output.write(json.dumps(response,separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
