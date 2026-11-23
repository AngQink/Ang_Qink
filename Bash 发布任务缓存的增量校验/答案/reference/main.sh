#!/usr/bin/env bash
declare -a s0 s1 s2 s3
while read -r a b c d e f; do
    if ((a==0)); then for ((i=0;i<32;i++)); do ((s0[i]=s1[i]=s2[i]=s3[i]=0)); done; fi
    (( p=q=r=s=0 ))
    if (( (a != 0) )); then
        if (( (a == 1) )); then
            (( s0[b] = (((((((c * 33) + (d * 24)) + (e * 7)) + f) + 28) % 4093) + 1) ))
            (( s1[b] = (((((d * 14) + (f * 10)) + (e * 23)) % 1297) + 1) ))
        fi
        if (( (a == 2) )); then
            if (( (s0[b] != 0) )); then
                if (( (c == s0[b]) )); then
                    if (( (d == s1[b]) )); then
                        (( s2[b] = c ))
                        (( s3[b] = d ))
                        (( p = 1 ))
                    fi
                fi
            fi
        fi
        if (( (a == 3) )); then
            if (( (s2[b] != 0) )); then
                if (( (c == s2[b]) )); then
                    if (( (d == s3[b]) )); then
                        (( s2[b] = 0 ))
                        (( s3[b] = 0 ))
                        (( p = 1 ))
                    fi
                fi
            fi
        fi
        (( q = s0[b] ))
        (( r = s1[b] ))
        if (( (q != 0) )); then
            if (( (q == s2[b]) )); then
                if (( (r == s3[b]) )); then
                    (( s = 1 ))
                fi
            fi
            if (( (a == 1) )); then
                (( p = (3 - s) ))
            fi
            if (( (a == 4) )); then
                (( p = (3 - s) ))
            fi
        fi
    fi
    printf '%d %d %d %d\n' "$p" "$q" "$r" "$s"
done
