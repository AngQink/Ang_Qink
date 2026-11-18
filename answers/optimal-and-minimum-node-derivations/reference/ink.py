"""Compute minimum derivation costs, both counts, and compact witnesses."""
import hashlib
import heapq
import json
import sys
from collections import deque


class Answer:
    __slots__=('cost','size','minways','infinite','ways','root','trees')
    def __init__(self,cost=None,size=0,minways=0,infinite=False,ways=0,root=0,trees=None):
        self.cost=cost;self.size=size;self.minways=minways;self.infinite=infinite
        self.ways=ways;self.root=root;self.trees=trees
    def select(self,index):
        if index>=self.size:return None
        node=self.root
        while True:
            rid,children,_,_=self.trees[node]
            if index==0:return rid
            index-=1
            for child in children:
                if index<self.trees[child][2]:node=child;break
                index-=self.trees[child][2]
            else:raise AssertionError('invalid preorder index')
    def response(self,command):
        if self.cost is None:return {'possible':False}
        if command['op']=='minways':return {'possible':True,'nodes':self.size,'ways':self.minways}
        return {'possible':True,'cost':self.cost,'infinite':self.infinite,'ways':self.ways,
                'witness':{'nodes':self.size,'sha256':self.trees[self.root][3].hex(),
                           'at':[self.select(i) for i in command['at']]}}


def evaluate(n,rules,mod,start,word):
    z=len(word)+1;V=n*z*z
    def item(A,i,j):return (A*z+i)*z+j
    edges=[]
    for rule in rules:
        if not rule['enabled']:continue
        A=rule['lhs'];rhs=rule['rhs'];w=rule['cost'];rid=rule['id']
        if not rhs:
            for i in range(z):edges.append((item(A,i,i),(),w,rid))
        elif isinstance(rhs[0],str):
            for i,ch in enumerate(word):
                if ch==rhs[0]:edges.append((item(A,i,i+1),(),w,rid))
        elif len(rhs)==1:
            B=rhs[0]
            for i in range(z):
                for j in range(i,z):edges.append((item(A,i,j),(item(B,i,j),),w,rid))
        else:
            B,C=rhs
            for i in range(z):
                for j in range(i,z):
                    head=item(A,i,j)
                    for k in range(i,j+1):edges.append((head,(item(B,i,k),item(C,k,j)),w,rid))
    # Lexicographic (cost, node count) is strictly larger than every child:
    # nonnegative costs, and one positive production-node contribution.
    reverse=[[] for _ in range(V)];remaining=[];acc_cost=[];acc_size=[];acc_ways=[]
    best=[None]*V;shortways=[0]*V;keys=[None]*V;done=[False]*V;chosen=[0]*V
    heap=[];trees=[None];intern={}
    def tree_less(a,b):
        while a!=b:
            A,B=trees[a],trees[b]
            if A[0]!=B[0]:return A[0]<B[0]
            for x,y in zip(A[1],B[1]):
                if x!=y:a,b=x,y;break
            else:raise AssertionError('equal uninterned trees')
        return False
    def key_less(a,b):
        if a[0]!=b[0]:return a[0]<b[0]
        for x,y in zip(a[1],b[1]):
            if x!=y:return tree_less(x,y)
        return False
    def offer(head,cost,size,ways,rid,children):
        if done[head]:return
        candidate=(cost,size);old=best[head]
        if old is None or candidate<old:
            best[head]=candidate;shortways[head]=ways%mod;keys[head]=(rid,children)
            heapq.heappush(heap,(cost,size,head))
        elif candidate==old:
            shortways[head]=(shortways[head]+ways)%mod
            key=(rid,children)
            if key_less(key,keys[head]):keys[head]=key
    for e,(head,tails,cost,rid) in enumerate(edges):
        remaining.append(len(tails));acc_cost.append(cost);acc_size.append(1);acc_ways.append(1)
        if not tails:offer(head,cost,1,1,rid,())
        for t in tails:reverse[t].append(e)
    while heap:
        cost,size,u=heapq.heappop(heap)
        if done[u] or best[u]!=(cost,size):continue
        done[u]=True;key=keys[u]
        if key not in intern:
            rid,kids=key
            payload=b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(kids)])+b''.join(trees[t][3] for t in kids)
            intern[key]=len(trees);trees.append((rid,kids,size,hashlib.sha256(payload).digest()))
        chosen[u]=intern[key]
        for e in reverse[u]:
            remaining[e]-=1;acc_cost[e]+=cost;acc_size[e]+=size
            acc_ways[e]=acc_ways[e]*shortways[u]%mod
            if remaining[e]==0:
                head,tails,_,rid=edges[e]
                offer(head,acc_cost[e],acc_size[e],acc_ways[e],rid,tuple(chosen[t] for t in tails))
    root=item(start,0,len(word))
    if best[root] is None:return Answer()
    # Reconstruct every primary-cost-tight alternative. This deliberately
    # includes trees larger than the minimum-node witness and zero-cost loops.
    outgoing=[[] for _ in range(V)]
    for head,tails,cost,rid in edges:
        if best[head] is not None and all(best[t] is not None for t in tails) and cost+sum(best[t][0] for t in tails)==best[head][0]:outgoing[head].append(tails)
    reachable={root};stack=[root]
    while stack:
        u=stack.pop()
        for tails in outgoing[u]:
            for t in tails:
                if t not in reachable:reachable.add(t);stack.append(t)
    pending={u:0 for u in reachable};parents={u:[] for u in reachable}
    for u in reachable:
        for tails in outgoing[u]:
            pending[u]+=len(tails)
            for t in tails:parents[t].append(u)
    ready=deque(u for u in reachable if pending[u]==0);allways={};processed=0
    while ready:
        u=ready.popleft();processed+=1;total=0
        for tails in outgoing[u]:
            value=1
            for t in tails:value=value*allways[t]%mod
            total=(total+value)%mod
        allways[u]=total
        for p in parents[u]:
            pending[p]-=1
            if pending[p]==0:ready.append(p)
    infinite=processed!=len(reachable)
    return Answer(best[root][0],best[root][1],shortways[root],infinite,
                  None if infinite else allways[root],chosen[root],trees)


class Engine:
    def __init__(self,command):
        self.n=command['nonterminals'];self.mod=command['mod']
        self.rules=[dict(r,rhs=r['rhs'][:]) for r in command['rules']]
        self.lookup={r['id']:r for r in self.rules};self.snapshots={};self.cache={}
    def execute(self,c):
        op=c['op']
        if op in ('parse','minways'):
            key=c['start'],c['word']
            if key not in self.cache:
                answer=evaluate(self.n,self.rules,self.mod,*key)
                if len(self.cache)>=8:self.cache.pop(next(iter(self.cache)))
                self.cache[key]=answer
            return self.cache[key].response(c)
        if op=='weight':
            r=self.lookup[c['id']]
            if r['cost']!=c['cost']:r['cost']=c['cost'];self.cache.clear()
        elif op=='enable':
            r=self.lookup[c['id']]
            if r['enabled']!=c['value']:r['enabled']=c['value'];self.cache.clear()
        elif op=='save':self.snapshots[c['slot']]=tuple((r['cost'],r['enabled']) for r in self.rules)
        elif op=='load':
            state=self.snapshots[c['slot']]
            if state!=tuple((r['cost'],r['enabled']) for r in self.rules):
                for r,(cost,enabled) in zip(self.rules,state):r['cost']=cost;r['enabled']=enabled
                self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    engine=None
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='init':engine=Engine(c);reply={'ok':True}
        else:reply=engine.execute(c)
        sys.stdout.buffer.write(json.dumps(reply,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
