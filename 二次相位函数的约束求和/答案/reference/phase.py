"""Exact quadratic phase sums over binary affine spaces; standard library."""
import json
import sys


def members(mask):
    while mask:
        bit=mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


class Form:
    def __init__(self,n,linear=None,edges=(),constant=0):
        self.n=n;self.linear=list(linear) if linear is not None else [0]*n
        self.adj=[0]*n;self.constant=constant&3;self.active=(1<<n)-1
        for u,v in edges:self.adj[u]|=1<<v;self.adj[v]|=1<<u

    def clone(self):
        result=Form(self.n);result.linear=self.linear[:];result.adj=self.adj[:]
        result.constant=self.constant;result.active=self.active
        return result

    def xor(self,u,v):
        bitu,bitv=1<<u,1<<v
        neighbors=self.adj[u];e=(neighbors>>v)&1
        self.linear[v]=(self.linear[v]+self.linear[u]+2*e)&3
        affected=neighbors & ~bitv
        self.adj[v]^=affected
        for w in members(affected):self.adj[w]^=bitv
        if self.linear[u]&1:self.adj[u]^=bitv;self.adj[v]^=bitu

    def flip(self,u):
        self.constant=(self.constant+self.linear[u])&3
        self.linear[u]=(-self.linear[u])&3
        for v in members(self.adj[u]):self.linear[v]=(self.linear[v]+2)&3

    def swap(self,u,v):
        if u==v:return
        mask=(1<<u)|(1<<v)
        def perm(row):return row^mask if ((row>>u)^(row>>v))&1 else row
        a,b=self.adj[u],self.adj[v]
        for w in range(self.n):
            if w!=u and w!=v:self.adj[w]=perm(self.adj[w])
        self.adj[u],self.adj[v]=perm(b),perm(a)
        self.linear[u],self.linear[v]=self.linear[v],self.linear[u]

    def substitute(self,u,mask,b):
        """Replace x[u] by b XOR parity(mask), then remove that variable."""
        lu=self.linear[u];V=self.adj[u]&self.active&~(1<<u)
        self.constant=(self.constant+lu*b)&3
        for v in members(mask):
            self.linear[v]=(self.linear[v]+lu*(1-2*b))&3
            if lu&1:self.adj[v]^=mask^(1<<v)
            self.adj[v]^=V&~(1<<v)
        for v in members(V):
            self.linear[v]=(self.linear[v]+2*b)&3
            self.adj[v]^=mask&~(1<<v)
        for v in members(mask&V):self.linear[v]=(self.linear[v]+2)&3
        self.active&=~(1<<u)

    def amplitude(self):
        power=phase=0
        while self.active:
            u=(self.active&-self.active).bit_length()-1
            value=self.linear[u]&3
            neighbors=self.adj[u]&self.active&~(1<<u)
            if value&1:
                phase+=(1 if value==1 else 7);power+=1
                delta=-1 if value==1 else 1
                for v in members(neighbors):
                    self.linear[v]=(self.linear[v]+delta)&3
                    self.adj[v]^=neighbors^(1<<v)
                self.active&=~(1<<u)
            elif not neighbors:
                if value==2:return {'zero':True}
                power+=2;self.active&=~(1<<u)
            else:
                v=(neighbors&-neighbors).bit_length()-1
                self.active&=~(1<<u)
                self.substitute(v,neighbors^(1<<v),value//2)
                power+=2
        return {'zero':False,'power':power,'phase':(phase+2*self.constant)&7}

    def value(self,point):
        value=self.constant
        for u in members(point):
            value+=self.linear[u]+2*((self.adj[u]&point&((1<<u)-1)).bit_count()&1)
        return value&3


def constrained(form,a,b):
    work=form.clone();basis={}
    for text,rhs in zip(a,b):
        mask=int(text,16)
        for pivot in sorted(basis,reverse=True):
            if mask>>pivot&1:
                tail,bit=basis[pivot];mask^=(1<<pivot)|tail;rhs^=bit
        if not mask:
            if rhs:return {'possible':False}
            continue
        pivot=mask.bit_length()-1;tail=mask^(1<<pivot)
        basis[pivot]=(tail,rhs);work.substitute(pivot,tail,rhs)
    first=0
    for pivot,(tail,bit) in sorted(basis.items()):
        first|=(bit^((tail&first).bit_count()&1))<<pivot
    return {'possible':True,'free':form.n-len(basis),
            'first':''.join(str(first>>i&1) for i in range(form.n)),
            'amplitude':work.amplitude()}


class Engine:
    def __init__(self,c):
        self.current=Form(c['n'],c['linear'],c['edges'],c['constant']);self.saved={}

    def execute(self,c):
        op=c['op'];f=self.current
        if op=='ask':return constrained(f,c['a'],c['b'])
        if op=='overlap':
            left,right=self.saved[c['left']],self.saved[c['right']]
            q=Form(f.n,[(x-y)&3 for x,y in zip(left.linear,right.linear)],constant=(left.constant-right.constant)&3)
            q.adj=[x^y for x,y in zip(left.adj,right.adj)]
            return constrained(q,c['a'],c['b'])
        if op=='value':
            point=sum((x=='1')<<i for i,x in enumerate(c['bits']))
            return {'phase':f.value(point)}
        if op=='phase':f.linear[c['u']]=(f.linear[c['u']]+c['delta'])&3
        elif op=='global':f.constant=(f.constant+c['delta'])&3
        elif op=='cz':
            u,v=c['u'],c['v'];f.adj[u]^=1<<v;f.adj[v]^=1<<u
        elif op=='flip':f.flip(c['u'])
        elif op=='xor':f.xor(c['dst'],c['src'])
        elif op=='swap':f.swap(c['u'],c['v'])
        elif op=='save':self.saved[c['slot']]=f.clone()
        elif op=='load':self.current=self.saved[c['slot']].clone()
        else:raise AssertionError(op)
        return {'ok':True}


def main():
    engine=None
    for line in sys.stdin.buffer:
        c=json.loads(line)
        if c['op']=='init':engine=Engine(c);reply={'ok':True}
        else:reply=engine.execute(c)
        sys.stdout.buffer.write(json.dumps(reply,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
