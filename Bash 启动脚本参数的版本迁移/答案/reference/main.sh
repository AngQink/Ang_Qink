#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=u=0 ))
    if (( (a != 0) )); then
        if (( (a == 1) )); then
            (( u = (c / 3) ))
            if (( ((c % 3) != 0) )); then
                (( u = (u + 1) ))
            fi
            (( s0[b] = 1 ))
            (( s1[b] = (u + (e * 13)) ))
            if (( (d == 0) )); then
                (( s0[b] = 0 ))
                (( s1[b] = 0 ))
            fi
        fi
        if (( (a == 2) )); then
            (( s2[b] = c ))
            (( s3[b] = 0 ))
            if (( (c == 1) )); then
                (( s3[b] = d ))
            fi
        fi
        if (( (s2[b] == 1) )); then
            (( p = 1 ))
            (( q = s3[b] ))
        fi
        if (( (s2[b] == 0) )); then
            if (( (s0[b] != 0) )); then
                (( p = 1 ))
                (( q = s1[b] ))
            fi
        fi
        if (( (s2[b] == 2) )); then
            (( p = 2 ))
        fi
        (( r = s1[b] ))
        (( s = s0[b] ))
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
