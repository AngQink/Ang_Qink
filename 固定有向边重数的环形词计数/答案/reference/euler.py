"""Count circular words with prescribed directed edge multiplicities."""
import hashlib
import json
import math
import sys
from array import array

MAX_LENGTH=200000


def determinant(matrix):
    a=[row[:] for row in matrix];n=len(a)
    if n==0:return 1
    sign=1;previous=1
    for k in range(n-1):
        if a[k][k]==0:
            pivot=next((i for i in range(k+1,n) if a[i][k]),None)
            if pivot is None:return 0
            a[k],a[pivot]=a[pivot],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):a[i][j]=(a[i][j]*pivot-a[i][k]*a[k][j])//previous
        for i in range(k+1,n):a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def tree_number(edges,root):
    active=[i for i in range(len(edges)) if i==root or any(edges[i]) or any(row[i] for row in edges)]
    others=[i for i in active if i!=root]
    minor=[[sum(edges[i][j] for j in active if j!=i) if i==j else -edges[i][j]
            for j in others] for i in others]
    return determinant(minor)


class PrimeTable:
    def __init__(self,p,a):
        self.p=p;self.a=a;self.output_mod=p**a
        bound=1;extra=0
        while bound*p<=MAX_LENGTH:bound*=p;extra+=1
        self.exponent=a+extra;self.precision=self.output_mod*bound
        self.unit=array('Q',[1]);self.valuation=array('I',[0])
        value=1;exponent=0
        for k in range(1,MAX_LENGTH+1):
            x=k
            while x%p==0:x//=p;exponent+=1
            value=value*x%self.precision
            self.unit.append(value);self.valuation.append(exponent)
    def quotient(self,scalar,numerators,denominators):
        if scalar==0:return 0
        assert scalar>0
        p=self.p;v=0
        while scalar%p==0:scalar//=p;v+=1
        v+=sum(self.valuation[x] for x in numerators)-sum(self.valuation[x] for x in denominators)
        assert v>=0, 'integer combinatorial quotient'
        if v>=self.exponent:return 0
        numerator=scalar%self.precision;denominator=1
        for x in numerators:numerator=numerator*self.unit[x]%self.precision
        for x in denominators:denominator=denominator*self.unit[x]%self.precision
        return numerator*pow(denominator,-1,self.precision)*pow(p,v,self.precision)%self.precision
    def divide(self,value,divisor):
        p=self.p;power=1
        while divisor%p==0:divisor//=p;power*=p
        assert value%power==0
        return (value//power)*pow(divisor,-1,self.output_mod)%self.output_mod


class Machine:
    def __init__(self,c):
        self.size=c['vertices'];self.edges=[row[:] for row in c['edges']]
        self.tables=[PrimeTable(p,a) for p,a in c['mod_factors']]
        self.mod=math.prod(t.output_mod for t in self.tables)
        self.crt=[self.mod//t.output_mod*pow(self.mod//t.output_mod,-1,t.output_mod)%self.mod for t in self.tables]
        self.saved={};self.clear()
    def clear(self):self.core=None;self.word=None;self.prefix_cache={}
    def combine(self,values):return sum(c*(v%t.output_mod) for c,v,t in zip(self.crt,values,self.tables))%self.mod
    def state(self):return tuple(tuple(row) for row in self.edges)
    def analyze(self,factors):
        if self.core is not None:return
        n=sum(map(sum,self.edges));assert 1<=n<=MAX_LENGTH
        degree=[sum(row) for row in self.edges];active=[i for i,d in enumerate(degree) if d]
        root=active[0];tree=tree_number(self.edges,root);assert tree>=0
        g=math.gcd(*(x for row in self.edges for x in row));assert g==math.prod(p**e for p,e in factors)
        repeats=[1]
        for p,e in factors:repeats=[r*p**j for r in repeats for j in range(e+1)]
        repeats.sort(reverse=True)
        base={};exact={};rows=[]
        for r in repeats:
            numerators=[degree[i]//r-1 for i in active]
            denominators=[x//r for row in self.edges for x in row if x]
            scaled_tree=tree//r**(len(active)-1)
            assert tree%r**(len(active)-1)==0
            base[r]=[t.quotient(n//r*scaled_tree,numerators,denominators) for t in self.tables]
            exact[r]=[(v-sum(exact[s][i] for s in repeats if s>r and s%r==0))%t.precision
                      for i,(t,v) in enumerate(zip(self.tables,base[r]))]
            period=n//r
            rows.append({'period':period,'words':self.combine(exact[r]),
                         'necklaces':self.combine([t.divide(v,period) for t,v in zip(self.tables,exact[r])])})
        self.base=base;self.length=n;self.possible=tree>0
        self.core={'possible':self.possible,'length':n,'words':self.combine(base[1]),
                   'necklaces':sum(row['necklaces'] for row in rows)%self.mod,'periods':rows}
    def canonical(self):
        if self.word is not None:return self.word
        remaining=[row[:] for row in self.edges]
        start=next(i for i,row in enumerate(remaining) if any(row))
        pointers=[0]*self.size;stack=[start];postorder=[]
        while stack:
            u=stack[-1];v=pointers[u]
            while v<self.size and remaining[u][v]==0:v+=1
            pointers[u]=v
            if v==self.size:postorder.append(stack.pop())
            else:remaining[u][v]-=1;stack.append(v)
        path=bytes(reversed(postorder));assert len(path)==self.length+1 and path[0]==path[-1]
        self.word=path[:-1];return self.word
    def prefix_count(self,prefix):
        key=tuple(prefix)
        if key in self.prefix_cache:return self.prefix_cache[key]
        if not prefix:return self.core['words']
        if len(prefix)>self.length or not self.possible:return 0
        remaining=[row[:] for row in self.edges]
        for a,b in zip(prefix,prefix[1:]):
            if remaining[a][b]==0:return 0
            remaining[a][b]-=1
        target=prefix[0];tree=tree_number(remaining,target)
        if tree==0:return 0
        degree=[sum(row) for row in remaining]
        active=[i for i in range(self.size) if i==target or degree[i] or any(row[i] for row in remaining)]
        numerators=[degree[i]-1+int(i==target) for i in active]
        if min(numerators)<0:return 0
        denominators=[x for row in remaining for x in row if x]
        value=self.combine([t.quotient(tree,numerators,denominators) for t in self.tables])
        if len(self.prefix_cache)>=256:self.prefix_cache.pop(next(iter(self.prefix_cache)))
        self.prefix_cache[key]=value
        return value
    def execute(self,c):
        op=c['op']
        if op=='count':
            self.analyze(c['gcd_factors']);n=self.length;word=self.canonical() if self.possible else None
            result=dict(self.core)
            result['fixed_rotations']=[self.combine(self.base[r]) if (r:=n//math.gcd(n,k)) in self.base else 0 for k in c['rotations']]
            result['prefix_counts']=[self.prefix_count(p) for p in c['prefixes']]
            result['witness']=None if word is None else {
                'sha256':hashlib.sha256(b'EULER1'+n.to_bytes(8,'little')+word).hexdigest(),
                'at':[word[k] if k<n else None for k in c['at']]}
            return result
        if op=='cycle':
            vertices=c['vertices'];delta=c['delta']
            if delta:
                for a,b in zip(vertices,vertices[1:]+vertices[:1]):self.edges[a][b]+=delta
                self.clear()
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            state=self.saved[c['slot']]
            if state!=self.state():self.edges=[list(row) for row in state];self.clear()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    machine=None
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='init':machine=Machine(c);result={'ok':True}
        else:result=machine.execute(c)
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
