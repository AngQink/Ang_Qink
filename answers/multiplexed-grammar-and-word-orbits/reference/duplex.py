"""DUPLEX: independent grammar and colored-cycle state machines."""
import hashlib
import heapq
import json
import math
import sys
from collections import deque


class GrammarChart:
    def __init__(self, nonterminals, rules, modulus, word):
        width=len(word)+1
        spans=[(i,j) for i in range(width) for j in range(i,width)]
        count=len(spans)
        index={span:k for k,span in enumerate(spans)}
        vertices=nonterminals*count
        edges=[]
        for r in rules:
            if not r['enabled']:continue
            lhs=r['lhs']*count;rhs=r['rhs'];cost=r['cost'];rid=r['id']
            if not rhs:
                for i in range(width):edges.append((lhs+index[i,i],(),cost,rid))
            elif isinstance(rhs[0],str):
                for i,ch in enumerate(word):
                    if ch==rhs[0]:edges.append((lhs+index[i,i+1],(),cost,rid))
            elif len(rhs)==1:
                base=rhs[0]*count
                for k in range(count):edges.append((lhs+k,(base+k,),cost,rid))
            else:
                left,right=(b*count for b in rhs)
                for k,(i,j) in enumerate(spans):
                    for mid in range(i,j+1):
                        edges.append((lhs+k,(left+index[i,mid],right+index[mid,j]),cost,rid))
        dependent=[[] for _ in range(vertices)]
        waiting=[];costs=[];sizes=[];products=[]
        distance=[None]*vertices;minimal=[0]*vertices;choices=[None]*vertices
        settled=[False]*vertices;tree_at=[0]*vertices
        heap=[];pool=[None];intern={}

        def less_tree(a,b):
            while a!=b:
                x,y=pool[a],pool[b]
                if x[0]!=y[0]:return x[0]<y[0]
                for c,d in zip(x[1],y[1]):
                    if c!=d:a,b=c,d;break
                else:raise AssertionError('tree interning invariant')
            return False

        def less_choice(a,b):
            if a[0]!=b[0]:return a[0]<b[0]
            for x,y in zip(a[1],b[1]):
                if x!=y:return less_tree(x,y)
            return False

        def relax(u,cost,size,ways,key):
            if settled[u]:return
            pair=(cost,size);old=distance[u]
            if old is None or pair<old:
                distance[u]=pair;minimal[u]=ways%modulus;choices[u]=key
                heapq.heappush(heap,(cost,size,u))
            elif pair==old:
                minimal[u]=(minimal[u]+ways)%modulus
                if less_choice(key,choices[u]):choices[u]=key

        for e,(head,children,cost,rid) in enumerate(edges):
            waiting.append(len(children));costs.append(cost);sizes.append(1);products.append(1)
            if not children:relax(head,cost,1,1,(rid,()))
            for child in children:dependent[child].append(e)
        while heap:
            cost,size,u=heapq.heappop(heap)
            if settled[u] or distance[u]!=(cost,size):continue
            settled[u]=True;key=choices[u]
            if key not in intern:
                rid,children=key
                digest=hashlib.sha256(b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(children)])+
                                      b''.join(pool[c][3] for c in children)).digest()
                intern[key]=len(pool);pool.append((rid,children,size,digest))
            tree_at[u]=intern[key]
            # Repeated children appear twice, and their choices are independent.
            for e in dependent[u]:
                waiting[e]-=1;costs[e]+=cost;sizes[e]+=size
                products[e]=products[e]*minimal[u]%modulus
                if waiting[e]==0:
                    head,children,_,rid=edges[e]
                    relax(head,costs[e],sizes[e],products[e],(rid,tuple(tree_at[c] for c in children)))
        # Consider all primary-cost-optimal alternatives, including larger trees.
        tight=[[] for _ in range(vertices)];parents=[[] for _ in range(vertices)];degree=[0]*vertices
        for head,children,cost,rid in edges:
            if distance[head] is None or any(distance[c] is None for c in children):continue
            if cost+sum(distance[c][0] for c in children)!=distance[head][0]:continue
            tight[head].append(children);degree[head]+=len(children)
            for child in children:parents[child].append(head)
        ways=[None]*vertices
        ready=deque(u for u in range(vertices) if distance[u] is not None and degree[u]==0)
        while ready:
            u=ready.popleft();total=0
            for children in tight[u]:
                product=1
                for child in children:product=product*ways[child]%modulus
                total=(total+product)%modulus
            ways[u]=total
            for parent in parents[u]:
                degree[parent]-=1
                if degree[parent]==0:ready.append(parent)
        # Unprocessed productive items are precisely those reaching a tight cycle.
        self.distance=distance;self.minimal=minimal;self.ways=ways
        self.roots=tree_at;self.pool=pool;self.span_count=count;self.last=len(word)

    def answer(self,c,op):
        root=c['start']*self.span_count+self.last
        pair=self.distance[root]
        if pair is None:return {'possible':False}
        if op=='minways':return {'possible':True,'nodes':pair[1],'ways':self.minimal[root]}
        def at(position):
            if position>=pair[1]:return None
            node=self.roots[root]
            while position:
                position-=1
                for child in self.pool[node][1]:
                    size=self.pool[child][2]
                    if position<size:node=child;break
                    position-=size
                else:raise AssertionError('preorder rank invariant')
            return self.pool[node][0]
        return {'possible':True,'cost':pair[0],'infinite':self.ways[root] is None,'ways':self.ways[root],
                'witness':{'nodes':pair[1],'sha256':self.pool[self.roots[root]][3].hex(),
                           'at':[at(k) for k in c['at']]}}


