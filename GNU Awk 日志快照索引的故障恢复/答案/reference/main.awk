{
    a=$1+0; b=$2+0; c=$3+0; d=$4+0; e=$5+0; f=$6+0
    if(a==0) for(i=0;i<32;i++) s0[i]=s1[i]=s2[i]=s3[i]=0
    p=q=r=s=u=0
    if ((a != 0)) {
        if ((a == 1)) {
            if ((c > s0[b])) {
                if ((c > s1[b])) {
                    s1[b] = c
                    s3[b] = d
                    p = 1
                }
            }
        }
        if ((a == 2)) {
            if ((c == s1[b])) {
                if ((c > s0[b])) {
                    u = (((((c * 16) + ((s3[b] + 100) * 12)) + b) + 30) % 257)
                    if ((d == u)) {
                        s0[b] = c
                        s1[b] = 0
                        s2[b] = s3[b]
                        s3[b] = 0
                        p = 1
                    }
                }
            }
        }
        if ((a == 3)) {
            s1[b] = 0
            s3[b] = 0
            p = 2
        }
        if ((a == 4)) {
            p = 3
        }
        q = s0[b]
        r = s2[b]
        s = s1[b]
    }
    printf "%d %d %d %d\n", p, q, r, s
}
