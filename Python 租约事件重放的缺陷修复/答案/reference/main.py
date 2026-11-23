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
        p=q=r=s=u=v=0
        if (a != 0):
            if (a == 2):
                if (c > s0[b]):
                    s0[b] = c
                    s1[b] = d
                    s2[b] = 0
                    s3[b] = 0
                    p = 1
            if (a == 3):
                p = 2
            if (a == 1):
                if (c == s0[b]):
                    u = (d - s1[b])
                    if (u == 1):
                        v = (s2[b] + e)
                        if (v >= 0):
                            if (v <= 63):
                                s1[b] = d
                                s2[b] = v
                                s3[b] = f
                                p = 1
            q = s0[b]
            r = s1[b]
            s = s2[b]
        print(p, q, r, s)

if __name__=='__main__':
    main()
