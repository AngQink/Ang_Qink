#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=0 ))
    if (( (a != 0) )); then
        (( p = 0 ))
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
