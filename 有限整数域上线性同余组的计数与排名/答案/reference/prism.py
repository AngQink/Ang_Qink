"""PRISM reference: incremental p-primary presentations of suffix images."""
import json
import math
import sys


def diagonalize(matrix, row_transform, prime, exponent, mod):
    """Diagonalize over Z/mod, retaining the change of row coordinates."""
    n = len(matrix)
    width = len(matrix[0])
    levels = [mod]*n
    powers = [prime**e for e in range(exponent+1)]
    for k in range(n):
        best = exponent
        choice = None
        for i in range(k,n):
            row = matrix[i]
            for j in range(k,width):
                a = row[j]
                if a and a%powers[best]==0:
                    continue
                if a:
                    e = 0
                    while a%powers[e+1]==0:
                        e += 1
                    if e<best:
                        best,choice = e,(i,j)
                        if best==0:
                            break
            if best==0:
                break
        if choice is None:
            break
        i,j = choice
        if i!=k:
            matrix[i],matrix[k] = matrix[k],matrix[i]
            row_transform[i],row_transform[k] = row_transform[k],row_transform[i]
        if j!=k:
            for row in matrix:
                row[j],row[k] = row[k],row[j]
        pivot = powers[best]
        levels[k] = pivot
        row = matrix[k]
        multiplier = pow(row[k]//pivot,-1,mod)
        for j in range(k,width):
            row[j] = row[j]*multiplier%mod
        transform = row_transform[k] = [x*multiplier%mod for x in row_transform[k]]
        # Other rows can be cleared because the pivot divides the trailing
        # submatrix. Clearing the pivot row by column operations then does
        # not change the trailing submatrix at all.
        for i in range(k+1,n):
            other = matrix[i]
            ratio = other[k]//pivot
            if ratio:
                for j in range(k+1,width):
                    other[j] = (other[j]-ratio*row[j])%mod
                row_transform[i] = [(x-ratio*y)%mod for x,y in zip(row_transform[i],transform)]
            other[k] = 0
        for j in range(k+1,width):
            row[j] = 0
    return levels


class PrimaryImage:
    def __init__(self, p, exponent, moduli, columns):
        q = p**exponent
        # Rows with no p-component impose no conditions in this image.
        local = []
        for i,m in enumerate(moduli):
            divisor = 1
            while m%p == 0:
                m //= p
                divisor *= p
            if divisor>1:
                local.append((i,q//divisor))
        self.constraints = []
        self.projections = [None]*len(columns)
        if not local:
            return
        n = len(local)
        transform = [[int(i==j) for j in range(n)] for i in range(n)]
        levels = [q]*n

        def coefficients(row, modulus):
            return tuple((i,(x*lift)%modulus) for x,(i,lift) in zip(row,local) if (x*lift)%modulus)

        for index in range(len(columns)-1,-1,-1):
            column = [columns[index][i]*lift%q for i,lift in local]
            vector = [sum(v*x for v,x in zip(row,column))%q for row in transform]
            multipliers = [d//math.gcd(v,d) for v,d in zip(vector,levels)]
            dominant = max(range(n),key=multipliers.__getitem__)
            step = multipliers[dominant]
            if step>1:
                d = levels[dominant]
                factor = d//step
                unit = vector[dominant]//factor
                self.projections[index] = step,d,factor,pow(unit,-1,step),coefficients(transform[dominant],d)

                presentation = [[(levels[i]%q if i==j else 0) for j in range(n)]+[vector[i]]
                                for i in range(n)]
                levels = diagonalize(presentation,transform,p,exponent,q)
            # If step is one, the new generator is already in the image.
        self.constraints = [(d,coefficients(row,d)) for d,row in zip(levels,transform) if d>1]


def dot(terms, vector):
    return sum(x*vector[i] for i,x in terms)


class Fiber:
    def __init__(self, factors, domains, moduli, columns):
        self.domains = domains
        self.columns = columns
        self.n = len(domains)
        images = [PrimaryImage(p,e,moduli,columns) for p,e in factors]
        self.constraints = [item for image in images for item in image.constraints]
        self.steps = []
        self.parts = []
        for index,domain in enumerate(domains):
            parts = [image.projections[index] for image in images if image.projections[index] is not None]
            step = math.prod(part[0] for part in parts)
            assert domain%step==0
            crt = []
            for power,d,factor,inv,terms in parts:
                complement = step//power
                crt.append((d,factor,inv*complement*pow(complement,-1,power),terms))
            self.steps.append(step)
            self.parts.append(crt)
        self.suffix_count = [1]*(self.n+1)
        for i in range(self.n-1,-1,-1):
            self.suffix_count[i] = self.suffix_count[i+1]*(domains[i]//self.steps[i])

    def residue(self, index, rhs):
        total = 0
        for mod,factor,mul,terms in self.parts[index]:
            value = dot(terms,rhs)%mod
            assert value%factor==0
            total += value//factor*mul
        return total%self.steps[index]

    def subtract(self, index, rhs, value):
        return [a-value*b for a,b in zip(rhs,self.columns[index])] if value else rhs

    def restrict(self, prefix, rhs):
        if any(dot(row,rhs)%mod for mod,row in self.constraints):
            return None
        for i,x in enumerate(prefix):
            residue = self.residue(i,rhs)
            if x%self.steps[i]!=residue:
                return None
            rhs = self.subtract(i,rhs,x)
        return rhs

    def nth(self, prefix, rhs, index):
        start = len(prefix)
        if index>=self.suffix_count[start]:
            return None
        answer = prefix[:]
        for i in range(start,self.n):
            bucket,index = divmod(index,self.suffix_count[i+1])
            value = self.residue(i,rhs)+self.steps[i]*bucket
            answer.append(value)
            rhs = self.subtract(i,rhs,value)
        return answer

    def probe(self, prefix, rhs, candidate):
        start = len(prefix)
        opening = candidate[:start]
        if opening<prefix:
            return {'before':0,'member':False}
        if opening>prefix:
            return {'before':self.suffix_count[start],'member':False}
        before = 0
        for i in range(start,self.n):
            step = self.steps[i]
            first = self.residue(i,rhs)
            x = candidate[i]
            before += ((x-first+step-1)//step)*self.suffix_count[i+1]
            if x%step!=first:
                return {'before':before,'member':False}
            rhs = self.subtract(i,rhs,x)
        return {'before':before,'member':True}


class Ledger:
    def __init__(self, init):
        self.factors = init['mod_factors']
        self.domains = init['domains']
        self.moduli = [row['mod'] for row in init['rows']]
        self.lookup = {row['id']:i for i,row in enumerate(init['rows'])}
        self.rows = tuple((tuple(x%m for x in row['a']),row['rhs']%m,row['enabled'])
                          for row,m in zip(init['rows'],self.moduli))
        self.slots = {}
        self.signature = None

    def query(self, command):
        selected = [i for i,(_,_,on) in enumerate(self.rows) if on and self.moduli[i]>1]
        signature = tuple((i,self.rows[i][0]) for i in selected)
        if self.signature!=signature:
            moduli = [self.moduli[i] for i in selected]
            columns = [[self.rows[i][0][j] for i in selected] for j in range(len(self.domains))]
            self.fiber = Fiber(self.factors,self.domains,moduli,columns)
            self.signature = signature
        fiber = self.fiber
        prefix = command['prefix']
        rhs = fiber.restrict(prefix,[self.rows[i][1] for i in selected])
        if rhs is None:
            return {'count':0,'at':[None]*len(command['at']),
                    'probes':[{'before':0,'member':False} for _ in command['probes']]}
        return {'count':fiber.suffix_count[len(prefix)],'at':[fiber.nth(prefix,rhs,k) for k in command['at']],
                'probes':[fiber.probe(prefix,rhs,x) for x in command['probes']]}

    def execute(self, command):
        op = command['op']
        if op=='query':
            return self.query(command)
        if op=='save':
            self.slots[command['slot']] = self.rows
        elif op=='load':
            self.rows = self.slots[command['slot']]
        else:
            i = self.lookup[command['id']]
            m = self.moduli[i]
            a,rhs,on = self.rows[i]
            if op=='row':
                a = tuple(x%m for x in command['a'])
                rhs = command['rhs']%m
            elif op=='rhs':
                rhs = command['rhs']%m
            elif op=='enable':
                on = command['value']
            else:
                raise AssertionError(op)
            self.rows = self.rows[:i]+((a,rhs,on),)+self.rows[i+1:]
        return {'ok':True}


def main():
    state = None
    output = sys.stdout.buffer
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        command = json.loads(line)
        if command['op']=='init':
            state = Ledger(command)
            result = {'ok':True}
        else:
            result = state.execute(command)
        output.write(json.dumps(result,separators=(',',':')).encode()+b'\n')
        output.flush()


if __name__ == '__main__':
    main()
