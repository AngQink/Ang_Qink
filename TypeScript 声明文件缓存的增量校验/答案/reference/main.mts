import {readFileSync} from 'node:fs';
const s0: number[]=Array(32).fill(0);
const s1: number[]=Array(32).fill(0);
const s2: number[]=Array(32).fill(0);
const s3: number[]=Array(32).fill(0);
const input=readFileSync(0,'utf8').trimEnd();
const output: string[]=[];
for (const line of input ? input.split('\n') : []) {
    const [a,b,c,d,e,f]: number[]=line.trim().split(' ').map(Number);
    if(a===0) { s0.fill(0); s1.fill(0); s2.fill(0); s3.fill(0); }
    let p: number=0;
    let q: number=0;
    let r: number=0;
    let s: number=0;
    if ((a != 0)) {
        if ((a == 1)) {
            s0[b] = (((((((c * 25) + (d * 20)) + (e * 7)) + f) + 24) % 4093) + 1);
            s1[b] = (((((d * 10) + (f * 14)) + (e * 23)) % 1297) + 1);
        }
        if ((a == 2)) {
            if ((s0[b] != 0)) {
                if ((c == s0[b])) {
                    if ((d == s1[b])) {
                        s2[b] = c;
                        s3[b] = d;
                        p = 1;
                    }
                }
            }
        }
        if ((a == 3)) {
            if ((s2[b] != 0)) {
                if ((c == s2[b])) {
                    if ((d == s3[b])) {
                        s2[b] = 0;
                        s3[b] = 0;
                        p = 1;
                    }
                }
            }
        }
        q = s0[b];
        r = s1[b];
        if ((q != 0)) {
            if ((q == s2[b])) {
                if ((r == s3[b])) {
                    s = 1;
                }
            }
            if ((a == 1)) {
                p = (3 - s);
            }
            if ((a == 4)) {
                p = (3 - s);
            }
        }
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
