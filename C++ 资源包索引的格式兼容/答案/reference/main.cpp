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
        I a=row[0], b=row[1], c=row[2], d=row[3], e=row[4];
        I p=0, q=0, r=0, s=0, u=0, v=0, w=0;
        if ((a == 1)) {
            p = (-1);
            u = ((((((c * 6) + s0[b]) + (e * 10)) + (b * 16)) + 20) % 251);
            if ((u == d)) {
                w = (((((s0[b] * 16) + (e * 17)) + b) + 20) % 2048);
                v = ((((c + 2048) - w) * 1593) % 2048);
                if ((v < 1024)) {
                    q = (v % 8);
                    v = (v / 8);
                    s = (v % 4);
                    v = (v / 4);
                    r = (v % 32);
                    v = (v / 32);
                    r = (r - 16);
                    s0[b] = (((c + d) + s0[b]) % 2048);
                    p = 1;
                }
            }
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
