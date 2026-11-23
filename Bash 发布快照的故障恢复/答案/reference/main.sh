#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=u=0 ))
    if (( (a != 0) )); then
        if (( (a == 1) )); then
            if (( (c > s0[b]) )); then
                if (( (c > s1[b]) )); then
                    (( s1[b] = c ))
                    (( s3[b] = d ))
                    (( p = 1 ))
                fi
            fi
        fi
        if (( (a == 2) )); then
            if (( (c == s1[b]) )); then
                if (( (c > s0[b]) )); then
                    (( u = (((((c * 14) + ((s3[b] + 100) * 10)) + b) + 28) % 257) ))
                    if (( (d == u) )); then
                        (( s0[b] = c ))
                        (( s1[b] = 0 ))
                        (( s2[b] = s3[b] ))
                        (( s3[b] = 0 ))
                        (( p = 1 ))
                    fi
                fi
            fi
        fi
        if (( (a == 3) )); then
            (( s1[b] = 0 ))
            (( s3[b] = 0 ))
            (( p = 2 ))
        fi
        if (( (a == 4) )); then
            (( p = 3 ))
        fi
        (( q = s0[b] ))
        (( r = s2[b] ))
        (( s = s1[b] ))
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
