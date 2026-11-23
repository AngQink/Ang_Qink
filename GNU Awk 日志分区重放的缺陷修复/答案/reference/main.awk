{
    a=$1+0; b=$2+0; c=$3+0; d=$4+0; e=$5+0; f=$6+0
    if(a==0) for(i=0;i<32;i++) s0[i]=s1[i]=s2[i]=s3[i]=0
    p=q=r=s=u=v=0
    if ((a != 0)) {
        if ((a == 2)) {
            if ((c > s0[b])) {
                s0[b] = c
                s1[b] = d
                s2[b] = 0
                s3[b] = 0
                p = 1
            }
        }
        if ((a == 3)) {
            p = 2
        }
        if ((a == 1)) {
            if ((c == s0[b])) {
                u = (d - s1[b])
                if ((u > 0)) {
                    v = (s2[b] + e)
                    if ((v >= 0)) {
                        if ((v <= 102)) {
                            s1[b] = d
                            s2[b] = v
                            s3[b] = f
                            p = 1
                        }
                    }
                }
            }
        }
        q = s0[b]
        r = s1[b]
        s = s2[b]
    }
    printf "%d %d %d %d\n", p, q, r, s
}
