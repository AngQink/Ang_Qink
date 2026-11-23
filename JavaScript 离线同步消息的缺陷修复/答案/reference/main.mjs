import {readFileSync} from 'node:fs';
const s0=Array(32).fill(0);
const s1=Array(32).fill(0);
const s2=Array(32).fill(0);
const s3=Array(32).fill(0);
const input=readFileSync(0,'utf8').trimEnd();
const output=[];
for (const line of input ? input.split('\n') : []) {
    const [a,b,c,d,e,f]=line.trim().split(' ').map(Number);
    if(a===0) { s0.fill(0); s1.fill(0); s2.fill(0); s3.fill(0); }
    let p=0;
    let q=0;
    let r=0;
    let s=0;
    let u=0;
    let v=0;
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
                if ((u == 1)) {
                    v = (s2[b] + e);
                    if ((v >= 0)) {
                        if ((v <= 81)) {
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
