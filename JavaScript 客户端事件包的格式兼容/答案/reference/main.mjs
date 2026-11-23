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
    let w=0;
    if ((a == 1)) {
        p = (-1);
        u = ((((((c * 9) + s0[b]) + (e * 13)) + (b * 19)) + 23) % 251);
        if ((u == d)) {
            w = (((((s0[b] * 19) + (e * 23)) + b) + 23) % 2048);
            v = ((((c + 2048) - w) * 1775) % 2048);
            if ((v < 1024)) {
                s = (v % 4);
                v = Math.trunc(v / 4);
                r = (v % 32);
                v = Math.trunc(v / 32);
                q = (v % 8);
                v = Math.trunc(v / 8);
                r = (r - 16);
                s0[b] = (((c + d) + s0[b]) % 2048);
                p = 1;
            }
        }
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
