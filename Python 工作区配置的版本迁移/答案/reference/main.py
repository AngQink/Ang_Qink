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
        p=q=r=s=u=0
        if (a != 0):
            if (a == 1):
                u = (c // 2)
                s0[b] = 1
                s1[b] = (u + (e * 2))
            if (a == 2):
                s2[b] = c
                s3[b] = 0
                if (c == 1):
                    s3[b] = d
            if (s2[b] == 1):
                p = 1
                q = s3[b]
            if (s2[b] == 0):
                if (s0[b] != 0):
                    p = 1
                    q = s1[b]
            if (s2[b] == 2):
                p = 2
            r = s1[b]
            s = s0[b]
        print(p, q, r, s)

if __name__=='__main__':
    main()
