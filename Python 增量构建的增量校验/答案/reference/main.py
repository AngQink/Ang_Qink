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
        p=q=r=s=0
        if (a != 0):
            if (a == 1):
                s0[b] = (((((((c * 11) + (d * 13)) + (e * 7)) + f) + 17) % 4093) + 1)
                s1[b] = (((((d * 3) + (f * 7)) + (e * 23)) % 1297) + 1)
            if (a == 2):
                if (s0[b] != 0):
                    if (c == s0[b]):
                        if (d == s1[b]):
                            s2[b] = c
                            s3[b] = d
                            p = 1
            if (a == 3):
                if (s2[b] != 0):
                    if (c == s2[b]):
                        if (d == s3[b]):
                            s2[b] = 0
                            s3[b] = 0
                            p = 1
            q = s0[b]
            r = s1[b]
            if (q != 0):
                if (q == s2[b]):
                    if (r == s3[b]):
                        s = 1
                if (a == 1):
                    p = (3 - s)
                if (a == 4):
                    p = (3 - s)
        print(p, q, r, s)

if __name__=='__main__':
    main()
