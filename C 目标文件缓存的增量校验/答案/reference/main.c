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
        I p=0, q=0, r=0, s=0;
        if ((a != 0)) {
            if ((a == 1)) {
                s0[b] = (((((((c * 15) + (d * 15)) + (e * 7)) + f) + 19) % 4093) + 1);
                s1[b] = (((((d * 5) + (f * 9)) + (e * 23)) % 1297) + 1);
            }
            if ((a == 2)) {
                if ((s0[b] != 0)) {
                    if ((c == s0[b])) {
                        if ((d == s1[b])) {
                            s2[b] = c;
                            s3[b] = d;
                            p = 1;
                        }
                    }
                }
            }
            if ((a == 3)) {
                if ((s2[b] != 0)) {
                    if ((c == s2[b])) {
                        if ((d == s3[b])) {
                            s2[b] = 0;
                            s3[b] = 0;
                            p = 1;
                        }
                    }
                }
            }
            q = s0[b];
            r = s1[b];
            if ((q != 0)) {
                if ((q == s2[b])) {
                    if ((r == s3[b])) {
                        s = 1;
                    }
                }
                if ((a == 1)) {
                    p = (3 - s);
                }
                if ((a == 4)) {
                    p = (3 - s);
                }
            }
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
