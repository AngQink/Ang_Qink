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
    if ((a != 0)) {
        if ((a == 1)) {
            if ((c > s0[b])) {
                if ((c > s1[b])) {
                    s1[b] = c;
                    s3[b] = d;
                    p = 1;
                }
            }
        }
        if ((a == 2)) {
            if ((c == s1[b])) {
                if ((c > s0[b])) {
                    u = (((((c * 9) + ((s3[b] + 100) * 13)) + b) + 23) % 257);
                    if ((d == u)) {
                        s0[b] = c;
                        s1[b] = 0;
                        s2[b] = s3[b];
                        s3[b] = 0;
                        p = 1;
                    }
                }
            }
        }
        if ((a == 3)) {
            s1[b] = 0;
            s3[b] = 0;
            p = 2;
        }
        if ((a == 4)) {
            p = 3;
        }
        q = s0[b];
        r = s2[b];
        s = s1[b];
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