class InkMachine:
    def __init__(self,c):
        self.n=c['nonterminals'];self.mod=c['mod']
        self.rules=[dict(r,rhs=r['rhs'][:]) for r in c['rules']]
        self.by_id={r['id']:r for r in self.rules};self.saved={};self.cache={}
    def state(self):return tuple((r['cost'],r['enabled']) for r in self.rules)
    def execute(self,c,op):
        if op in ('parse','minways'):
            word=c['word']
            if word not in self.cache:
                if len(self.cache)>=4:self.cache.pop(next(iter(self.cache)))
                self.cache[word]=GrammarChart(self.n,self.rules,self.mod,word)
            return self.cache[word].answer(c,op)
        if op=='weight':
            r=self.by_id[c['id']]
            if r['cost']!=c['cost']:r['cost']=c['cost'];self.cache.clear()
        elif op=='enable':
            r=self.by_id[c['id']]
            if r['enabled']!=c['value']:r['enabled']=c['value'];self.cache.clear()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            values=self.saved[c['slot']]
            if values!=self.state():
                for r,(cost,enabled) in zip(self.rules,values):r['cost']=cost;r['enabled']=enabled
                self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


class CyclicRing:
    def __init__(self,colors,degree,modulus):
        self.c=colors;self.q=degree;self.m=modulus
        self.bits=2*modulus.bit_length()+(colors*degree).bit_length()+1
        self.digit=(1<<self.bits)-1;self.cut=self.bits*degree;self.mask=(1<<self.cut)-1
    def mono(self,power):return 1<<(self.bits*(power%self.q))
    def reduce(self,value):
        value=(value&self.mask)+(value>>self.cut);result=0
        for i in range(self.q):
            result|=((value&self.digit)%self.m)<<(self.bits*i);value>>=self.bits
        return result
    def product(self,a,b):
        columns=list(zip(*b))
        return [[self.reduce(sum(x*y for x,y in zip(row,col))) for col in columns] for row in a]
    def vector(self,row,matrix):
        return [self.reduce(sum(x*y for x,y in zip(row,col))) for col in zip(*matrix)]
    def powers(self,matrix,count):
        out=[matrix]
        for _ in range(1,count):out.append(self.product(out[-1],out[-1]))
        return out
    def power(self,powers,exponent):
        out=[[int(i==j) for j in range(self.c)] for i in range(self.c)];bit=0
        while exponent:
            if exponent&1:out=self.product(out,powers[bit])
            exponent>>=1;bit+=1
        return out
    def vector_power(self,row,powers,exponent):
        bit=0
        while exponent:
            if exponent&1:row=self.vector(row,powers[bit])
            exponent>>=1;bit+=1
        return row
    def filtered(self,poly,repeat,residue):
        return sum((poly>>(self.bits*i))&self.digit for i in range(self.q)
                   if repeat*i%self.q==residue)%self.m


