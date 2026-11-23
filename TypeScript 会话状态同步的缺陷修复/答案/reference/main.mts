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
    let u: number=0;
    let v: number=0;
    if ((a != 0)) {
        if ((a == 2)) {
            if ((c > s0[b])) {
                s0[b] = c;
                s1[b] = d;
                s2[b] = 0;
                s3[b] = 0;
                p = 1;
            }
        }
        if ((a == 3)) {
            p = 2;
        }
        if ((a == 1)) {
            if ((c == s0[b])) {
                u = (d - s1[b]);
                if ((u > 0)) {
                    v = (s2[b] + e);
                    if ((v >= 0)) {
                        if ((v <= 84)) {
                            s1[b] = d;
                            s2[b] = v;
                            s3[b] = f;
                            p = 1;
                        }
                    }
                }
            }
        }
        q = s0[b];
        r = s1[b];
        s = s2[b];
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
