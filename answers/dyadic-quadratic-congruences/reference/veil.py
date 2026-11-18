"""Private reference: exact dyadic quadratic Gauss sums, no floating point."""
import hashlib
import json
import sys


def normal_form(bits,matrix,linear,constant):
    fullmask=(1<<bits)-1
    a=[[x&fullmask for x in row] for row in matrix];b=[x&fullmask for x in linear]
    constant&=fullmask;scale=0;blocks=[];free=0;tail=0;tail_level=bits
    while a:
        n=len(a);active=[i for i in range(n) if b[i] or any(a[i])]
        if len(active)!=n:
            free+=n-len(active);a=[[a[i][j] for j in active] for i in active];b=[b[i] for i in active]
            if not a:break
            n=len(a)
        joined=0
        for row in a:
            for value in row:joined|=value
        for value in b:joined|=value
        shift=(joined&-joined).bit_length()-1
        if shift:
            a=[[x>>shift for x in row] for row in a];b=[x>>shift for x in b];scale+=shift
        modulus=1<<(bits-scale);mask=modulus-1
        pair=next(((i,j) for i in range(n) for j in range(i+1,n) if a[i][j]&1),None)
        if pair is not None:
            i,j=pair;u,v,w=a[i][i],a[i][j],a[j][j]
            other=[t for t in range(n) if t not in pair]
            left=[b[i]]+[a[i][t] for t in other];right=[b[j]]+[a[j][t] for t in other]
            inverse=pow(4*u*w-v*v,-1,modulus)
            alpha=[(2*w*x-v*y)*inverse&mask for x,y in zip(left,right)]
            beta=[(-v*x+2*u*y)*inverse&mask for x,y in zip(left,right)]
            c0=u*alpha[0]**2+v*alpha[0]*beta[0]+w*beta[0]**2
            constant=(constant-(c0<<scale))&fullmask
            newb=[];newa=[[0]*len(other) for _ in other]
            for r,t in enumerate(other,1):
                newb.append((b[t]-2*u*alpha[0]*alpha[r]-v*(alpha[0]*beta[r]+beta[0]*alpha[r])-2*w*beta[0]*beta[r])&mask)
                newa[r-1][r-1]=(a[t][t]-u*alpha[r]**2-v*alpha[r]*beta[r]-w*beta[r]**2)&mask
                for s,z in enumerate(other[r:],r+1):
                    value=(a[t][z]-2*u*alpha[r]*alpha[s]-v*(alpha[r]*beta[s]+alpha[s]*beta[r])-2*w*beta[r]*beta[s])&mask
                    newa[r-1][s-1]=newa[s-1][r-1]=value
            blocks.append((scale,2,-1 if u&1 and w&1 else 1));a,b=newa,newb
            continue
        if any(x&1 for x in b):
            tail=n;tail_level=scale+int(all((a[i][i]+b[i])%2==0 for i in range(n)))
            break
        i=next(i for i in range(n) if a[i][i]&1);unit=a[i][i]
        other=[t for t in range(n) if t!=i];inverse=pow(unit,-1,modulus)
        h=[(b[i]//2)*inverse&mask]+[(a[i][t]//2)*inverse&mask for t in other]
        constant=(constant-((unit*h[0]*h[0])<<scale))&fullmask
        newb=[(b[t]-2*unit*h[0]*h[r])&mask for r,t in enumerate(other,1)]
        newa=[[0]*len(other) for _ in other]
        for r,t in enumerate(other,1):
            newa[r-1][r-1]=(a[t][t]-unit*h[r]*h[r])&mask
            for s,z in enumerate(other[r:],r+1):
                newa[r-1][s-1]=newa[s-1][r-1]=(a[t][z]-2*unit*h[r]*h[s])&mask
        blocks.append((scale,1,unit&7));a,b=newa,newb
    return constant,blocks,free,tail,tail_level


def shift_root(poly,power):
    power&=7;out=[0,0,0,0]
    for i,x in enumerate(poly):
        k=(i+power)&7
        out[k&3]+=x if k<4 else -x
    return tuple(out)


class Analyzer:
    def __init__(self,bits,matrix,linear,constant):
        self.bits=bits;self.dimension=len(matrix)
        self.constant,self.blocks,self.free,self.tail,self.tail_level=normal_form(bits,matrix,linear,constant)
    def count(self,target):
        k=self.bits;t=(target-self.constant)&((1<<k)-1)
        numerator=1<<(k*self.dimension)
        for level in range(1,k+1):
            if self.tail and level>self.tail_level:continue
            if level>=3 and t&((1<<(level-3))-1):continue
            exponent=k*(self.free+self.tail);sign=1;phases=[];zero=False
            for scale,kind,unit in self.blocks:
                effective=level-scale
                if effective<=0:exponent+=k*kind
                elif kind==2:
                    exponent+=2*k-effective
                    if unit==-1 and effective&1:sign=-sign
                elif effective==1:zero=True;break
                elif effective&1:
                    exponent+=k-(effective-1)//2;phases.append((1,unit))
                else:
                    exponent+=k-effective//2;phases.append((2,unit))
            if zero:continue
            trace=[0,0,0,0]
            units=(1,) if level==1 else (1,3) if level==2 else (1,3,5,7)
            for u in units:
                poly=(1,0,0,0)
                for kind,unit in phases:
                    shifted=shift_root(poly,kind*unit*u)
                    poly=shifted if kind==1 else tuple(x+y for x,y in zip(poly,shifted))
                power=-u*(t>>(level-3)) if level>=3 else -u*t*(1<<(3-level))
                poly=shift_root(poly,power)
                for i,x in enumerate(poly):trace[i]+=x
            assert trace[1:]==[0,0,0], 'rational cyclotomic trace'
            numerator+=sign*trace[0]*(1<<(exponent+max(0,level-3)))
        denominator=1<<k
        assert numerator%denominator==0
        count=numerator//denominator
        assert 0<=count<=1<<(k*self.dimension)
        return count


class Machine:
    def __init__(self,c):
        self.n=c['variables'];self.k=c['bits'];self.mask=(1<<self.k)-1
        self.a=[[c['q'][min(i,j)][max(i,j)]&self.mask for j in range(self.n)] for i in range(self.n)]
        self.b=[x&self.mask for x in c['linear']];self.c=c['constant']&self.mask
        self.saved={};self.cache={}
    def state(self):return tuple(tuple(r) for r in self.a),tuple(self.b),self.c
    def evaluate(self,values):
        return (self.c+sum(self.b[i]*values[i]+self.a[i][i]*values[i]**2 for i in range(self.n))+
                sum(self.a[i][j]*values[i]*values[j] for i in range(self.n) for j in range(i+1,self.n)))&self.mask
    def count(self,target,locks):
        key=target,tuple(tuple(pair) for pair in locks)
        if key in self.cache:return self.cache[key]
        values=[pair[1] for pair in locks];scale=[1<<pair[0] for pair in locks]
        constant=self.c+sum(self.b[i]*values[i]+self.a[i][i]*values[i]**2 for i in range(self.n))
        constant+=sum(self.a[i][j]*values[i]*values[j] for i in range(self.n) for j in range(i+1,self.n))
        matrix=[[self.a[i][j]*scale[i]*scale[j]&self.mask for j in range(self.n)] for i in range(self.n)]
        linear=[scale[i]*(self.b[i]+2*self.a[i][i]*values[i]+sum(self.a[i][j]*values[j] for j in range(self.n) if j!=i))&self.mask for i in range(self.n)]
        total=Analyzer(self.k,matrix,linear,constant).count(target)
        redundancy=1<<sum(pair[0] for pair in locks)
        assert total%redundancy==0
        answer=total//redundancy
        if len(self.cache)>=1024:self.cache.pop(next(iter(self.cache)))
        self.cache[key]=answer;return answer
    def execute(self,c):
        op=c['op']
        if op=='solve':
            target=c['target'];locks=[pair[:] for pair in c['locks']];total=self.count(target,locks)
            witness=None
            if total and c['witness']:
                for bit in range(self.k):
                    for i in range(self.n):
                        if locks[i][0]>bit:continue
                        locks[i][0]=bit+1
                        if self.count(target,locks)==0:locks[i][1]|=1<<bit
                values=[pair[1] for pair in locks];assert self.evaluate(values)==target
                payload=b'DYAD1'+bytes([self.n,self.k])+b''.join(x.to_bytes((self.k+7)//8,'little') for x in values)
                witness={'values':values,'sha256':hashlib.sha256(payload).hexdigest()}
            return {'possible':total>0,'count':total,'witness':witness}
        changed=False
        if op=='quad':
            i,j,value=c['i'],c['j'],c['value']&self.mask
            if self.a[i][j]!=value:self.a[i][j]=self.a[j][i]=value;changed=True
        elif op=='linear':
            i,value=c['i'],c['value']&self.mask
            if self.b[i]!=value:self.b[i]=value;changed=True
        elif op=='constant':
            value=c['value']&self.mask
            if value!=self.c:self.c=value;changed=True
        elif op=='save':self.saved[c['slot']]=self.state()
        elif op=='load':
            state=self.saved[c['slot']]
            if state!=self.state():self.a=[list(r) for r in state[0]];self.b=list(state[1]);self.c=state[2];changed=True
        else:raise AssertionError(op)
        if changed:self.cache.clear()
        return {'ok':True}


def main():
    machine=None
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='init':machine=Machine(c);out={'ok':True}
        else:out=machine.execute(c)
        sys.stdout.buffer.write(json.dumps(out,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
