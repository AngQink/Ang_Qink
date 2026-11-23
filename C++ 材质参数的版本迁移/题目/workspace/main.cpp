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
        I a=row[0];
        I p=0, q=0, r=0, s=0;
        if ((a != 0)) {
            p = 0;
        }
        printf("%lld %lld %lld %lld\n", p, q, r, s);
    }
    return 0;
}
