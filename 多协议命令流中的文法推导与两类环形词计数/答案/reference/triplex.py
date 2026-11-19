"""TRIPLEX: three independently owned states and snapshot namespaces."""
import hashlib
import heapq
import json
import math
import sys
from array import array
from collections import deque


def det(a):
    a=[r[:] for r in a];n=len(a)
    if not n:return 1
    previous=1;sign=1
    for k in range(n-1):
        if not a[k][k]:
            row=next((i for i in range(k+1,n) if a[i][k]),None)
            if row is None:return 0
            a[k],a[row]=a[row],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):a[i][j]=(a[i][j]*pivot-a[i][k]*a[k][j])//previous
        for i in range(k+1,n):a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def arborescences(edges,root):
    active=[i for i in range(len(edges)) if i==root or any(edges[i]) or any(row[i] for row in edges)]
    others=[i for i in active if i!=root]
    return det([[sum(edges[i][v] for v in active if v!=i) if i==j else -edges[i][j]
                 for j in others] for i in others])


class Factorials:
    def __init__(self,p,a):
        self.p=p;self.output=p**a;bound=1;extra=0
        while bound*p<=200000:bound*=p;extra+=1
        self.exponent=a+extra;self.precision=self.output*bound
        self.unit=array('Q',[1]);self.val=array('I',[0]);unit=1;valuation=0
        for k in range(1,200001):
            t=k
            while t%p==0:t//=p;valuation+=1
            unit=unit*t%self.precision;self.unit.append(unit);self.val.append(valuation)
    def ratio(self,scalar,top,bottom):
        if scalar==0:return 0
        power=0
        while scalar%self.p==0:scalar//=self.p;power+=1
        power+=sum(self.val[k] for k in top)-sum(self.val[k] for k in bottom)
        assert power>=0
        if power>=self.exponent:return 0
        numerator=scalar%self.precision;denominator=1
        for k in top:numerator=numerator*self.unit[k]%self.precision
        for k in bottom:denominator=denominator*self.unit[k]%self.precision
        return numerator*pow(denominator,-1,self.precision)*pow(self.p,power,self.precision)%self.precision
    def divide(self,value,divisor):
        power=1
        while divisor%self.p==0:divisor//=self.p;power*=self.p
        assert value%power==0
        return value//power*pow(divisor,-1,self.output)%self.output


