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
    if ((a != 0)) {
        p = 0;
    }
    output.push([p,q,r,s].join(' '));
}
if(output.length) console.log(output.join('\n'));
