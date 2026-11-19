"""Standard-library implementation of constrained minimum-cost flow."""
import json
import sys
from collections import deque


class BlockingFlow:
    def __init__(self, n):
        self.graph = [[] for _ in range(n)]
        self.to = []
        self.cap = []

    def add(self, u, v, cap):
        arc = len(self.to)
        self.graph[u].append(arc)
        self.graph[v].append(arc+1)
        self.to.extend((v,u))
        self.cap.extend((cap,0))
        return arc

    def send(self, source, sink, limit):
        sent = 0
        graph, to, cap = self.graph, self.to, self.cap
        while sent < limit:
            level = [-1]*len(graph)
            level[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for a in graph[u]:
                    v = to[a]
                    if cap[a] and level[v] < 0:
                        level[v] = level[u]+1
                        queue.append(v)
            if level[sink] < 0:
                break
            cursor = [0]*len(graph)

            def push(u, amount):
                if u == sink:
                    return amount
                while cursor[u] < len(graph[u]):
                    arc = graph[u][cursor[u]]
                    v = to[arc]
                    if cap[arc] and level[v] == level[u]+1:
                        got = push(v,min(amount,cap[arc]))
                        if got:
                            cap[arc] -= got
                            cap[arc^1] += got
                            return got
                    cursor[u] += 1
                return 0

            while sent < limit:
                got = push(source,limit-sent)
                if not got:
                    break
                sent += got
        return sent


def feasibility(n, edges, bounds, balance):
    if sum(balance):
        return None
    network = BlockingFlow(n+2)
    need = list(balance)
    flow = [lo for lo,hi in bounds]
    tracked = []
    for i, (_,u,v) in enumerate(edges):
        lo, hi = bounds[i]
        if u != v:
            need[u] -= lo
            need[v] += lo
            tracked.append((i,network.add(u,v,hi-lo)))
    amount = 0
    for u,b in enumerate(need):
        if b > 0:
            network.add(n,u,b)
            amount += b
        elif b < 0:
            network.add(u,n+1,-b)
    if network.send(n,n+1,amount) != amount:
        return None
    for edge,arc in tracked:
        flow[edge] += network.cap[arc^1]
    return flow


def minimize(n, edges, bounds, costs, flow):
    graph = [[] for _ in range(n)]
    head, tail, caps, price = [], [], [], []
    mapping = []
    for i, (_,u,v) in enumerate(edges):
        lo,hi = bounds[i]
        if u == v:
            flow[i] = hi if costs[i] < 0 else lo
            continue
        arc = len(head)
        mapping.append((i,arc))
        head.extend((v,u))
        tail.extend((u,v))
        caps.extend((hi-flow[i],flow[i]-lo))
        cost = (n+1)*costs[i]
        price.extend((cost,-cost))
        graph[u].append(arc)
        graph[v].append(arc+1)
    potential = [0]*n
    maximum = max(map(abs,price),default=0)
    epsilon = 1 << maximum.bit_length()
    while epsilon > 1:
        epsilon //= 2
        excess = [0]*n
        for a, cost in enumerate(price):
            u,v = tail[a],head[a]
            if caps[a] and cost+potential[u]-potential[v] < 0:
                amount = caps[a]
                caps[a] = 0
                caps[a^1] += amount
                excess[u] -= amount
                excess[v] += amount
        queue = deque(i for i,b in enumerate(excess) if b>0)
        cursor = [0]*n
        while queue:
            u = queue.popleft()
            while excess[u] > 0:
                if cursor[u] == len(graph[u]):
                    potential[u] = max(potential[head[a]]-price[a]-epsilon for a in graph[u] if caps[a])
                    cursor[u] = 0
                arc = graph[u][cursor[u]]
                v = head[arc]
                if not caps[arc] or price[arc]+potential[u]-potential[v] >= 0:
                    cursor[u] += 1
                    continue
                amount = min(caps[arc],excess[u])
                if excess[v] <= 0 < excess[v]+amount:
                    queue.append(v)
                excess[u] -= amount
                excess[v] += amount
                caps[arc] -= amount
                caps[arc^1] += amount
    for i,a in mapping:
        flow[i] = bounds[i][0]+caps[a^1]

    # Solve the exact residual potential inequalities after cost scaling.
    distance = [0]*n
    for _ in range(n):
        changed = False
        for i,(_,u,v) in enumerate(edges):
            lo,hi = bounds[i]
            c = costs[i]
            if flow[i] < hi and distance[v] > distance[u]+c:
                distance[v] = distance[u]+c
                changed = True
            if flow[i] > lo and distance[u] > distance[v]-c:
                distance[u] = distance[v]-c
                changed = True
        if not changed:
            break
    else:
        raise AssertionError('negative residual cycle')
    return [costs[i]+distance[u]-distance[v]==0 for i,(_,u,v) in enumerate(edges)]


class Face:
    def __init__(self, n, edges, bounds, tight):
        self.n, self.edges, self.bounds, self.tight = n, edges, bounds, tight

    def move(self, flow, index, direction, locked, apply=False):
        if not self.tight[index]:
            return 0
        lo,hi = self.bounds[index]
        limit = hi-flow[index] if direction>0 else flow[index]-lo
        if not limit:
            return 0
        _,u,v = self.edges[index]
        if u == v:
            if apply:
                flow[index] += direction*limit
            return limit
        network = BlockingFlow(self.n)
        arcs = []
        for i,(_,a,b) in enumerate(self.edges):
            if i in locked or i == index or a == b or not self.tight[i]:
                continue
            left,right = self.bounds[i]
            if flow[i] < right:
                arcs.append((i,1,network.add(a,b,right-flow[i])))
            if flow[i] > left:
                arcs.append((i,-1,network.add(b,a,flow[i]-left)))
        amount = network.send(v,u,limit) if direction>0 else network.send(u,v,limit)
        if apply:
            flow[index] += direction*amount
            for i,sign,arc in arcs:
                flow[i] += sign*network.cap[arc^1]
        return amount


class Ledger:
    def __init__(self, command):
        edges = sorted(command['edges'],key=lambda edge:edge['id'])
        self.n = command['vertices']
        self.edges = tuple((e['id'],e['u'],e['v']) for e in edges)
        self.edge_id = {e[0]:i for i,e in enumerate(self.edges)}
        self.state = (tuple((e['lo'],e['hi'],e['cost']) for e in edges),tuple(command['balance']))
        self.snapshots = {}
        self.cache = {}

    def replace(self, state):
        if state != self.state:
            self.state = state
            self.cache.clear()

    def solve(self, command):
        key = tuple(sorted(tuple(x) for x in command['pins']))
        if key not in self.cache:
            if len(self.cache) >= 8:
                self.cache.pop(next(iter(self.cache)))
            table,balance = self.state
            bounds = [(lo,hi) for lo,hi,_ in table]
            costs = [cost for _,_,cost in table]
            for label,value in key:
                i = self.edge_id[label]
                lo,hi = bounds[i]
                if not lo <= value <= hi:
                    self.cache[key] = None
                    break
                bounds[i] = (value,value)
            else:
                flow = feasibility(self.n,self.edges,bounds,balance)
                if flow is None:
                    self.cache[key] = None
                else:
                    tight = minimize(self.n,self.edges,bounds,costs,flow)
                    face = Face(self.n,self.edges,bounds,tight)
                    locked = set()
                    for i in range(len(flow)):
                        face.move(flow,i,-1,locked,True)
                        locked.add(i)
                    cost = sum(a*b for a,b in zip(flow,costs))
                    self.cache[key] = cost,flow,face,{}
        data = self.cache[key]
        if data is None:
            return {'possible':False}
        cost, flow, face, ranges = data
        requested = []
        for label in command['inspect']:
            i = self.edge_id[label]
            if i not in ranges:
                ranges[i] = [flow[i]-face.move(flow,i,-1,()),flow[i]+face.move(flow,i,1,())]
            requested.append(ranges[i])
        return {'possible':True,'cost':cost,'flow':[[e[0],f] for e,f in zip(self.edges,flow)],'ranges':requested}

    def execute(self, command):
        op = command['op']
        if op == 'solve':
            return self.solve(command)
        if op == 'save':
            self.snapshots[command['slot']] = self.state
        elif op == 'load':
            self.replace(self.snapshots[command['slot']])
        elif op == 'patch':
            table,balance = map(list,self.state)
            for label,lo,hi,cost in command['edges']:
                table[self.edge_id[label]] = (lo,hi,cost)
            for u,b in command['balance']:
                balance[u] = b
            self.replace((tuple(table),tuple(balance)))
        else:
            raise AssertionError(op)
        return {'ok':True}


def main():
    ledger = None
    output = sys.stdout.buffer
    for row in sys.stdin.buffer:
        if not row.strip():
            continue
        command = json.loads(row)
        if command['op'] == 'init':
            ledger = Ledger(command)
            reply = {'ok':True}
        else:
            reply = ledger.execute(command)
        output.write(json.dumps(reply,separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
