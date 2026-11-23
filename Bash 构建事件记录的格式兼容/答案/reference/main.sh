#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=u=v=w=0 ))
    if (( (a == 1) )); then
        (( p = (-1) ))
        (( u = ((((((c * 14) + s0[b]) + (e * 10)) + (b * 24)) + 28) % 251) ))
        if (( (u == d) )); then
            (( w = (((((s0[b] * 24) + (e * 33)) + b) + 28) % 2048) ))
            (( v = ((((c + 2048) - w) * 1065) % 2048) ))
            if (( (v < 1024) )); then
                (( q = (v % 8) ))
                (( v = (v / 8) ))
                (( r = (v % 32) ))
                (( v = (v / 32) ))
                (( s = (v % 4) ))
                (( v = (v / 4) ))
                (( r = (r - 16) ))
                (( s0[b] = (((c + d) + s0[b]) % 2048) ))
                (( p = 1 ))
            fi
        fi
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
