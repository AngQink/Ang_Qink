"""Exact weighted derivations, infinite optimal ambiguity, compact witnesses."""
import hashlib
import heapq
import json
import sys
from collections import deque


def inside(edges,vertices,unit=False):
    reverse=[[] for _ in range(vertices)]
    pending=[];score=[];best=[None]*vertices;done=[False]*vertices;queue=[];order=[]
    for e,(head,tails,cost,rid) in enumerate(edges):
        pending.append(len(tails));value=1 if unit else cost;score.append(value)
        if not tails:
            if best[head] is None or value<best[head]:best[head]=value;heapq.heappush(queue,(value,head))
        for child in tails:reverse[child].append(e)
    while queue:
        value,u=heapq.heappop(queue)
        if done[u] or value!=best[u]:continue
        done[u]=True;order.append(u)
        for e in reverse[u]:
            pending[e]-=1;score[e]+=value
            if pending[e]==0:
                head=edges[e][0];candidate=score[e]
                if not done[head] and (best[head] is None or candidate<best[head]):
                    best[head]=candidate;heapq.heappush(queue,(candidate,head))
    return best,order


def parse(n,rules,mod,start,word,indices):
    z=len(word)+1;vertices=n*z*z
    def node(a,i,j):return (a*z+i)*z+j
    edges=[]
    for rule in rules:
        if not rule['enabled']:continue
        A=rule['lhs'];rhs=rule['rhs'];cost=rule['cost'];rid=rule['id']
        if not rhs:
            for i in range(z):edges.append((node(A,i,i),(),cost,rid))
        elif isinstance(rhs[0],str):
            for i,char in enumerate(word):
                if char==rhs[0]:edges.append((node(A,i,i+1),(),cost,rid))
        elif len(rhs)==1:
            B=rhs[0]
            for i in range(z):
                for j in range(i,z):edges.append((node(A,i,j),(node(B,i,j),),cost,rid))
        else:
            B,C=rhs
            for i in range(z):
                for j in range(i,z):
                    head=node(A,i,j)
                    for k in range(i,j+1):edges.append((head,(node(B,i,k),node(C,k,j)),cost,rid))
    root=node(start,0,len(word));costs,_=inside(edges,vertices)
    if costs[root] is None:return {'possible':False}
    outgoing=[[] for _ in range(vertices)]
    for edge in edges:
        head,tails,cost,rid=edge
        if costs[head] is not None and all(costs[t] is not None for t in tails) and cost+sum(costs[t] for t in tails)==costs[head]:outgoing[head].append(edge)
    reachable={root};stack=[root];tight=[]
    while stack:
        u=stack.pop()
        for edge in outgoing[u]:
            tight.append(edge)
            for child in edge[1]:
                if child not in reachable:reachable.add(child);stack.append(child)
    # Counts use every minimum-cost edge, even when it is not part of the
    # secondary minimum-node witness. A reachable productive cycle pumps.
    dependencies={u:0 for u in reachable};parents={u:[] for u in reachable}
    for head,tails,_,rid in tight:
        dependencies[head]+=len(tails)
        for child in tails:parents[child].append(head)
    ready=deque(u for u in reachable if dependencies[u]==0);count=[0]*vertices;processed=0
    while ready:
        u=ready.popleft();processed+=1;value=0
        for _,tails,_,rid in outgoing[u]:
            ways=1
            for child in tails:ways=ways*count[child]%mod
            value=(value+ways)%mod
        count[u]=value
        for parent in parents[u]:
            dependencies[parent]-=1
            if dependencies[parent]==0:ready.append(parent)
    infinite=processed!=len(reachable)
    sizes,order=inside(tight,vertices,unit=True)
    chosen=[0]*vertices;pool=[None];intern={}
    # Every witness child has strictly fewer nodes than its parent, so the
    # positive-node-cost order remains valid even if optimal costs have cycles.
    def compare(a,b):
        while a!=b:
            A,B=pool[a],pool[b]
            if A[0]!=B[0]:return -1 if A[0]<B[0] else 1
            for x,y in zip(A[1],B[1]):
                if x!=y:a,b=x,y;break
            else:raise AssertionError('non-interned equal witnesses')
        return 0
    for u in order:
        best=None
        for _,tails,_,rid in outgoing[u]:
            if 1+sum(sizes[t] for t in tails)!=sizes[u]:continue
            children=tuple(chosen[t] for t in tails);key=(rid,children)
            better=best is None or rid<best[0]
            if best is not None and rid==best[0]:
                for a,b in zip(children,best[1]):
                    if a!=b:better=compare(a,b)<0;break
            if better:best=key
        assert best is not None
        if best not in intern:
            rid,children=best
            payload=b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(children)])+b''.join(pool[t][3] for t in children)
            intern[best]=len(pool);pool.append((rid,children,1+sum(pool[t][2] for t in children),hashlib.sha256(payload).digest()))
        chosen[u]=intern[best]
    witness=chosen[root]
    def select(index):
        if index>=pool[witness][2]:return None
        u=witness
        while True:
            rid,children,_,_=pool[u]
            if index==0:return rid
            index-=1
            for child in children:
                if index<pool[child][2]:u=child;break
                index-=pool[child][2]
            else:raise AssertionError('invalid witness index')
    return {'possible':True,'cost':costs[root],'infinite':infinite,'ways':None if infinite else count[root],
            'witness':{'nodes':pool[witness][2],'sha256':pool[witness][3].hex(),'at':[select(i) for i in indices]}}


class Engine:
    def __init__(self,c):
        self.n=c['nonterminals'];self.mod=c['mod'];self.rules=[dict(r,rhs=r['rhs'][:]) for r in c['rules']]
        self.lookup={r['id']:i for i,r in enumerate(self.rules)};self.saved={}
    def execute(self,c):
        op=c['op']
        if op=='parse':return parse(self.n,self.rules,self.mod,c['start'],c['word'],c['at'])
        if op=='weight':self.rules[self.lookup[c['id']]]['cost']=c['cost']
        elif op=='enable':self.rules[self.lookup[c['id']]]['enabled']=c['value']
        elif op=='save':self.saved[c['slot']]=[(r['cost'],r['enabled']) for r in self.rules]
        elif op=='load':
            for r,(cost,enabled) in zip(self.rules,self.saved[c['slot']]):r['cost']=cost;r['enabled']=enabled
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    e=None
    for line in sys.stdin.buffer:
        c=json.loads(line)
        if c['op']=='init':e=Engine(c);result={'ok':True}
        else:result=e.execute(c)
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
