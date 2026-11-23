{
    a=$1+0; b=$2+0; c=$3+0; d=$4+0; e=$5+0; f=$6+0
    if(a==0) for(i=0;i<32;i++) s0[i]=s1[i]=s2[i]=s3[i]=0
    p=q=r=s=u=0
    if ((a != 0)) {
        if ((a == 1)) {
            u = int(c / 5)
            if (((c % 5) != 0)) {
                u = (u + 1)
            }
            s0[b] = 1
            s1[b] = (u + (e * 15))
            if ((d == 0)) {
                s0[b] = 0
                s1[b] = 0
            }
        }
        if ((a == 2)) {
            s2[b] = c
            s3[b] = 0
            if ((c == 1)) {
                s3[b] = d
            }
        }
        if ((s2[b] == 1)) {
            p = 1
            q = s3[b]
        }
        if ((s2[b] == 0)) {
            if ((s0[b] != 0)) {
                p = 1
                q = s1[b]
            }
        }
        if ((s2[b] == 2)) {
            p = 2
        }
        r = s1[b]
        s = s0[b]
    }
    printf "%d %d %d %d\n", p, q, r, s
}
