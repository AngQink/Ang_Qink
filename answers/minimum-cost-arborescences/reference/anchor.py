"""Count minimum-cost rooted arborescences exactly."""
import json
import sys


def determinant(matrix):
    previous = 1
    n = len(matrix)
    for k in range(n-1):
        row = matrix[k]
        pivot = row[k]
        if not pivot:
            return 0
        for i in range(k+1,n):
            other = matrix[i]
            a = other[k]
            for j in range(k+1,n):
                other[j] = (pivot*other[j]-a*row[j])//previous
        previous = pivot
    return matrix[-1][-1] if n else 1


def tree_weights(edges, vertices, roots):
    pos = {u:i for i,u in enumerate(vertices)}
    size = len(vertices)
    laplacian = [[0]*size for _ in vertices]
    for u,v,weight in edges:
        row = laplacian[pos[v]]
        row[pos[v]] += weight
        row[pos[u]] -= weight
    result = {}
    for root in roots:
        i = pos[root]
        # A directed in-degree Laplacian gives outward trees. Its
        # nonsingular principal cofactors have positive leading minors.
        result[root] = determinant([row[:i]+row[i+1:] for j,row in enumerate(laplacian) if j!=i])
    return result


def close(reach):
    n = len(reach)
    for k in range(n):
        allowed = reach[k]
        bit = 1<<k
        for i in range(n):
            if reach[i]&bit:
                reach[i] |= allowed


def minimum_trees(n, root, edges):
    # Incoming weights are (tail, head, integer cost, multiplicity).
    # Initial overall reachability is independent of cost.
    adj = [[] for _ in range(n)]
    for u,v,_,_ in edges:
        adj[u].append(v)
    visited = {root}
    queue = [root]
    for u in queue:
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    if len(visited)!=n:
        return None,0

    total = 0
    while True:
        lowest = [None]*n
        lowest[root] = 0
        for u,v,c,_ in edges:
            if lowest[v] is None or c<lowest[v]:
                lowest[v] = c
        total += sum(lowest)
        edges = [(u,v,c-lowest[v],w) for u,v,c,w in edges]
        zero = [(u,v,w) for u,v,c,w in edges if c==0]
        reach = [1<<i for i in range(n)]
        for u,v,_ in zero:
            reach[u] |= 1<<v
        close(reach)
        if reach[root]==(1<<n)-1:
            return total,tree_weights(zero,list(range(n)),[root])[root]

        # Locate a source SCC in the zero graph other than the root SCC.
        # Each way of entering it has positive reduced cost.
        for r in range(n):
            bit = 1<<r
            if reach[root]&bit:
                continue
            inbound = sum(1<<i for i,mask in enumerate(reach) if mask&bit)
            if inbound&~reach[r]==0:
                break
        else:
            raise AssertionError('no zero source component')
        component = [i for i in range(n) if inbound>>i&1]
        inside = set(component)
        entry = {v for u,v,c,w in edges if v in inside and u not in inside}
        internal = [(u,v,w) for u,v,w in zero if u in inside and v in inside]
        choices = tree_weights(internal,component,entry)
        others = [i for i in range(n) if i not in inside]
        remap = {v:i for i,v in enumerate(others)}
        block = len(others)
        updated = []
        for u,v,c,w in edges:
            if u in inside:
                if v not in inside:
                    updated.append((block,remap[v],c,w))
            elif v in inside:
                updated.append((remap[u],block,c,w*choices[v]))
            else:
                updated.append((remap[u],remap[v],c,w))
        n,root,edges = block+1,remap[root],updated


