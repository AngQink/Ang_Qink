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
            u = Math.trunc(c / 3);
            s0[b] = 1;
            s1[b] = (u + (e * 8));
        }
        if ((a == 2)) {
            s2[b] = c;
            s3[b] = 0;
            if ((c == 1)) {
                s3[b] = d;
            }
        }
        if ((s2[b] == 1)) {
            p = 1;
            q = s3[b];
        }
        if ((s2[b] == 0)) {
            if ((s0[b] != 0)) {
                p = 1;
                q = s1[b];
            }
        }
        if ((s2[b] == 2)) {
            p = 2;
        }
        r = s1[b];
        s = s0[b];
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
