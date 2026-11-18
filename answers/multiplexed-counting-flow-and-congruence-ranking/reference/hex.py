"""HEX: six independent state machines sharing one NDJSON stream."""
import hashlib
import heapq
import json
import math
import sys
from array import array
from collections import deque


OK = {'ok': True}
NO = {'possible': False}


def all_divisors(factors):
    result = [1]
    for p,e in factors:
        powers = [p**i for i in range(e+1)]
        result = [x*d for x in result for d in powers]
    return sorted(result)


def store(cache, key, value, limit):
    if len(cache)>=limit:
        del cache[next(iter(cache))]
    cache[key] = value
    return value


class Machine:
    def __init__(self, state):
        self.state = state
        self.slots = {}
        self.cache = {}

    def set_state(self, state):
        if state!=self.state:
            self.state = state
            self.cache.clear()

    def run(self, op, message):
        if op=='save':
            self.slots[message['slot']] = self.state
        elif op=='load':
            self.set_state(self.slots[message['slot']])
        else:
            return self.command(op,message)
        return OK


# PRISM: each suffix image is diagonal in a suitable p-primary row basis.
# The order of a new column modulo the next image gives the step size in
# that coordinate and the number of equal-sized branches.

def reduce_image(matrix, basis, p, q):
    size = len(matrix)
    width = len(matrix[0])
    diagonal = [q]*size
    for k in range(size):
        divisor = q
        row_at = col_at = -1
        for i in range(k,size):
            row = matrix[i]
            for j in range(k,width):
                x = row[j]
                if x % divisor:
                    d = 1
                    while x%(d*p)==0:
                        d *= p
                    divisor = d
                    row_at,col_at = i,j
                    if d==1:
                        break
            if divisor==1:
                break
        if row_at<0:
            break
        if row_at!=k:
            matrix[k],matrix[row_at] = matrix[row_at],matrix[k]
            basis[k],basis[row_at] = basis[row_at],basis[k]
        if col_at!=k:
            for row in matrix:
                row[k],row[col_at] = row[col_at],row[k]
        pivot = matrix[k]
        inv = pow(pivot[k]//divisor,-1,q)
        diagonal[k] = divisor
        if inv!=1:
            pivot = matrix[k] = [x*inv%q for x in pivot]
            basis[k] = [x*inv%q for x in basis[k]]
        change = basis[k]
        for i in range(k+1,size):
            other = matrix[i]
            multiple = other[k]//divisor
            if multiple:
                other[k] = 0
                for j in range(k+1,width):
                    other[j] = (other[j]-multiple*pivot[j])%q
                basis[i] = [(x-multiple*y)%q for x,y in zip(basis[i],change)]
        # Column elimination affects only the pivot row.
        pivot[k+1:] = [0]*(width-k-1)
    return diagonal


def sparse(indices, coefficients, modulus):
    return [(i,c%modulus) for i,c in zip(indices,coefficients) if c%modulus]


def evaluate(coefficients, values):
    return sum(weight*values[i] for i,weight in coefficients)


def primary_data(p, exponent, rows, columns):
    q = p**exponent
    local = []
    for i,modulus in enumerate(rows):
        order = 1
        while modulus%p==0:
            modulus //= p
            order *= p
        if order>1:
            local.append((i,q//order))
    count = len(local)
    projections = [None]*len(columns)
    if not count:
        return [],projections
    indices = [i for i,_ in local]
    # The initial diagonal basis includes the lift of each row modulus to q.
    basis = [[weight if i==j else 0 for j in range(count)]
             for i,(_,weight) in enumerate(local)]
    diag = [q]*count
    for j in range(len(columns)-1,-1,-1):
        col = [columns[j][i] for i in indices]
        image = [sum(a*b for a,b in zip(transform,col))%q for transform in basis]
        candidates = [d//math.gcd(d,x) for d,x in zip(diag,image)]
        best = max(range(count),key=candidates.__getitem__)
        step = candidates[best]
        if step==1:
            continue
        modulus = diag[best]
        divisor = modulus//step
        inv = pow(image[best]//divisor,-1,step)
        projections[j] = step,modulus,divisor,inv,sparse(indices,basis[best],modulus)
        matrix = [[(diag[i]%q if i==t else 0) for t in range(count)]+[image[i]]
                  for i in range(count)]
        diag = reduce_image(matrix,basis,p,q)
    constraints = [(d,sparse(indices,row,d)) for d,row in zip(diag,basis) if d>1]
    return constraints,projections


class Fibers:
    def __init__(self, factors, domains, rows, columns):
        self.columns = columns
        self.n = len(domains)
        self.constraints = []
        per_column = [[] for _ in domains]
        for p,e in factors:
            constraints,projections = primary_data(p,e,rows,columns)
            self.constraints.extend(constraints)
            for i,projection in enumerate(projections):
                if projection:
                    per_column[i].append(projection)
        self.steps, self.rules = [],[]
        for domain,components in zip(domains,per_column):
            step = math.prod(part[0] for part in components)
            assert domain%step==0
            self.steps.append(step)
            rules = []
            for order,modulus,divisor,inv,row in components:
                comp = step//order
                crt = comp*pow(comp,-1,order)
                rules.append((modulus,divisor,crt*inv,row))
            self.rules.append(rules)
        self.sizes = [1]*(self.n+1)
        for i in range(self.n-1,-1,-1):
            self.sizes[i] = self.sizes[i+1]*(domains[i]//self.steps[i])

    def residue(self, i, rhs):
        result = 0
        # The residual target is known reachable in this suffix. The
        # dominant congruence therefore implies the others at that prime.
        for modulus,divisor,weight,row in self.rules[i]:
            value = evaluate(row,rhs)%modulus
            assert value%divisor==0
            result += value//divisor*weight
        return result%self.steps[i]

    def remove(self, i, value, rhs):
        if value==0:
            return rhs
        return [x-value*y for x,y in zip(rhs,self.columns[i])]

    def constrain(self, prefix, rhs):
        if any(evaluate(row,rhs)%mod for mod,row in self.constraints):
            return None
        for i,x in enumerate(prefix):
            if x%self.steps[i]!=self.residue(i,rhs):
                return None
            rhs = self.remove(i,x,rhs)
        return rhs

    def select(self, prefix, rhs, index):
        start = len(prefix)
        if index>=self.sizes[start]:
            return None
        values = prefix[:]
        for i in range(start,self.n):
            branch,index = divmod(index,self.sizes[i+1])
            chosen = self.residue(i,rhs)+branch*self.steps[i]
            values.append(chosen)
            rhs = self.remove(i,chosen,rhs)
        return values

    def rank(self, prefix, rhs, probe):
        length = len(prefix)
        head = probe[:length]
        if head!=prefix:
            return {'before':self.sizes[length] if head>prefix else 0,'member':False}
        before = 0
        for i in range(length,self.n):
            step = self.steps[i]
            first = self.residue(i,rhs)
            x = probe[i]
            before += ((x-first+step-1)//step)*self.sizes[i+1]
            if x%step!=first:
                return {'before':before,'member':False}
            rhs = self.remove(i,x,rhs)
        return {'before':before,'member':True}


class Prism(Machine):
    def __init__(self, command):
        rows = command['rows']
        self.factors = command['mod_factors']
        self.domains = command['domains']
        self.moduli = [r['mod'] for r in rows]
        self.index = {r['id']:i for i,r in enumerate(rows)}
        self.key = None
        super().__init__(tuple((tuple(a%r['mod'] for a in r['a']),r['rhs']%r['mod'],r['enabled']) for r in rows))

    def command(self, op, command):
        if op=='query':
            active = [i for i,(_,_,enabled) in enumerate(self.state) if enabled and self.moduli[i]>1]
            key = tuple((i,self.state[i][0]) for i in active)
            if key!=self.key:
                columns = [[self.state[i][0][j] for i in active]
                           for j in range(len(self.domains))]
                self.fibers = Fibers(self.factors,self.domains,[self.moduli[i] for i in active],columns)
                self.key = key
            model = self.fibers
            prefix = command['prefix']
            target = model.constrain(prefix,[self.state[i][1] for i in active])
            if target is None:
                return {'count':0,'at':[None]*len(command['at']),
                        'probes':[{'before':0,'member':False} for _ in command['probes']]}
            return {'count':model.sizes[len(prefix)],'at':[model.select(prefix,target,k) for k in command['at']],
                    'probes':[model.rank(prefix,target,v) for v in command['probes']]}
        i = self.index[command['id']]
        mod = self.moduli[i]
        coefficients,rhs,enabled = self.state[i]
        if op=='row':
            coefficients = tuple(a%mod for a in command['a'])
        if op in ('row','rhs'):
            rhs = command['rhs']%mod
        else:
            assert op=='enable'
            enabled = command['value']
        self.set_state(self.state[:i]+((coefficients,rhs,enabled),)+self.state[i+1:])
        return OK



# Euler: matrix-tree factorial formulas, including virtual end vertices
# created by consuming a prefix, with exact divisions at each prime.

def tree_count(graph, out_degree, root):
    kept = [i for i,degree in enumerate(out_degree)
            if i!=root and (degree or any(row[i] for row in graph))]
    matrix = [[out_degree[i]-graph[i][i] if i==j else -graph[i][j] for j in kept] for i in kept]
    divisor = 1
    for k in range(len(matrix)-1):
        row = matrix[k]
        lead = row[k]
        if lead==0:
            return 0
        for i in range(k+1,len(matrix)):
            below = matrix[i]
            for j in range(k+1,len(matrix)):
                below[j] = (lead*below[j]-below[k]*row[j])//divisor
        divisor = lead
    return matrix[-1][-1] if matrix else 1


class Factorials:
    def __init__(self, prime, exponent):
        self.prime = prime
        self.output = prime**exponent
        self.max_v = exponent
        p = prime
        while p<=200000:
            p *= prime
            self.max_v += 1
        self.mod = prime**self.max_v
        self.units = array('Q',[1])
        self.valuations = array('I',[0])

    def extend(self, target):
        prime,mod = self.prime,self.mod
        units,vals = self.units,self.valuations
        unit,v = units[-1],vals[-1]
        for i in range(len(units),target+1):
            while i%prime==0:
                i //= prime
                v += 1
            unit = unit*i%mod
            units.append(unit)
            vals.append(v)

    def quotient(self, factor, numerator, denominator):
        if not factor:
            return 0
        self.extend(max(max(numerator,default=0),max(denominator,default=0)))
        values,units = self.valuations,self.units
        prime,mod = self.prime,self.mod
        valuation = sum(values[n] for n in numerator)-sum(values[d] for d in denominator)
        while factor%prime==0:
            factor //= prime
            valuation += 1
        if valuation>=self.max_v:
            return 0
        assert valuation>=0
        a,b = factor%mod,1
        for n in numerator:
            a = a*units[n]%mod
        for n in denominator:
            b = b*units[n]%mod
        return a*pow(b,-1,mod)*prime**valuation%mod

    def orbit(self, residue, period):
        prime = self.prime
        power = 1
        while period%prime==0:
            period //= prime
            power *= prime
        assert residue%power==0
        return (residue//power)*pow(period,-1,self.output)%self.output


class Euler(Machine):
    def __init__(self, command):
        super().__init__(tuple(map(tuple,command['edges'])))
        self.primes = [Factorials(p,e) for p,e in command['mod_factors']]
        self.mod = math.prod(p.output for p in self.primes)
        self.crt = []
        for p in self.primes:
            comp = self.mod//p.output
            self.crt.append(comp*pow(comp,-1,p.output))

    def combine(self, residues):
        return sum(a*b for a,b in zip(residues,self.crt))%self.mod

    @staticmethod
    def witness(graph, start):
        adj = [[(u,c) for u,c in reversed(list(enumerate(row))) if c] for row in graph]
        stack = [start]
        word = bytearray()
        while stack:
            edges = adj[stack[-1]]
            if not edges:
                word.append(stack.pop())
                continue
            v,capacity = edges[-1]
            if capacity==1:
                edges.pop()
            else:
                edges[-1] = v,capacity-1
            stack.append(v)
        word.reverse()
        return bytes(word[:-1])

    def prepare(self, factors):
        graph = self.state
        out = [sum(row) for row in graph]
        size = sum(out)
        active = [u for u,d in enumerate(out) if d]
        tree = tree_count(graph,out,active[0])
        entries = [c for row in graph for c in row if c]
        exact,rotations,periods = {},{},[]
        for r in reversed(all_divisors(factors)):
            period = size//r
            a = [out[u]//r-1 for u in active]
            b = [c//r for c in entries]
            total = [p.quotient(period*(tree//r**(len(active)-1)),a,b) for p in self.primes]
            rotations[r] = self.combine(total)
            multiples = [row for k,row in exact.items() if k%r==0]
            row = [(x-sum(y[i] for y in multiples))%p.mod for i,(x,p) in enumerate(zip(total,self.primes))]
            exact[r] = row
            periods.append({'period':period,'words':self.combine(row),
                            'necklaces':self.combine(p.orbit(v,period) for p,v in zip(self.primes,row))})
        digest = word = None
        if tree:
            word = self.witness(graph,active[0])
            digest = hashlib.sha256(b'EULER1'+size.to_bytes(8,'little')+word).hexdigest()
        metrics = {'possible':bool(tree),'length':size,'words':rotations[1],
                   'necklaces':sum(row['necklaces'] for row in periods)%self.mod,'periods':periods}
        return metrics,rotations,word,digest

    def completions(self, prefix, metrics):
        if not prefix:
            return metrics['words']
        if len(prefix)>metrics['length'] or not metrics['possible']:
            return 0
        code = tuple(prefix)
        if code not in self.cache:
            graph = list(map(list,self.state))
            for a,b in zip(prefix,prefix[1:]):
                if not graph[a][b]:
                    return 0
                graph[a][b] -= 1
            end = prefix[0]
            out = list(map(sum,graph))
            tree = tree_count(graph,out,end)
            numerator = [out[end]]+[d-1 for u,d in enumerate(out) if u!=end and d]
            denominator = [x for row in graph for x in row if x]
            self.cache[code] = self.combine(p.quotient(tree,numerator,denominator) for p in self.primes)
        return self.cache[code]

    def command(self, op, command):
        if op=='cycle':
            tour,delta = command['vertices'],command['delta']
            if delta:
                graph = list(map(list,self.state))
                for a,b in zip(tour,tour[1:]+tour[:1]):
                    graph[a][b] += delta
                self.set_state(tuple(map(tuple,graph)))
            return OK
        assert op=='count'
        if 'base' not in self.cache:
            self.cache['base'] = self.prepare(command['gcd_factors'])
        metrics,rotations,word,digest = self.cache['base']
        n = metrics['length']
        return dict(metrics,
                    fixed_rotations=[rotations.get(n//math.gcd(n,k),0) for k in command['rotations']],
                    prefix_counts=[self.completions(p,metrics) for p in command['prefixes']],
                    witness=None if word is None else {'sha256':digest,
                                                         'at':[word[k] if k<n else None for k in command['at']]})


# Ink: solve the minimum (cost, size) hyperpaths. Count across all
# minimum-cost alternatives, including rules outside a least-size witness.

class Forest:
    def __init__(self):
        self.nodes = []
        self.keys = {}

    def identify(self, key, size):
        if key not in self.keys:
            rule,kids = key
            image = b'DERIVE1'+rule.to_bytes(4,'little')+bytes([len(kids)])
            image += b''.join(self.nodes[i][3] for i in kids)
            self.keys[key] = len(self.nodes)
            self.nodes.append((rule,kids,size,hashlib.sha256(image).digest()))
        return self.keys[key]

    def earlier(self, first, second):
        while first[0]==second[0]:
            for a,b in zip(first[1],second[1]):
                if a!=b:
                    first,second = self.nodes[a],self.nodes[b]
                    break
            else:
                return False
        return first[0]<second[0]

    def select(self, root, index):
        if index>=self.nodes[root][2]:
            return None
        while index:
            index -= 1
            for child in self.nodes[root][1]:
                size = self.nodes[child][2]
                if index<size:
                    root = child
                    break
                index -= size
        return self.nodes[root][0]


class GrammarShape:
    def __init__(self, count, rules, length):
        spans = [(i,j) for i in range(length+1) for j in range(i,length+1)]
        lookup = {x:i for i,x in enumerate(spans)}
        width = len(spans)
        cuts = [[(lookup[i,m],lookup[m,j]) for m in range(i,j+1)] for i,j in spans]
        epsilon = [lookup[i,i] for i in range(length+1)]
        self.single = [lookup[i,i+1] for i in range(length)]
        self.target = lookup[0,length]
        self.vertices,self.width = count*width,width
        self.reverse = [[] for _ in range(self.vertices)]
        self.rules = rules
        self.head,self.left,self.right,self.production,self.arity = [],[],[],[],[]
        self.empty,self.terminals = [],[]
        for r,(rid,parent,children) in enumerate(rules):
            shift = parent*width
            if not children:
                for i in epsilon:
                    self.empty.append((shift+i,r))
            elif isinstance(children[0],str):
                self.terminals.append((shift,children[0],r))
            elif len(children)==1:
                a = children[0]*width
                for i in range(width):
                    self.add(shift+i,a+i,-1,r)
            else:
                a,b = (u*width for u in children)
                for i,options in enumerate(cuts):
                    for u,v in options:
                        self.add(shift+i,a+u,b+v,r)

    def add(self, head, left, right, rule):
        arc = len(self.head)
        self.head.append(head)
        self.left.append(left)
        self.right.append(right)
        self.production.append(rule)
        self.arity.append(2 if right>=0 else 1)
        self.reverse[left].append(arc)
        if right>=0:
            self.reverse[right].append(arc)


class GrammarAnswer:
    def __init__(self, shape, state, word, modulus):
        self.width,self.target = shape.width,shape.target
        n = shape.vertices
        labels = [r[0] for r in shape.rules]
        prices = [cost if enabled else None for cost,enabled in state]
        price = [prices[r] for r in shape.production]
        support = shape.arity[:]
        sizes = [1]*len(price)
        best,choice,root = [None]*n,[None]*n,[-1]*n
        trees = Forest()
        heap = []
        terminal = []

        def submit(u, cost, size, key):
            next_pair = cost,size
            if best[u] is None or next_pair<best[u]:
                best[u],choice[u] = next_pair,key
                heapq.heappush(heap,(cost,size,u))
            elif next_pair==best[u] and trees.earlier(key,choice[u]):
                choice[u] = key

        def leaf(u,r):
            cost = prices[r]
            if cost is not None:
                terminal.append((u,cost))
                submit(u,cost,1,(labels[r],()))

        for u,r in shape.empty:
            leaf(u,r)
        for shift,letter,r in shape.terminals:
            for c,span in zip(word,shape.single):
                if letter==c:
                    leaf(shift+span,r)
        head,left,right,production = shape.head,shape.left,shape.right,shape.production
        while heap:
            cost,size,u = heapq.heappop(heap)
            if root[u]>=0 or best[u]!=(cost,size):
                continue
            root[u] = trees.identify(choice[u],size)
            for arc in shape.reverse[u]:
                old = price[arc]
                if old is None:
                    continue
                price[arc] = old+cost
                support[arc] -= 1
                v = head[arc]
                if root[v]>=0:
                    continue
                sizes[arc] += size
                if support[arc]==0:
                    kids = (root[left[arc]],)
                    if right[arc]>=0:
                        kids += (root[right[arc]],)
                    submit(v,price[arc],sizes[arc],(labels[production[arc]],kids))

        # Eliminate leaves from the graph of all optimal alternatives.
        # A productive item left over can reach a cycle and pump it.
        leaf_ways,needed = [0]*n,[0]*n
        for u,cost in terminal:
            if best[u][0]==cost:
                leaf_ways[u] += 1
        parents,alternatives = [[] for _ in range(n)],[[] for _ in range(n)]
        for i,u in enumerate(head):
            if support[i] or price[i]!=best[u][0]:
                continue
            a,b = left[i],right[i]
            parents[a].append(u)
            needed[u] += 1
            if b>=0:
                parents[b].append(u)
                needed[u] += 1
            alternatives[u].append(i)
        ways = [None]*n
        queue = deque(i for i in range(n) if root[i]>=0 and not needed[i])
        while queue:
            u = queue.popleft()
            total = leaf_ways[u]
            for i in alternatives[u]:
                a,b = left[i],right[i]
                total += ways[a] if b<0 else ways[a]*ways[b]
            ways[u] = total%modulus
            for v in parents[u]:
                needed[v] -= 1
                if not needed[v]:
                    queue.append(v)
        self.best,self.root,self.trees,self.ways = best,root,trees,ways

    def answer(self, start, positions):
        u = start*self.width+self.target
        root = self.root[u]
        if root<0:
            return NO
        cost,size = self.best[u]
        return {'possible':True,'cost':cost,'infinite':self.ways[u] is None,'ways':self.ways[u],
                'witness':{'nodes':size,'sha256':self.trees.nodes[root][3].hex(),
                           'at':[self.trees.select(root,k) for k in positions]}}


class Ink(Machine):
    def __init__(self, command):
        entries = command['rules']
        super().__init__(tuple((r['cost'],r['enabled']) for r in entries))
        self.rules = [(r['id'],r['lhs'],tuple(r['rhs'])) for r in entries]
        self.n,self.mod = command['nonterminals'],command['mod']
        self.lookup = {r['id']:i for i,r in enumerate(entries)}
        self.shape_length = None

    def command(self, op, command):
        if op=='parse':
            word = command['word']
            if word not in self.cache:
                if len(word)!=self.shape_length:
                    self.shape = GrammarShape(self.n,self.rules,len(word))
                    self.shape_length = len(word)
                store(self.cache,word,GrammarAnswer(self.shape,self.state,word,self.mod),3)
            return self.cache[word].answer(command['start'],command['at'])
        index = self.lookup[command['id']]
        cost,enabled = self.state[index]
        pair = (command['cost'],enabled) if op=='weight' else (cost,command['value'])
        self.set_state(self.state[:index]+(pair,)+self.state[index+1:])
        return OK



# Mirror: represent inventory profiles as cyclic polynomials. The traces
# and reflection boundary walks are scalar functionals of powers of one
# matrix. A characteristic recurrence evaluates them at large lengths.

class Cyclic:
    def __init__(self, degree, modulus, width):
        self.degree,self.modulus = degree,modulus
        self.bits = 2*modulus.bit_length()+(degree*width).bit_length()+1
        self.digit = (1<<self.bits)-1
        self.split = degree*self.bits
        self.low = (1<<self.split)-1

    def coeffs(self, number):
        return [(number>>(self.bits*i))&self.digit for i in range(self.degree)]

    def from_coeffs(self, values):
        return sum((a%self.modulus)<<(self.bits*i) for i,a in enumerate(values))

    def mono(self, exponent):
        return 1<<(self.bits*(exponent%self.degree))

    def normalize(self, number):
        number = (number&self.low)+(number>>self.split)
        out = 0
        bits,mask,mod = self.bits,self.digit,self.modulus
        for i in range(self.degree):
            out |= ((number&mask)%mod)<<(i*bits)
            number >>= bits
        return out

    def double(self, number):
        values = [0]*self.degree
        for i,x in enumerate(self.coeffs(number)):
            values[2*i%self.degree] += x
        return self.from_coeffs(values)

    def dot(self, a,b):
        return self.normalize(sum(x*y for x,y in zip(a,b)))


class Transfer:
    def __init__(self, weights, allowed, mirror, degree, modulus):
        n = len(weights)
        self.n = n
        ring = self.ring = Cyclic(degree,modulus,n)
        small = Cyclic(degree,1<<32,n)
        a = [[small.mono(weights[j]) if allowed[i][j] else 0
              for j in range(n)] for i in range(n)]
        columns = list(zip(*a))
        power = [[int(i==j) for j in range(n)] for i in range(n)]
        fixed = [i for i in range(n) if mirror[i]==i]
        join = [i for i in range(n) if allowed[i][mirror[i]]]
        endpoint = [ring.mono(w) for w in weights]
        paired = [ring.mono(2*w) for w in weights]
        last = [ring.normalize(sum(endpoint[j] for j in fixed if allowed[i][j])) for i in range(n)]
        traces = []
        odd,even_at_vertex,even_at_edge = [],[],[]
        for k in range(n+1):
            # Through A**n the exact coefficients are bounded by n**n.
            traces.append(small.coeffs(small.normalize(sum(power[i][i] for i in range(n)))))
            if k==n:
                break
            twice = [[ring.double(ring.from_coeffs(small.coeffs(v))) for v in row] for row in power]
            start = [ring.normalize(sum(endpoint[i]*twice[i][j] for i in fixed)) for j in range(n)]
            odd.append(ring.normalize(sum(start[j] for j in join)))
            even_at_vertex.append(ring.dot(start,last))
            even_at_edge.append(ring.normalize(sum(paired[i]*twice[i][j] for i in join for j in join)))
            power = [[small.dot(row,col) for col in columns] for row in power]
        char = [[1]+[0]*(degree-1)]
        # Newton identities before reduction preserve the integer division.
        for k in range(1,n+1):
            values = [0]*degree
            for i in range(1,k+1):
                for r,x in enumerate(char[k-i]):
                    for s,y in enumerate(traces[i]):
                        values[(r+s)%degree] -= x*y
            assert all(x%k==0 for x in values)
            char.append([x//k for x in values])
        self.substitution = [ring.from_coeffs([-x for x in c]) for c in char[:0:-1]]
        self.trace_seed = [ring.from_coeffs(c) for c in traces[:-1]]
        self.boundary = odd,even_at_vertex,even_at_edge
        self.powers = [([0,1]+[0]*(n-2)) if n>1 else self.substitution]
        self.lookup = {0:[1]+[0]*(n-1)}

    def multiply(self, a,b):
        ring,n = self.ring,self.n
        out = [0]*(2*n-1)
        for i,u in enumerate(a):
            if u:
                for j,v in enumerate(b):
                    out[i+j] += u*v
        out = list(map(ring.normalize,out))
        for i in range(len(out)-1,n-1,-1):
            if out[i]:
                for j,c in enumerate(self.substitution,i-n):
                    if c:
                        out[j] = ring.normalize(out[j]+out[i]*c)
        return out[:n]

    def p(self, exponent):
        if exponent not in self.lookup:
            while len(self.powers)<exponent.bit_length():
                self.powers.append(self.multiply(self.powers[-1],self.powers[-1]))
            value = None
            while exponent:
                low = exponent&-exponent
                a = self.powers[low.bit_length()-1]
                value = a if value is None else self.multiply(value,a)
                exponent ^= low
            return value
        return self.lookup[exponent]

    def cached_power(self, exponent):
        if exponent not in self.lookup:
            self.lookup[exponent] = self.p(exponent)
        return self.lookup[exponent]

    def profiles(self, length):
        ring = self.ring
        words = ring.coeffs(ring.dot(self.cached_power(length),self.trace_seed))
        exponent = (length-1)//2 if length&1 else length//2-1
        weights = [ring.double(x) for x in self.cached_power(exponent)]
        if length&1:
            odd = ring.coeffs(ring.dot(weights,self.boundary[0]))
            return words,odd,odd
        return (words,ring.coeffs(ring.dot(weights,self.boundary[1])),
                ring.coeffs(ring.dot(weights,self.boundary[2])))


class Mirror(Machine):
    def __init__(self, command):
        super().__init__((tuple(command['weights']),tuple(map(tuple,command['edges']))))
        self.q,self.mod = command['inventory_mod'],command['mod']
        self.tau = command['mirror']

    def orbit(self, command):
        factors = tuple(map(tuple,command['factors']))
        if factors not in self.cache:
            periods = all_divisors(factors)
            weights,edges = self.state
            transfer = Transfer(weights,edges,self.tau,self.q,2*periods[-1]*self.mod)
            store(self.cache,factors,[(d,*transfer.profiles(d)) for d in periods],4)
        data = self.cache[factors]
        n = data[-1][0]
        lift = 2*n*self.mod
        rotations,primitive,reflections = {},{},{}
        rows = []
        for d,words,vertices,edges in data:
            valid = [j for j in range(self.q) if j*(n//d)%self.q==command['residue']]
            rotations[d] = sum(words[i] for i in valid)
            fixed0 = sum(vertices[i] for i in valid)
            fixed1 = sum(edges[i] for i in valid)
            axes = d*fixed0 if d&1 else d//2*(fixed0+fixed1)
            divisors = [p for p in primitive if d%p==0]
            rooted = primitive[d] = (rotations[d]-sum(primitive[p] for p in divisors))%lift
            reflections[d] = (axes-sum(d//p*reflections[p] for p in divisors))%lift
            folded = (rooted+reflections[d])%lift
            assert rooted%d==0 and folded%(2*d)==0
            rows.append({'period':d,'words':rooted%self.mod,'necklaces':rooted//d%self.mod,
                         'bracelets':folded//(2*d)%self.mod})
        return {'length':n,'words':rotations[n]%self.mod,
                'necklaces':sum(x['necklaces'] for x in rows)%self.mod,
                'bracelets':sum(x['bracelets'] for x in rows)%self.mod,'periods':rows,
                'fixed':{'rotations':[rotations[math.gcd(x,n)]%self.mod for x in command['rotations']],
                         'mirrors':[(fixed1 if x&1 else fixed0)%self.mod for x in command['mirrors']]}}

    def command(self, op, command):
        if op=='orbit':
            return self.orbit(command)
        weights,graph = self.state
        value = command['value']
        if op=='weight':
            i = command['color']
            weights = list(weights)
            weights[i] = weights[self.tau[i]] = value
            self.set_state((tuple(weights),graph))
        else:
            assert op=='edge'
            u,v = command['u'],command['v']
            a,b = self.tau[u],self.tau[v]
            graph = list(map(list,graph))
            for i,j in ((u,v),(v,u),(a,b),(b,a)):
                graph[i][j] = value
            self.set_state((weights,tuple(map(tuple,graph))))
        return OK


# Dyadic: complete squares and split binary blocks over odd determinants.
# Character sums in the eighth-root ring give exact counts.

def decompose(bits, a, b, constant):
    free = scale = 0
    limit = bits
    blocks = []
    while b:
        active = [i for i in range(len(b)) if b[i] or any(a[i])]
        free += len(b)-len(active)
        if not active:
            break
        if len(active)<len(b):
            a = [[a[i][j] for j in active] for i in active]
            b = [b[i] for i in active]
        n = len(b)
        seen = 0
        for i in range(n):
            seen |= b[i]
            for j in range(i,n):
                seen |= a[i][j]
        power = (seen&-seen).bit_length()-1
        if power:
            scale += power
            a = [[x>>power for x in row] for row in a]
            b = [x>>power for x in b]
        mod = 1<<(bits-scale)
        mask = mod-1
        pair = next(((i,j) for i in range(n) for j in range(i+1,n) if a[i][j]&1),None)
        if pair is None and any(x&1 for x in b):
            free += n
            uniform_even = all((a[i][i]+b[i])%2==0 for i in range(n))
            limit = scale+int(uniform_even)
            break
        if pair is None:
            i = next(i for i in range(n) if a[i][i]&1)
            trailing = [j for j in range(n) if j!=i]
            coefficient = a[i][i]
            inverse = pow(coefficient,-1,mod)
            offset = (b[i]//2*inverse)&mask
            shifts = [(a[i][j]//2*inverse)&mask for j in trailing]
            constant -= (coefficient*offset*offset)<<scale
            b = [(b[j]-2*coefficient*offset*u)&mask for j,u in zip(trailing,shifts)]
            a = [[(a[i][j]-coefficient*shifts[r]*shifts[s]*(1 if r==s else 2))&mask
                  for s,j in enumerate(trailing)] for r,i in enumerate(trailing)]
            blocks.append((scale,1,coefficient&7))
        else:
            i,j = pair
            trailing = [x for x in range(n) if x not in pair]
            p,q,r = a[i][i],a[i][j],a[j][j]
            inverse = pow(4*p*r-q*q,-1,mod)

            def shift(x,y):
                return (inverse*(2*r*x-q*y))&mask,(inverse*(2*p*y-q*x))&mask

            def quadratic(vector):
                x,y = vector
                return p*x*x+q*x*y+r*y*y

            def cross(first,second):
                x,y = first
                u,v = second
                return 2*p*x*u+q*(x*v+y*u)+2*r*y*v

            offset = shift(b[i],b[j])
            shifts = [shift(a[i][u],a[j][u]) for u in trailing]
            constant -= quadratic(offset)<<scale
            b = [(b[u]-cross(offset,z))&mask for u,z in zip(trailing,shifts)]
            a = [[(a[u][v]-(quadratic(shifts[i]) if i==j else cross(shifts[i],shifts[j])))&mask
                  for j,v in enumerate(trailing)] for i,u in enumerate(trailing)]
            blocks.append((scale,2,-1 if p&r&1 else 1))
    return constant,free,limit,blocks


def shift_root(coefs, phase):
    result = [0]*4
    for i,x in enumerate(coefs):
        slot = (i+phase)&7
        result[slot&3] = x if slot<4 else -x
    return result


def dyadic_count(bits, a, b, constant,target):
    n = len(b)
    constant,free,limit,blocks = decompose(bits,a,b,constant)
    rhs = (target-constant)&((1<<bits)-1)
    total = 1<<(bits*n)
    for order in range(1,min(limit,bits)+1):
        duplicates = max(0,order-3)
        if rhs & ((1<<duplicates)-1):
            continue
        terms = []
        power = bits*free
        sign = 1
        for scale,arity,key in blocks:
            degree = order-scale
            if degree<=0:
                power += arity*bits
            elif arity==2:
                power += 2*bits-degree
                if key<0 and degree&1:
                    sign = -sign
            elif degree==1:
                break
            elif degree&1:
                power += bits-(degree-1)//2
                terms.append((key,False))
            else:
                power += bits-degree//2
                terms.append((2*key,True))
        else:
            character = rhs>>duplicates if order>=3 else rhs<<(3-order)
            vector = [0]*4
            for k in range(1,1<<min(3,order),2):
                part = [1,0,0,0]
                for phase,mixed in terms:
                    shifted = shift_root(part,k*phase)
                    part = [u+v for u,v in zip(part,shifted)] if mixed else shifted
                for i,x in enumerate(shift_root(part,-k*character)):
                    vector[i] += x
            assert vector[1:]==[0,0,0]
            total += sign*(vector[0]<<(power+duplicates))
    assert total>=0 and total%(1<<bits)==0
    return total>>bits


class Dyadic(Machine):
    def __init__(self, command):
        self.n,self.bits = command['variables'],command['bits']
        self.mask = (1<<self.bits)-1
        a = command['q']
        a = tuple(tuple(a[min(i,j)][max(i,j)]&self.mask for j in range(self.n)) for i in range(self.n))
        super().__init__((a,tuple(x&self.mask for x in command['linear']),command['constant']&self.mask))

    def count(self, target, locks):
        key = target,tuple(map(tuple,locks))
        if key in self.cache:
            return self.cache[key]
        a,b,c = self.state
        x = [value for _,value in locks]
        shift = [level for level,_ in locks]
        free = [i for i in range(self.n) if shift[i]<self.bits]
        c += sum((b[i]+a[i][i]*x[i])*x[i] for i in range(self.n))
        c += sum(a[i][j]*x[i]*x[j] for i in range(self.n) for j in range(i+1,self.n))
        q = [[(a[i][j]<<(shift[i]+shift[j]))&self.mask for j in free] for i in free]
        g = []
        for i in free:
            derivative = b[i]+2*a[i][i]*x[i]+sum(a[i][j]*x[j] for j in range(self.n) if j!=i)
            g.append((derivative<<shift[i])&self.mask)
        duplications = sum(shift[i] for i in free)
        count = dyadic_count(self.bits,q,g,c,target)
        assert count%(1<<duplications)==0
        return store(self.cache,key,count>>duplications,1024)

    def solve(self, command):
        locks = [pair[:] for pair in command['locks']]
        target = command['target']
        count = self.count(target,locks)
        witness = None
        if count and command['witness']:
            for bit in range(self.bits):
                for p in locks:
                    if p[0]<=bit:
                        p[0] = bit+1
                        if not self.count(target,locks):
                            p[1] |= 1<<bit
            values = [v for _,v in locks]
            width = (self.bits+7)//8
            payload = b'DYAD1'+bytes([self.n,self.bits])+b''.join(x.to_bytes(width,'little') for x in values)
            witness = {'values':values,'sha256':hashlib.sha256(payload).hexdigest()}
        return {'possible':bool(count),'count':count,'witness':witness}

    def command(self, op, command):
        if op=='solve':
            return self.solve(command)
        a,b,c = self.state
        value = command['value']&self.mask
        if op=='quad':
            i,j = command['i'],command['j']
            matrix = list(map(list,a))
            matrix[i][j] = matrix[j][i] = value
            a = tuple(map(tuple,matrix))
        elif op=='linear':
            i = command['i']
            b = b[:i]+(value,)+b[i+1:]
        else:
            assert op=='constant'
            c = value
        self.set_state((a,b,c))
        return OK



# Tide: retain both residual directions throughout epsilon scaling.
# Lexicographic movements keep previously fixed edges out of the network.

class Residual:
    def __init__(self, n):
        self.neighbors = [[] for _ in range(n)]
        self.to,self.capacity = [],[]

    def add(self, u,v,forward,backward=0):
        edge = len(self.to)
        self.neighbors[u].append(edge)
        self.neighbors[v].append(edge^1)
        self.to.extend((v,u))
        self.capacity.extend((forward,backward))
        return edge

    def max_flow(self, start, end, limit):
        n = len(self.neighbors)
        arcs, to, cap = self.neighbors,self.to,self.capacity
        total = 0
        while total<limit:
            dist = [-1]*n
            dist[start] = 0
            queue = deque([start])
            while queue:
                u = queue.popleft()
                for e in arcs[u]:
                    v = to[e]
                    if cap[e] and dist[v]<0:
                        dist[v] = dist[u]+1
                        queue.append(v)
            if dist[end]<0:
                break
            next_arc = [0]*n

            def assign(u, remaining):
                if u==end:
                    return remaining
                bag = arcs[u]
                while next_arc[u]<len(bag):
                    e = bag[next_arc[u]]
                    v = to[e]
                    if cap[e] and dist[v]==dist[u]+1:
                        got = assign(v,min(remaining,cap[e]))
                        if got:
                            cap[e] -= got
                            cap[e^1] += got
                            return got
                    next_arc[u] += 1
                return 0

            while total<limit:
                sent = assign(start,limit-total)
                if not sent:
                    break
                total += sent
        return total


def feasible_flow(n, arcs, limits,balance):
    if sum(balance):
        return None
    graph = Residual(n+2)
    demand = list(balance)
    handles = []
    flow = [lo for lo,_ in limits]
    for i,((u,v),(lo,hi)) in enumerate(zip(arcs,limits)):
        if u!=v:
            demand[u] -= lo
            demand[v] += lo
            if hi>lo:
                handles.append((i,graph.add(u,v,hi-lo)))
    expected = 0
    for u,x in enumerate(demand):
        if x>0:
            graph.add(n,u,x)
            expected += x
        elif x<0:
            graph.add(u,n+1,-x)
    if graph.max_flow(n,n+1,expected)!=expected:
        return None
    for i,e in handles:
        flow[i] += graph.capacity[e^1]
    return flow


def optimize_flow(n, arcs, limits, costs, flow):
    residual = Residual(n)
    scaled = []
    handles = []
    for i,((u,v),(lo,hi),cost) in enumerate(zip(arcs,limits,costs)):
        if u==v:
            flow[i] = hi if cost<0 else lo
        elif lo<hi:
            handles.append((i,residual.add(u,v,hi-flow[i],flow[i]-lo)))
            scaled.extend((cost*(n+1),-cost*(n+1)))
    potential = [0]*n
    gain = 1<<max(map(abs,scaled),default=0).bit_length()
    to,cap,adj = residual.to,residual.capacity,residual.neighbors
    while gain>1:
        gain //= 2
        excess = [0]*n
        for a,weight in enumerate(scaled):
            u,v = to[a^1],to[a]
            if cap[a] and weight+potential[u]-potential[v]<0:
                amount = cap[a]
                cap[a] = 0
                cap[a^1] += amount
                excess[u] -= amount
                excess[v] += amount
        queue = deque(i for i,b in enumerate(excess) if b>0)
        while queue:
            u = queue.popleft()
            while excess[u]>0:
                for a in adj[u]:
                    v = to[a]
                    if not cap[a] or scaled[a]+potential[u]-potential[v]>=0:
                        continue
                    amount = min(cap[a],excess[u])
                    cap[a] -= amount
                    cap[a^1] += amount
                    excess[u] -= amount
                    if excess[v]<=0<excess[v]+amount:
                        queue.append(v)
                    excess[v] += amount
                    if excess[u]==0:
                        break
                else:
                    potential[u] = max(potential[to[e]]-scaled[e]-gain for e in adj[u] if cap[e])
        assert not any(excess)
    # At scale one, no simple residual cycle (length at most n) having
    # integer-scaled weight a multiple of n+1 can have negative weight.
    for i,a in handles:
        flow[i] = limits[i][0]+cap[a^1]
    distance = [0]*n
    for _ in range(n):
        revised = False
        for i,((u,v),(lo,hi),weight) in enumerate(zip(arcs,limits,costs)):
            if flow[i]<hi and distance[v]>distance[u]+weight:
                distance[v] = distance[u]+weight
                revised = True
            if flow[i]>lo and distance[u]>distance[v]-weight:
                distance[u] = distance[v]-weight
                revised = True
        if not revised:
            break
    else:
        raise AssertionError('residual optimum')
    return [c+distance[u]-distance[v]==0 for (u,v),c in zip(arcs,costs)]


class FlowFace:
    def __init__(self, n, arcs, limits,tight):
        self.n,self.arcs,self.limits,self.tight = n,arcs,limits,tight
        self.routes = [i for i,(u,v) in enumerate(arcs) if u!=v and tight[i] and limits[i][0]<limits[i][1]]

    def move(self, flow, position, sign, blocked=0, commit=False):
        if not self.tight[position]:
            return 0
        lo,hi = self.limits[position]
        size = hi-flow[position] if sign>0 else flow[position]-lo
        if not size:
            return 0
        u,v = self.arcs[position]
        if u==v:
            if commit:
                flow[position] += sign*size
            return size
        graph = Residual(self.n)
        handles = []
        for i in self.routes:
            if i==position or i<blocked:
                continue
            a,b = self.arcs[i]
            low,high = self.limits[i]
            initial = high-flow[i]
            e = graph.add(a,b,initial,flow[i]-low)
            if commit:
                handles.append((i,e,initial))
        start,end = (v,u) if sign>0 else (u,v)
        # The return path must carry exactly as much as the chosen arc.
        sent = graph.max_flow(start,end,size)
        if commit:
            for i,e,initial in handles:
                flow[i] += initial-graph.capacity[e]
            flow[position] += sign*sent
        return sent


class Tide(Machine):
    def __init__(self, command):
        edges = sorted(command['edges'],key=lambda e:e['id'])
        self.n = command['vertices']
        self.ids = [e['id'] for e in edges]
        self.lookup = {v:i for i,v in enumerate(self.ids)}
        self.arcs = [(e['u'],e['v']) for e in edges]
        super().__init__((tuple((e['lo'],e['hi'],e['cost']) for e in edges),tuple(command['balance'])))

    def optimum(self, pins):
        rows,balance = self.state
        costs = [row[2] for row in rows]
        limits = [row[:2] for row in rows]
        for i,value in pins:
            e = self.lookup[i]
            lo,hi = limits[e]
            if not lo<=value<=hi:
                return None
            limits[e] = value,value
        flow = feasible_flow(self.n,self.arcs,limits,balance)
        if flow is None:
            return None
        tight = optimize_flow(self.n,self.arcs,limits,costs,flow)
        face = FlowFace(self.n,self.arcs,limits,tight)
        for i in range(len(flow)):
            face.move(flow,i,-1,i+1,True)
        return sum(a*b for a,b in zip(costs,flow)),flow,face,{}

    def solve(self, command):
        key = tuple(sorted(map(tuple,command['pins'])))
        if key not in self.cache:
            store(self.cache,key,self.optimum(key),8)
        result = self.cache[key]
        if result is None:
            return NO
        cost,flow,face,known = result
        ranges = []
        for k in command['inspect']:
            i = self.lookup[k]
            if i not in known:
                known[i] = [flow[i]-face.move(flow,i,-1),flow[i]+face.move(flow,i,1)]
            ranges.append(known[i])
        return {'possible':True,'cost':cost,'flow':list(zip(self.ids,flow)),'ranges':ranges}

    def command(self, op, command):
        if op=='solve':
            return self.solve(command)
        assert op=='patch'
        rows,balance = map(list,self.state)
        for k,lo,hi,cost in command['edges']:
            rows[self.lookup[k]] = lo,hi,cost
        for u,x in command['balance']:
            balance[u] = x
        self.set_state((tuple(rows),tuple(balance)))
        return OK


def main():
    modules = dict(euler=Euler,ink=Ink,mirror=Mirror,dyadic=Dyadic,tide=Tide,prism=Prism)
    states = {}
    output = sys.stdout.buffer
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        record = json.loads(line)
        family,op = record['op'].split('_',1)
        if op=='init':
            states[family] = modules[family](record)
            answer = OK
        else:
            answer = states[family].run(op,record)
        output.write(json.dumps(answer,separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
