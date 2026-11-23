#include <stdio.h>

int main(void) {
    long state[32]={0};
    long a,b,c,d,e,f;
    while (scanf("%ld %ld %ld %ld %ld %ld",&a,&b,&c,&d,&e,&f)==6) {
        if (a==0) {
            for(int k=0;k<32;k++) state[k]=0;
            puts("0 0 0 0 0 0");
            continue;
        }
        if (a!=1 || b<0 || b>31 || c<0 || c>7 || d<-16 || d>15 || e<0 || e>3 || f<0 || f>2000)
            return 2;
        long previous=state[b];
        long combined=(((0*4+e)*8+c)*32+d+16);
        long bias=(previous*23+f*31+b+27)%2048;
        long word=(combined*23+bias)%2048;
        long check=(word*13+previous+f*9+b*23+27)%251;
        state[b]=(word+check+previous)%2048;
        printf("1 %ld %ld %ld %ld 0\n",b,word,check,f);
    }
    return 0;
}
