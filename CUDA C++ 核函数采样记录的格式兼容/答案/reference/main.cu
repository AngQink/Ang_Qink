#include <cstdio>
#include <vector>
#include <cuda_runtime.h>
typedef long long I;
__global__ void process(const I *input,I *output,int rows) {
    I s0[32]={0};
    I s1[32]={0};
    I s2[32]={0};
    I s3[32]={0};
    for(int n=0;n<rows;n++) {
        const I *row=input+6*n;
        if (!row[0]) for(int i=0;i<32;i++) s0[i]=s1[i]=s2[i]=s3[i]=0;
        I a=row[0], b=row[1], c=row[2], d=row[3], e=row[4];
        I p=0, q=0, r=0, s=0, u=0, v=0, w=0;
        if ((a == 1)) {
            p = (-1);
            u = ((((((c * 21) + s0[b]) + (e * 9)) + (b * 31)) + 35) % 251);
            if ((u == d)) {
                w = (((((s0[b] * 31) + (e * 47)) + b) + 35) % 2048);
                v = ((((c + 2048) - w) * 931) % 2048);
                if ((v < 1024)) {
                    s = (v % 4);
                    v = (v / 4);
                    r = (v % 32);
                    v = (v / 32);
                    q = (v % 8);
                    v = (v / 8);
                    r = (r - 16);
                    s0[b] = (((c + d) + s0[b]) % 2048);
                    p = 1;
                }
            }
        }
        output[4*n]=p; output[4*n+1]=q; output[4*n+2]=r; output[4*n+3]=s;
    }
}
int main() {
    std::vector<I> input;
    I value;
    while (scanf("%lld",&value)==1) input.push_back(value);
    if (input.empty()) return 0;
    if (input.size()%6) return 2;
    std::vector<I> output(input.size()/6*4);
    I *in=nullptr,*out=nullptr;
    if (cudaMalloc(&in,input.size()*sizeof(I)) || cudaMalloc(&out,output.size()*sizeof(I))) return 3;
    if (cudaMemcpy(in,input.data(),input.size()*sizeof(I),cudaMemcpyHostToDevice)) return 3;
    process<<<1,1>>>(in,out,static_cast<int>(input.size()/6));
    if (cudaMemcpy(output.data(),out,output.size()*sizeof(I),cudaMemcpyDeviceToHost)) return 3;
    cudaFree(in); cudaFree(out);
    for (size_t i=0;i<output.size();i+=4) printf("%lld %lld %lld %lld\n",output[i],output[i+1],output[i+2],output[i+3]);
}
