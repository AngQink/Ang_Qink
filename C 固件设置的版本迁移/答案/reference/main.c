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
        I p=0, q=0, r=0, s=0, u=0;
        if ((a != 0)) {
            if ((a == 1)) {
                u = (c / 4);
                s0[b] = 1;
                s1[b] = (u + (e * 4));
            }
            if ((a == 2)) {
                s2[b] = c;
                s3[b] = 0;
                if ((c == 1)) {
                    s3[b] = d;
                }
            }
            if ((s2[b] == 1)) {
                p = 1;
                q = s3[b];
            }
            if ((s2[b] == 0)) {
                if ((s0[b] != 0)) {
                    p = 1;
                    q = s1[b];
                }
            }
            if ((s2[b] == 2)) {
                p = 2;
            }
            r = s1[b];
            s = s0[b];
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
