use std::io::{self,BufRead};
fn main(){
    let mut s0=[0i64;32];
    let mut s1=[0i64;32];
    let mut s2=[0i64;32];
    let mut s3=[0i64;32];
    for line in io::stdin().lock().lines(){
        let line=line.unwrap();
        let row:Vec<i64>=line.split_whitespace().map(|x|x.parse().unwrap()).collect();
        if row[0]==0 { s0.fill(0); s1.fill(0); s2.fill(0); s3.fill(0); }
        let a=row[0];
        let b=row[1];
        let c=row[2];
        let d=row[3];
        let e=row[4];
        let mut p:i64=0;
        let mut q:i64=0;
        let mut r:i64=0;
        let mut s:i64=0;
        let mut u:i64=0;
        let mut v:i64=0;
        let mut w:i64=0;
        if ((a == 1)) {
            p = (-1);
            u = ((((((c * 7) + s0[(b) as usize]) + (e * 11)) + (b * 17)) + 21) % 251);
            if ((u == d)) {
                w = (((((s0[(b) as usize] * 17) + (e * 19)) + b) + 21) % 2048);
                v = ((((c + 2048) - w) * 931) % 2048);
                if ((v < 1024)) {
                    r = (v % 32);
                    v = (v / 32);
                    q = (v % 8);
                    v = (v / 8);
                    s = (v % 4);
                    v = (v / 4);
                    r = (r - 16);
                    s0[(b) as usize] = (((c + d) + s0[(b) as usize]) % 2048);
                    p = 1;
                }
            }
        }
        println!("{} {} {} {}", p, q, r, s);
    }
}