class Euler:
    def __init__(self,c):
        self.v=c['vertices'];self.edges=[r[:] for r in c['edges']]
        self.tables=[Factorials(p,a) for p,a in c['mod_factors']]
        self.mod=math.prod(t.output for t in self.tables)
        self.crt=[self.mod//t.output*pow(self.mod//t.output,-1,t.output)%self.mod for t in self.tables]
        self.saved={};self.invalidate()
    def invalidate(self):self.core=None;self.word=None;self.prefixes={}
    def state(self):return tuple(tuple(r) for r in self.edges)
    def combine(self,values):return sum(v*k for v,k in zip(values,self.crt))%self.mod
    def prepare(self,factors):
        if self.core is not None:return
        n=sum(map(sum,self.edges));degree=[sum(row) for row in self.edges]
        active=[i for i,d in enumerate(degree) if d];tree=arborescences(self.edges,active[0])
        repeats=[1]
        for p,e in factors:repeats=[r*p**j for r in repeats for j in range(e+1)]
        repeats.sort(reverse=True);base={};exact={};periods=[]
        for r in repeats:
            top=[degree[i]//r-1 for i in active]
            bottom=[x//r for row in self.edges for x in row if x]
            scaled=tree//r**(len(active)-1)
            base[r]=[t.ratio(n//r*scaled,top,bottom) for t in self.tables]
            exact[r]=[(x-sum(exact[s][i] for s in repeats if s>r and s%r==0))%t.precision
                      for i,(x,t) in enumerate(zip(base[r],self.tables))]
            p=n//r
            periods.append({'period':p,'words':self.combine(exact[r]),
                            'necklaces':self.combine([t.divide(x,p) for t,x in zip(self.tables,exact[r])])})
        self.length=n;self.base=base
        self.core={'possible':tree>0,'length':n,'words':self.combine(base[1]),
                   'necklaces':sum(p['necklaces'] for p in periods)%self.mod,'periods':periods}
    def canonical(self):
        if self.word is not None:return self.word
        remaining=[r[:] for r in self.edges];start=next(i for i,r in enumerate(remaining) if any(r))
        cursor=[0]*self.v;stack=[start];reverse=[]
        while stack:
            u=stack[-1];v=cursor[u]
            while v<self.v and not remaining[u][v]:v+=1
            cursor[u]=v
            if v==self.v:reverse.append(stack.pop())
            else:remaining[u][v]-=1;stack.append(v)
        self.word=bytes(reversed(reverse))[:-1]
        return self.word
    def prefix_count(self,prefix):
        key=tuple(prefix)
        if key in self.prefixes:return self.prefixes[key]
        if not prefix:return self.core['words']
        if len(prefix)>self.length or not self.core['possible']:return 0
        remaining=[r[:] for r in self.edges]
        for u,v in zip(prefix,prefix[1:]):
            if not remaining[u][v]:return 0
            remaining[u][v]-=1
        target=prefix[0];tree=arborescences(remaining,target)
        if tree==0:return 0
        degree=[sum(r) for r in remaining]
        top=[degree[i]-1+int(i==target) for i in range(self.v)
             if i==target or degree[i] or any(r[i] for r in remaining)]
        if min(top)<0:return 0
        bottom=[x for row in remaining for x in row if x]
        answer=self.combine([t.ratio(tree,top,bottom) for t in self.tables])
        if len(self.prefixes)>=256:self.prefixes.pop(next(iter(self.prefixes)))
        self.prefixes[key]=answer;return answer
    def execute(self,c,op):
        if op=='count':
            self.prepare(c['gcd_factors']);n=self.length;result=dict(self.core)
            result['fixed_rotations']=[self.combine(self.base[r]) if (r:=n//math.gcd(n,k)) in self.base else 0 for k in c['rotations']]
            result['prefix_counts']=[self.prefix_count(p) for p in c['prefixes']]
            if self.core['possible']:
                word=self.canonical()
                result['witness']={'sha256':hashlib.sha256(b'EULER1'+n.to_bytes(8,'little')+word).hexdigest(),
                                   'at':[word[k] if k<n else None for k in c['at']]}
            else:result['witness']=None
            return result
        if op=='cycle':
            vertices=c['vertices'];delta=c['delta']
            if delta:
                for u,v in zip(vertices,vertices[1:]+vertices[:1]):self.edges[u][v]+=delta
                self.invalidate()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            state=self.saved[c['slot']]
            if state!=self.state():self.edges=[list(r) for r in state];self.invalidate()
        else:raise AssertionError(op)
        return {'ok':True}


class ParseChart:
    def __init__(self,n,rules,mod,word):
        z=len(word)+1;spans=[(i,j) for i in range(z) for j in range(i,z)]
        index={s:k for k,s in enumerate(spans)};self.width=len(spans);v=n*self.width;edges=[]
        for r in rules:
            if not r['enabled']:continue
            head=r['lhs']*self.width;rhs=r['rhs'];cost=r['cost'];rid=r['id']
            if not rhs:
                for i in range(z):edges.append((head+index[i,i],(),cost,rid))
            elif isinstance(rhs[0],str):
                for i,ch in enumerate(word):
                    if ch==rhs[0]:edges.append((head+index[i,i+1],(),cost,rid))
            elif len(rhs)==1:
                tail=rhs[0]*self.width
                for k in range(self.width):edges.append((head+k,(tail+k,),cost,rid))
            else:
                left,right=(x*self.width for x in rhs)
                for k,(i,j) in enumerate(spans):
                    for mid in range(i,j+1):edges.append((head+k,(left+index[i,mid],right+index[mid,j]),cost,rid))
        dist=[None]*v;keys=[None]*v;settled=[False]*v;roots=[0]*v
        reverse=[[] for _ in range(v)];waiting=[];costs=[];sizes=[];heap=[];pool=[None];intern={}
        def less_tree(a,b):
            while a!=b:
                x,y=pool[a],pool[b]
                if x[0]!=y[0]:return x[0]<y[0]
                for p,q in zip(x[1],y[1]):
                    if p!=q:a,b=p,q;break
                else:raise AssertionError('interning')
            return False
        def less_key(a,b):
            if a[0]!=b[0]:return a[0]<b[0]
            for x,y in zip(a[1],b[1]):
                if x!=y:return less_tree(x,y)
            return False
        def offer(u,cost,size,key):
            if settled[u]:return
            value=(cost,size)
            if dist[u] is None or value<dist[u]:
                dist[u]=value;keys[u]=key;heapq.heappush(heap,(cost,size,u))
            elif value==dist[u] and less_key(key,keys[u]):keys[u]=key
        for e,(head,children,cost,rid) in enumerate(edges):
            waiting.append(len(children));costs.append(cost);sizes.append(1)
            if not children:offer(head,cost,1,(rid,()))
            for child in children:reverse[child].append(e)
        while heap:
            cost,size,u=heapq.heappop(heap)
            if settled[u] or dist[u]!=(cost,size):continue
            settled[u]=True;key=keys[u]
            if key not in intern:
                rid,children=key
                digest=hashlib.sha256(b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(children)])+
                                      b''.join(pool[c][3] for c in children)).digest()
                intern[key]=len(pool);pool.append((rid,children,size,digest))
            roots[u]=intern[key]
            for e in reverse[u]:
                waiting[e]-=1;costs[e]+=cost;sizes[e]+=size
                if not waiting[e]:
                    head,children,_,rid=edges[e]
                    offer(head,costs[e],sizes[e],(rid,tuple(roots[c] for c in children)))
        tight=[[] for _ in range(v)];parents=[[] for _ in range(v)];degree=[0]*v
        for head,children,cost,rid in edges:
            if dist[head] is None or any(dist[c] is None for c in children):continue
            if cost+sum(dist[c][0] for c in children)!=dist[head][0]:continue
            tight[head].append(children);degree[head]+=len(children)
            for child in children:parents[child].append(head)
        ways=[None]*v;ready=deque(u for u in range(v) if dist[u] is not None and degree[u]==0)
        while ready:
            u=ready.popleft();total=0
            for children in tight[u]:
                product=1
                for child in children:product=product*ways[child]%mod
                total=(total+product)%mod
            ways[u]=total
            for p in parents[u]:
                degree[p]-=1
                if degree[p]==0:ready.append(p)
        self.dist=dist;self.ways=ways;self.roots=roots;self.pool=pool;self.last=len(word)
    def answer(self,c):
        u=c['start']*self.width+self.last
        if self.dist[u] is None:return {'possible':False}
        cost,size=self.dist[u];root=self.roots[u]
        def at(k):
            if k>=size:return None
            node=root
            while k:
                k-=1
                for child in self.pool[node][1]:
                    if k<self.pool[child][2]:node=child;break
                    k-=self.pool[child][2]
                else:raise AssertionError('preorder')
            return self.pool[node][0]
        return {'possible':True,'cost':cost,'infinite':self.ways[u] is None,'ways':self.ways[u],
                'witness':{'nodes':size,'sha256':self.pool[root][3].hex(),'at':[at(k) for k in c['at']]}}


class Ink:
    def __init__(self,c):
        self.n=c['nonterminals'];self.mod=c['mod'];self.rules=[dict(r,rhs=r['rhs'][:]) for r in c['rules']]
        self.by_id={r['id']:r for r in self.rules};self.saved={};self.cache={}
    def state(self):return tuple((r['cost'],r['enabled']) for r in self.rules)
    def execute(self,c,op):
        if op=='parse':
            word=c['word']
            if word not in self.cache:
                if len(self.cache)>=4:self.cache.pop(next(iter(self.cache)))
                self.cache[word]=ParseChart(self.n,self.rules,self.mod,word)
            return self.cache[word].answer(c)
        if op in ('weight','enable'):
            r=self.by_id[c['id']];field='cost' if op=='weight' else 'enabled';value=c['cost' if op=='weight' else 'value']
            if r[field]!=value:r[field]=value;self.cache.clear()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            state=self.saved[c['slot']]
            if state!=self.state():
                for r,(cost,enabled) in zip(self.rules,state):r['cost']=cost;r['enabled']=enabled
                self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


class PolynomialRing:
    def __init__(self,c,q,m):
        self.c=c;self.q=q;self.m=m;self.bits=2*m.bit_length()+(c*q).bit_length()+1
        self.mask=(1<<self.bits)-1;self.cut=self.bits*q;self.low=(1<<self.cut)-1
    def mono(self,k):return 1<<(self.bits*(k%self.q))
    def reduce(self,x):
        x=(x&self.low)+(x>>self.cut);out=0
        for i in range(self.q):out|=((x&self.mask)%self.m)<<(self.bits*i);x>>=self.bits
        return out
    def matrix(self,a,b):
        columns=list(zip(*b))
        return [[self.reduce(sum(x*y for x,y in zip(row,col))) for col in columns] for row in a]
    def vector(self,row,matrix):return [self.reduce(sum(x*y for x,y in zip(row,col))) for col in zip(*matrix)]
    def powers(self,matrix,bits):
        out=[matrix]
        for _ in range(1,bits):out.append(self.matrix(out[-1],out[-1]))
        return out
    def power(self,powers,n):
        out=[[int(i==j) for j in range(self.c)] for i in range(self.c)];k=0
        while n:
            if n&1:out=self.matrix(out,powers[k])
            n>>=1;k+=1
        return out
    def apply(self,row,powers,n):
        k=0
        while n:
            if n&1:row=self.vector(row,powers[k])
            n>>=1;k+=1
        return row
    def filter(self,x,multiple,residue):
        return sum((x>>(self.bits*k))&self.mask for k in range(self.q) if multiple*k%self.q==residue)%self.m


def mirror_counts(c,q,mod,tau,weights,edges,factors,residue):
    n=math.prod(p**e for p,e in factors);lift=2*n*mod;divisors=[1]
    for p,e in factors:divisors=[d*p**k for d in divisors for k in range(e+1)]
    divisors.sort();ring=PolynomialRing(c,q,lift)
    one=[ring.mono(w) for w in weights];two=[ring.mono(2*w) for w in weights]
    a=[[one[j] if edges[i][j] else 0 for j in range(c)] for i in range(c)]
    b=[[two[j] if edges[i][j] else 0 for j in range(c)] for i in range(c)]
    pa=ring.powers(a,n.bit_length());pb=pa if a==b else ring.powers(b,n.bit_length())
    fixed=[tau[i]==i for i in range(c)];seam=[int(edges[i][tau[i]]) for i in range(c)]
    start=[one[i] if fixed[i] else 0 for i in range(c)]
    start_edge=[two[i]*seam[i] for i in range(c)]
    end=[ring.reduce(sum(a[i][j] for j in range(c) if fixed[j])) for i in range(c)]
    base={};reflection={};single={}
    for d in divisors:
        repeat=n//d;matrix=ring.power(pa,d)
        base[d]=ring.filter(ring.reduce(sum(matrix[i][i] for i in range(c))),repeat,residue)
        if d%2:
            row=ring.apply(start,pb,d//2)
            value=ring.filter(ring.reduce(sum(x*y for x,y in zip(row,seam))),repeat,residue)
            single[d]=(value,value);reflection[d]=d*value%lift
        else:
            row=ring.apply(start,pb,d//2-1)
            vertex=ring.filter(ring.reduce(sum(x*y for x,y in zip(row,end))),repeat,residue)
            row=ring.apply(start_edge,pb,d//2-1)
            edge=ring.filter(ring.reduce(sum(x*y for x,y in zip(row,seam))),repeat,residue)
            single[d]=(vertex,edge);reflection[d]=d//2*(vertex+edge)%lift
    exact={};exact_ref={};periods=[]
    for p in divisors:
        exact[p]=(base[p]-sum(exact[d] for d in divisors if d<p and p%d==0))%lift
        exact_ref[p]=(reflection[p]-sum((p//d)*exact_ref[d] for d in divisors if d<p and p%d==0))%lift
        periods.append({'period':p,'words':exact[p]%mod,'necklaces':exact[p]//p%mod,
                        'bracelets':((exact[p]+exact_ref[p])%lift)//(2*p)%mod})
    core={'length':n,'words':base[n]%mod,'necklaces':sum(p['necklaces'] for p in periods)%mod,
          'bracelets':sum(p['bracelets'] for p in periods)%mod,'periods':periods}
    return core,{d:x%mod for d,x in base.items()},tuple(x%mod for x in single[n])


class Mirror:
    def __init__(self,c):
        self.c=c['colors'];self.q=c['inventory_mod'];self.mod=c['mod'];self.tau=c['mirror'][:]
        self.weights=c['weights'][:];self.edges=[r[:] for r in c['edges']];self.saved={};self.cache={}
    def state(self):return tuple(self.weights),tuple(tuple(r) for r in self.edges)
    def execute(self,c,op):
        if op=='orbit':
            key=tuple(tuple(x) for x in c['factors']),c['residue']
            if key not in self.cache:
                if len(self.cache)>=8:self.cache.pop(next(iter(self.cache)))
                self.cache[key]=mirror_counts(self.c,self.q,self.mod,self.tau,self.weights,self.edges,*key)
            core,rotations,mirrors=self.cache[key];n=core['length']
            return dict(core,fixed={'rotations':[rotations[math.gcd(n,k)] for k in c['rotations']],
                                    'mirrors':[mirrors[k%2] for k in c['mirrors']]})
        if op=='weight':
            color=c['color'];value=c['value']
            if self.weights[color]!=value:self.weights[color]=self.weights[self.tau[color]]=value;self.cache.clear()
        elif op=='edge':
            u,v=c['u'],c['v'];changed=False
            for a,b in {(u,v),(v,u),(self.tau[u],self.tau[v]),(self.tau[v],self.tau[u])}:
                if self.edges[a][b]!=c['value']:self.edges[a][b]=c['value'];changed=True
            if changed:self.cache.clear()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            state=self.saved[c['slot']]
            if state!=self.state():self.weights=list(state[0]);self.edges=[list(r) for r in state[1]];self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    machines={};constructors={'euler':Euler,'ink':Ink,'mirror':Mirror}
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line);family,op=c['op'].split('_',1)
        if op=='init':machines[family]=constructors[family](c);result={'ok':True}
        else:result=machines[family].execute(c,op)
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