def cycle_counts(colors,q,mod,tau,weights,edges,factors,residue):
    n=math.prod(p**e for p,e in factors);lift=2*n*mod
    divisors=[1]
    for p,e in factors:divisors=[d*p**k for d in divisors for k in range(e+1)]
    divisors.sort();ring=CyclicRing(colors,q,lift)
    one=[ring.mono(w) for w in weights];two=[ring.mono(2*w) for w in weights]
    a=[[one[j] if edges[i][j] else 0 for j in range(colors)] for i in range(colors)]
    b=[[two[j] if edges[i][j] else 0 for j in range(colors)] for i in range(colors)]
    pa=ring.powers(a,n.bit_length());pb=pa if a==b else ring.powers(b,n.bit_length())
    fixed=[tau[i]==i for i in range(colors)]
    seam=[int(edges[i][tau[i]]) for i in range(colors)]
    start_fixed=[one[i] if fixed[i] else 0 for i in range(colors)]
    start_seam=[two[i]*seam[i] for i in range(colors)]
    end_fixed=[ring.reduce(sum(a[i][j] for j in range(colors) if fixed[j])) for i in range(colors)]
    words={};reflection_sums={};mirrors={}
    for d in divisors:
        repeat=n//d;matrix=ring.power(pa,d)
        trace=ring.reduce(sum(matrix[i][i] for i in range(colors)))
        words[d]=ring.filtered(trace,repeat,residue)
        if d%2:
            row=ring.vector_power(start_fixed,pb,d//2)
            value=ring.filtered(ring.reduce(sum(x*y for x,y in zip(row,seam))),repeat,residue)
            mirrors[d]=(value,value);reflection_sums[d]=d*value%lift
        else:
            row=ring.vector_power(start_fixed,pb,d//2-1)
            vertex=ring.filtered(ring.reduce(sum(x*y for x,y in zip(row,end_fixed))),repeat,residue)
            row=ring.vector_power(start_seam,pb,d//2-1)
            edge=ring.filtered(ring.reduce(sum(x*y for x,y in zip(row,seam))),repeat,residue)
            mirrors[d]=(vertex,edge);reflection_sums[d]=d//2*(vertex+edge)%lift
    def mu(value):
        sign=1
        for p,_ in factors:
            if value%p==0:
                value//=p;sign=-sign
                if value%p==0:return 0
        return sign
    periods=[]
    for p in divisors:
        exact=reflected=0
        for d in divisors:
            if p%d==0:
                sign=mu(p//d);exact+=sign*words[d]
                reflected+=sign*(p//d)*reflection_sums[d]
        exact%=lift;reflected%=lift
        periods.append({'period':p,'words':exact%mod,'necklaces':exact//p%mod,
                        'bracelets':((exact+reflected)%lift)//(2*p)%mod})
    core={'length':n,'words':words[n]%mod,'necklaces':sum(p['necklaces'] for p in periods)%mod,
          'bracelets':sum(p['bracelets'] for p in periods)%mod,'periods':periods}
    return core,{d:value%mod for d,value in words.items()},tuple(v%mod for v in mirrors[n])


class MirrorMachine:
    def __init__(self,c):
        self.c=c['colors'];self.q=c['inventory_mod'];self.mod=c['mod'];self.tau=c['mirror'][:]
        self.weights=c['weights'][:];self.edges=[row[:] for row in c['edges']]
        self.saved={};self.cache={}
    def state(self):return (tuple(self.weights),tuple(tuple(row) for row in self.edges))
    def execute(self,c,op):
        if op=='orbit':
            key=tuple(tuple(x) for x in c['factors']),c['residue']
            if key not in self.cache:
                if len(self.cache)>=8:self.cache.pop(next(iter(self.cache)))
                self.cache[key]=cycle_counts(self.c,self.q,self.mod,self.tau,self.weights,self.edges,*key)
            core,rotations,mirrors=self.cache[key];n=core['length']
            return dict(core,fixed={'rotations':[rotations[math.gcd(n,k)] for k in c['rotations']],
                                    'mirrors':[mirrors[k%2] for k in c['mirrors']]})
        if op=='weight':
            color=c['color'];value=c['value']
            if self.weights[color]!=value:
                self.weights[color]=self.weights[self.tau[color]]=value;self.cache.clear()
        elif op=='edge':
            u,v,value=c['u'],c['v'],c['value'];changed=False
            for a,b in {(u,v),(v,u),(self.tau[u],self.tau[v]),(self.tau[v],self.tau[u])}:
                if self.edges[a][b]!=value:self.edges[a][b]=value;changed=True
            if changed:self.cache.clear()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            weights,edges=self.saved[c['slot']]
            if (weights,edges)!=self.state():
                self.weights=list(weights);self.edges=[list(row) for row in edges];self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    machines={}
    for line in sys.stdin.buffer:
        if not line.strip():continue
        command=json.loads(line);side,op=command['op'].split('_',1)
        if op=='init':
            machines[side]=(InkMachine if side=='ink' else MirrorMachine)(command);result={'ok':True}
        else:result=machines[side].execute(command,op)
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n')
        sys.stdout.buffer.flush()


if __name__=='__main__':main()
