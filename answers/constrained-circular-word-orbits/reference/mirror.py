"""Private reference: cyclic group algebra + divisor inversion, no third parties."""
import json
import math
import sys


class Algebra:
    def __init__(self, size, degree, modulus):
        self.s=size;self.q=degree;self.mod=modulus
        self.width=2*modulus.bit_length()+(size*degree).bit_length()+1
        self.mask=(1<<self.width)-1
        self.wrap=self.width*degree;self.low=(1<<self.wrap)-1
    def monomial(self,degree):return 1<<(self.width*(degree%self.q))
    def reduce(self,value):
        value=(value&self.low)+(value>>self.wrap)
        result=0
        for i in range(self.q):
            result|=((value&self.mask)%self.mod)<<(self.width*i)
            value>>=self.width
        return result
    def coefficients(self,value):
        return [(value>>(self.width*i))&self.mask for i in range(self.q)]
    def multiply(self,left,right):
        columns=list(zip(*right));out=[]
        for row in left:
            out.append([self.reduce(sum(x*y for x,y in zip(row,col))) for col in columns])
        return out
    def vector_multiply(self,row,matrix):
        return [self.reduce(sum(x*y for x,y in zip(row,col))) for col in zip(*matrix)]
    def powers(self,matrix,bits):
        result=[matrix]
        for _ in range(1,bits):result.append(self.multiply(result[-1],result[-1]))
        return result
    def power(self,powers,exponent):
        result=[[int(i==j) for j in range(self.s)] for i in range(self.s)]
        k=0
        while exponent:
            if exponent&1:result=self.multiply(result,powers[k])
            exponent>>=1;k+=1
        return result
    def vector_power(self,row,powers,exponent):
        k=0
        while exponent:
            if exponent&1:row=self.vector_multiply(row,powers[k])
            exponent>>=1;k+=1
        return row


def solve(s,q,mod,tau,weights,edges,factors,residue):
    n=math.prod(p**e for p,e in factors)
    divisors=[1]
    for p,e in factors:
        divisors=[d*p**j for d in divisors for j in range(e+1)]
    divisors.sort()
    lifted=2*n*mod
    ring=Algebra(s,q,lifted)
    m1=[ring.monomial(w) for w in weights]
    m2=[ring.monomial(2*w) for w in weights]
    a=[[m1[j] if edges[i][j] else 0 for j in range(s)] for i in range(s)]
    b=[[m2[j] if edges[i][j] else 0 for j in range(s)] for i in range(s)]
    ap=ring.powers(a,n.bit_length())
    bp=ap if a==b else ring.powers(b,n.bit_length())
    fixed=[tau[i]==i for i in range(s)]
    seam=[int(edges[i][tau[i]]) for i in range(s)]
    fixed_start=[m1[i] if fixed[i] else 0 for i in range(s)]
    seam_start=[m2[i]*seam[i] for i in range(s)]
    fixed_end=[ring.reduce(sum(a[i][j] for j in range(s) if fixed[j])) for i in range(s)]
    def filter_residue(poly,repeat):
        return sum(c for k,c in enumerate(ring.coefficients(poly))
                   if repeat*k%q==residue)%lifted
    counts={};mirror_sums={};single_mirrors={}
    for d in divisors:
        repeat=n//d
        matrix=ring.power(ap,d)
        trace=ring.reduce(sum(matrix[i][i] for i in range(s)))
        counts[d]=filter_residue(trace,repeat)
        if d&1:
            row=ring.vector_power(fixed_start,bp,d//2)
            poly=ring.reduce(sum(x*y for x,y in zip(row,seam)))
            value=filter_residue(poly,repeat)
            mirror_sums[d]=d*value%lifted;single_mirrors[d]=(value,value)
        else:
            exponent=d//2-1
            row=ring.vector_power(fixed_start,bp,exponent)
            vertex=filter_residue(ring.reduce(sum(x*y for x,y in zip(row,fixed_end))),repeat)
            row=ring.vector_power(seam_start,bp,exponent)
            edge=filter_residue(ring.reduce(sum(x*y for x,y in zip(row,seam))),repeat)
            mirror_sums[d]=(d//2)*(vertex+edge)%lifted
            single_mirrors[d]=(vertex,edge)
    def mobius(value):
        result=1
        for p,_ in factors:
            if value%p==0:
                value//=p;result=-result
                if value%p==0:return 0
        return result
    periods=[]
    for p in divisors:
        exact=reflection=0
        for d in divisors:
            if p%d==0:
                mu=mobius(p//d)
                exact+=mu*counts[d]
                reflection+=mu*(p//d)*mirror_sums[d]
        exact%=lifted;reflection%=lifted
        assert exact%p==0
        orbit_numerator=(exact+reflection)%lifted
        assert orbit_numerator%(2*p)==0
        periods.append({'period':p,'words':exact%mod,
                        'necklaces':exact//p%mod,'bracelets':orbit_numerator//(2*p)%mod})
    core={'length':n,'words':counts[n]%mod,
          'necklaces':sum(row['necklaces'] for row in periods)%mod,
          'bracelets':sum(row['bracelets'] for row in periods)%mod,'periods':periods}
    assert sum(row['words'] for row in periods)%mod==core['words']
    return core,{d:v%mod for d,v in counts.items()},tuple(v%mod for v in single_mirrors[n])


class Engine:
    def __init__(self,c):
        self.s=c['colors'];self.q=c['inventory_mod'];self.mod=c['mod'];self.tau=c['mirror'][:]
        self.weights=c['weights'][:];self.edges=[row[:] for row in c['edges']]
        self.saved={};self.cache={}
    def execute(self,c):
        op=c['op']
        if op=='orbit':
            key=tuple(tuple(x) for x in c['factors']),c['residue']
            if key not in self.cache:
                if len(self.cache)>=8:self.cache.pop(next(iter(self.cache)))
                self.cache[key]=solve(self.s,self.q,self.mod,self.tau,self.weights,self.edges,*key)
            core,rotations,mirrors=self.cache[key];n=core['length']
            return dict(core,fixed={'rotations':[rotations[math.gcd(n,k)] for k in c['rotations']],
                                    'mirrors':[mirrors[k%2] for k in c['mirrors']]})
        if op=='edge':
            u,v=c['u'],c['v'];value=c['value'];changed=False
            for a,b in {(u,v),(v,u),(self.tau[u],self.tau[v]),(self.tau[v],self.tau[u])}:
                if self.edges[a][b]!=value:changed=True;self.edges[a][b]=value
            if changed:self.cache.clear()
        elif op=='weight':
            a=c['color'];value=c['value']
            if self.weights[a]!=value:
                self.weights[a]=self.weights[self.tau[a]]=value;self.cache.clear()
        elif op=='save':self.saved[c['slot']]=(self.weights[:],[r[:] for r in self.edges])
        elif op=='load':
            weights,edges=self.saved[c['slot']]
            if self.weights!=weights or self.edges!=edges:
                self.weights=weights[:];self.edges=[r[:] for r in edges];self.cache.clear()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    engine=None
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='init':engine=Engine(c);out={'ok':True}
        else:out=engine.execute(c)
        sys.stdout.buffer.write(json.dumps(out,separators=(',',':')).encode()+b'\n')
        sys.stdout.buffer.flush()


if __name__=='__main__':main()
