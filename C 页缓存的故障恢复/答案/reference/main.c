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
        I a=row[0], b=row[1], c=row[2], d=row[3];
        I p=0, q=0, r=0, s=0, u=0;
        if ((a != 0)) {
            if ((a == 1)) {
                if ((c > s0[b])) {
                    if ((c > s1[b])) {
                        s1[b] = c;
                        s3[b] = d;
                        p = 1;
                    }
                }
            }
            if ((a == 2)) {
                if ((c == s1[b])) {
                    if ((c > s0[b])) {
                        u = (((((c * 5) + ((s3[b] + 100) * 9)) + b) + 19) % 257);
                        if ((d == u)) {
                            s0[b] = c;
                            s1[b] = 0;
                            s2[b] = s3[b];
                            s3[b] = 0;
                            p = 1;
                        }
                    }
                }
            }
            if ((a == 3)) {
                s1[b] = 0;
                s3[b] = 0;
                p = 2;
            }
            if ((a == 4)) {
                p = 3;
            }
            q = s0[b];
            r = s2[b];
            s = s1[b];
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
