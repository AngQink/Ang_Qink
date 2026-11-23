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
                        u = (((((c * 21) + ((s3[b] + 100) * 9)) + b) + 35) % 257);
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