class TreeOrder:
    def __init__(self, n, root, endpoints, conditions, costs, pins):
        self.n, self.root = n,root
        self.endpoints, self.costs = endpoints,costs
        self.vertices = [i for i in range(n) if i!=root]
        self.available = []
        self.options = [[] for _ in range(n)]
        self.results = {}
        for label,(u,v) in endpoints.items():
            if conditions[label] and u!=v and v!=root:
                self.options[v].append(label)
                self.available.append(label)
        self.base = [-1]*n
        self.total = 0
        self.optimal = None
        for label in pins:
            _,v = endpoints[label]
            if label not in self.options[v] or self.base[v]>=0:
                return
            self.base[v] = label
            self.options[v] = [label]
        for labels in self.options:
            labels.sort()
        self.optimal,self.total = self.resolve(self.base)

    def resolve(self, locks):
        key = tuple(locks)
        if key not in self.results:
            edges = []
            for label in self.available:
                u,v = self.endpoints[label]
                if locks[v]<0 or label==locks[v]:
                    edges.append((u,v,self.costs[label],1))
            self.results[key] = minimum_trees(self.n,self.root,edges)
        return self.results[key]

    def branch(self, locks, v,label):
        if label not in self.options[v] or locks[v]>=0 and label!=locks[v]:
            return 0
        old = locks[v]
        locks[v] = label
        cost,count = self.resolve(locks)
        locks[v] = old
        return count if cost==self.optimal else 0

    def pick(self, k):
        if k>=self.total:
            return None
        locks = self.base[:]
        count = self.total
        answer = []
        for v in self.vertices:
            options = self.options[v]
            for i,label in enumerate(options):
                # A known parent fiber partitions by the next coordinate.
                branch = count if i==len(options)-1 else self.branch(locks,v,label)
                if k<branch:
                    locks[v] = label
                    answer.append(label)
                    count = branch
                    break
                k -= branch
                count -= branch
            else:
                raise AssertionError('rank exceeds fiber')
        return answer

    def rank(self, vector):
        if not self.total:
            return {'before':0,'member':False}
        locks = self.base[:]
        count = self.total
        before = 0
        for vertex,value in zip(self.vertices,vector):
            options = self.options[vertex]
            for i,label in enumerate(options):
                if label>value:
                    return {'before':before,'member':False}
                branch = count if i==len(options)-1 else self.branch(locks,vertex,label)
                if label==value:
                    if branch==0:
                        return {'before':before,'member':False}
                    locks[vertex] = label
                    count = branch
                    break
                before += branch
                count -= branch
            else:
                return {'before':before,'member':False}
        return {'before':before,'member':True}

    def uses(self, label):
        if not self.total or label not in self.endpoints:
            return 0
        return self.branch(self.base[:],self.endpoints[label][1],label)

    def answer(self, command):
        return {'possible':bool(self.total),'cost':self.optimal,'count':self.total,
                'at':[self.pick(k) for k in command['at']],
                'probes':[self.rank(v) for v in command['probes']],
                'uses':[self.uses(label) for label in command['uses']]}


class Ledger:
    def __init__(self, init):
        self.n = init['vertices']
        edges = init['edges']
        self.endpoints = {e['id']:(e['u'],e['v']) for e in edges}
        self.labels = [e['id'] for e in edges]
        self.slots = {}
        self.state = tuple((e['cost'],e['enabled']) for e in edges)
        self.cache = {}

    def replace(self, state):
        if state!=self.state:
            self.state = state
            self.cache.clear()

    def execute(self, cmd):
        op = cmd['op']
        if op=='query':
            key = cmd['root'],tuple(sorted(cmd['pins']))
            if key not in self.cache:
                cost = {i:c for i,(c,en) in zip(self.labels,self.state)}
                enabled = {i:en for i,(c,en) in zip(self.labels,self.state)}
                if len(self.cache)>=4:
                    self.cache.pop(next(iter(self.cache)))
                self.cache[key] = TreeOrder(self.n,key[0],self.endpoints,enabled,cost,key[1])
            return self.cache[key].answer(cmd)
        if op=='save':
            self.slots[cmd['slot']] = self.state
        elif op=='load':
            self.replace(self.slots[cmd['slot']])
        else:
            i = self.labels.index(cmd['id'])
            cost,on = self.state[i]
            values = (cmd['cost'],on) if op=='cost' else (cost,cmd['value'])
            self.replace(self.state[:i]+(values,)+self.state[i+1:])
        return {'ok':True}


def main():
    state = None
    output = sys.stdout.buffer
    for raw in sys.stdin.buffer:
        if not raw.strip():
            continue
        command = json.loads(raw)
        if command['op']=='init':
            state = Ledger(command)
            result = {'ok':True}
        else:
            result = state.execute(command)
        output.write(json.dumps(result,separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
