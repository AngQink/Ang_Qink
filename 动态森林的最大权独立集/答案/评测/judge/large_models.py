"""Independent closed-form pressure models, with exact integer counts."""
import bisect
from models import best


class HubModel:
    def __init__(self, weights, edges, modulus, hubs):
        self.w = weights[:]
        self.mod = modulus
        self.hubs = hubs
        self.g = [set() for _ in range(hubs)]
        self.parent = [-1]*len(weights)
        self.positive = [0]*hubs
        self.zeros = [0]*hubs
        self.leaves = [0]*hubs
        for u,v in edges:
            self._link(u,v)

    def _adjust(self, h, u, direction):
        self.positive[h] += direction*max(0,self.w[u])
        self.zeros[h] += direction*(self.w[u] == 0)
        self.leaves[h] += direction

    def _link(self, u,v):
        if u < self.hubs and v < self.hubs:
            self.g[u].add(v)
            self.g[v].add(u)
        else:
            if u < self.hubs:
                u,v = v,u
            assert v < self.hubs and self.parent[u] == -1
            self.parent[u] = v
            self._adjust(v,u,1)

    def component(self,u):
        h = u if u < self.hubs else self.parent[u]
        if h == -1:
            return [u], {u:None}
        order, parent = [h], {h:None}
        for v in order:
            for w in self.g[v]:
                if w != parent[v]:
                    assert w not in parent
                    parent[w] = v
                    order.append(w)
        return order,parent

    def same(self,u,v):
        members = self.component(u)[1]
        if u >= self.hubs and self.parent[u] == -1:
            return u == v
        return (v if v < self.hubs else self.parent[v]) in members

    def _solve(self,u,pins):
        order,parent = self.component(u)
        if u >= self.hubs and self.parent[u] == -1:
            if pins.get(u) == 1:
                return (self.w[u],1),1
            if pins.get(u) == 0:
                return (0,1),1
            return best((0,1),(self.w[u],1)),1
        dp, total = {}, 0
        for h in reversed(order):
            a = (self.positive[h], 1 << self.zeros[h])
            b = (self.w[h],1)
            total += 1+self.leaves[h]
            for vertex,state in pins.items():
                if vertex == h:
                    if state == 0:
                        b = None
                    else:
                        a = None
                elif vertex >= self.hubs and self.parent[vertex] == h:
                    if a is not None:
                        score,count = a
                        score -= max(0,self.w[vertex])
                        if self.w[vertex] == 0:
                            count //= 2
                        if state:
                            score += self.w[vertex]
                        a = score,count
                    if state:
                        b = None
            for child in self.g[h]:
                if child == parent[h]:
                    continue
                x,y = dp[child]
                z = best(x,y)
                a = None if a is None or z is None else (a[0]+z[0],a[1]*z[1])
                b = None if b is None or x is None else (b[0]+x[0],b[1]*x[1])
            dp[h] = a,b
        return best(*dp[order[0]]),total

    def execute(self,cmd):
        op,u = cmd['op'],cmd['u']
        if op == 'set':
            if u >= self.hubs and self.parent[u] != -1:
                self._adjust(self.parent[u],u,-1)
                self.w[u] = cmd['w']
                self._adjust(self.parent[u],u,1)
            else:
                self.w[u] = cmd['w']
        elif op == 'link':
            assert not self.same(u,cmd['v'])
            self._link(u,cmd['v'])
        elif op == 'cut':
            v = cmd['v']
            if u < self.hubs and v < self.hubs:
                self.g[u].remove(v)
                self.g[v].remove(u)
            else:
                if u < self.hubs:
                    u,v = v,u
                assert self.parent[u] == v
                self._adjust(v,u,-1)
                self.parent[u] = -1
        elif op == 'ask':
            a,n = self._solve(u,{u:0})
            b,_ = self._solve(u,{u:1})
            z = best(a,b)
            pack=lambda value:dict(weight=value[0],ways=value[1] % self.mod)
            return {'n':n,'best':pack(z),'out':pack(a),'in':pack(b)}
        elif op == 'pair':
            v = cmd['v']
            if not self.same(u,v):
                return dict(connected=False)
            if u == v and cmd['su'] != cmd['sv']:
                return dict(connected=True,possible=False)
            z,_ = self._solve(u,{u:cmd['su'],v:cmd['sv']})
            if z is None:
                return dict(connected=True,possible=False)
            return dict(connected=True,possible=True,weight=z[0],ways=z[1] % self.mod)
        else:
            raise ValueError(op)
        return dict(ok=True)


class LineModel:
    def __init__(self,n,weight,modulus):
        self.n,self.weight,self.mod = n,weight,modulus
        self.cuts = [-1,n-1]
        self.fib = [0,1]
        for _ in range(n+2):
            self.fib.append((self.fib[-1]+self.fib[-2]) % modulus)

    def bounds(self,u):
        at = bisect.bisect_left(self.cuts,u)
        return self.cuts[at-1]+1,self.cuts[at]

    def _solve(self,lo,hi,pins):
        included = sorted(u for u,state in pins.items() if state == 1)
        if any(b == a+1 for a,b in zip(included,included[1:])):
            return None
        blocked = set(pins)
        for u in included:
            blocked.update([u-1,u+1])
        score,ways = len(included)*self.weight,1
        begin = lo
        for end in sorted(v for v in blocked if lo <= v <= hi)+[hi+1]:
            length = end-begin
            if length > 0:
                if self.weight > 0:
                    score += ((length+1)//2)*self.weight
                    ways *= (1 if length % 2 else length//2+1)
                elif self.weight == 0:
                    ways *= self.fib[length+2]
            begin = end+1
        return score,ways

    def execute(self,cmd):
        op,u = cmd['op'],cmd['u']
        if op == 'cut':
            v = cmd['v']
            assert abs(u-v)==1 and min(u,v) not in self.cuts
            bisect.insort(self.cuts,min(u,v))
        elif op == 'link':
            v = cmd['v']
            assert abs(u-v)==1 and min(u,v) in self.cuts
            self.cuts.remove(min(u,v))
        elif op == 'set':
            assert cmd['w']==self.weight
        elif op == 'ask':
            lo,hi = self.bounds(u)
            a,b = self._solve(lo,hi,{u:0}),self._solve(lo,hi,{u:1})
            z = best(a,b)
            pack=lambda value:dict(weight=value[0],ways=value[1] % self.mod)
            return {'n':hi-lo+1,'best':pack(z),'out':pack(a),'in':pack(b)}
        elif op == 'pair':
            v=cmd['v']
            lo,hi=self.bounds(u)
            if not lo<=v<=hi:
                return dict(connected=False)
            if u==v and cmd['su']!=cmd['sv']:
                return dict(connected=True,possible=False)
            z=self._solve(lo,hi,{u:cmd['su'],v:cmd['sv']})
            if z is None:
                return dict(connected=True,possible=False)
            return dict(connected=True,possible=True,weight=z[0],ways=z[1] % self.mod)
        else:
            raise ValueError(op)
        return dict(ok=True)
