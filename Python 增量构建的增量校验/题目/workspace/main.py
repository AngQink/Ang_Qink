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
            p = 0
        print(p, q, r, s)

if __name__=='__main__':
    main()
