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
    let w: number=0;
    if ((a == 1)) {
        p = (-1);
        u = ((((((c * 10) + s0[b]) + (e * 14)) + (b * 20)) + 24) % 251);
        if ((u == d)) {
            w = (((((s0[b] * 20) + (e * 25)) + b) + 24) % 2048);
            v = ((((c + 2048) - w) * 241) % 2048);
            if ((v < 1024)) {
                r = (v % 32);
                v = Math.trunc(v / 32);
                s = (v % 4);
                v = Math.trunc(v / 4);
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
