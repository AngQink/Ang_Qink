#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=u=v=0 ))
    if (( (a != 0) )); then
        if (( (a == 2) )); then
            if (( (c > s0[b]) )); then
                (( s0[b] = c ))
                (( s1[b] = d ))
                (( s2[b] = 0 ))
                (( s3[b] = 0 ))
                (( p = 1 ))
            fi
        fi
        if (( (a == 3) )); then
            (( p = 2 ))
        fi
        if (( (a == 1) )); then
            if (( (c == s0[b]) )); then
                (( u = (((d + 64) - s1[b]) % 64) ))
                if (( (u > 0) )); then
                    if (( (u < 32) )); then
                        (( v = (s2[b] + e) ))
                        if (( (v >= 0) )); then
                            if (( (v <= 96) )); then
                                (( s1[b] = d ))
                                (( s2[b] = v ))
                                (( s3[b] = f ))
                                (( p = 1 ))
                            fi
                        fi
                    fi
                fi
            fi
        fi
        (( q = s0[b] ))
        (( r = s1[b] ))
        (( s = s2[b] ))
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
