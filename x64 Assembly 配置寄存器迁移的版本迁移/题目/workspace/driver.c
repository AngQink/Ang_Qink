#include <stdio.h>
void step(const long long *input,long long *output,long long *state);
int main(void) {
    long long row[6], result[4], state[128]={0};
    while (scanf("%lld %lld %lld %lld %lld %lld",row,row+1,row+2,row+3,row+4,row+5)==6) {
        if (!row[0]) for(int i=0;i<128;i++) state[i]=0;
        step(row,result,state);
        printf("%lld %lld %lld %lld\n",result[0],result[1],result[2],result[3]);
    }
    return 0;
}
