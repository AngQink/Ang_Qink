import sys

def main():
    s0=[0]*32
    s1=[0]*32
    s2=[0]*32
    s3=[0]*32
    for line in sys.stdin:
        a,b,c,d,e,f=map(int,line.split())
        if a==0:
            s0[:]=[0]*32
            s1[:]=[0]*32
            s2[:]=[0]*32
            s3[:]=[0]*32
        p=q=r=s=u=v=w=0
        if (a == 1):
            p = (-1)
            u = ((((((c * 3) + s0[b]) + (e * 7)) + (b * 13)) + 17) % 251)
            if (u == d):
                w = (((((s0[b] * 13) + (e * 11)) + b) + 17) % 2048)
                v = ((((c + 2048) - w) * 683) % 2048)
                if (v < 1024):
                    s = (v % 4)
                    v = (v // 4)
                    r = (v % 32)
                    v = (v // 32)
                    q = (v % 8)
                    v = (v // 8)
                    r = (r - 16)
                    s0[b] = (((c + d) + s0[b]) % 2048)
                    p = 1
        print(p, q, r, s)

if __name__=='__main__':
    main()
