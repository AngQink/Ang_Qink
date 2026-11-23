#include <stdio.h>
typedef long long I;
int main(void) {
    I s0[32]={0};
    I s1[32]={0};
    I s2[32]={0};
    I s3[32]={0};
    I row[6];
    while(scanf("%lld %lld %lld %lld %lld %lld",row,row+1,row+2,row+3,row+4,row+5)==6) {
        if (!row[0]) for(int i=0;i<32;i++) s0[i]=s1[i]=s2[i]=s3[i]=0;
        I a=row[0], b=row[1], c=row[2], d=row[3], e=row[4], f=row[5];
        I p=0, q=0, r=0, s=0, u=0, v=0;
        if ((a != 0)) {
            if ((a == 2)) {
                if ((c > s0[b])) {
                    s0[b] = c;
                    s1[b] = d;
                    s2[b] = 0;
                    s3[b] = 0;
                    p = 1;
                }
            }
            if ((a == 3)) {
                p = 2;
            }
            if ((a == 1)) {
                if ((c == s0[b])) {
                    u = (d - s1[b]);
                    if ((u == 1)) {
                        v = (s2[b] + e);
                        if ((v >= 0)) {
                            if ((v <= 72)) {
                                s1[b] = d;
                                s2[b] = v;
                                s3[b] = f;
                                p = 1;
                            }
                        }
                    }
                }
            }
            q = s0[b];
            r = s1[b];
            s = s2[b];
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
