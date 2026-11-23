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
        let mut p:i64=0;
        let mut q:i64=0;
        let mut r:i64=0;
        let mut s:i64=0;
        let mut u:i64=0;
        if ((a != 0)) {
            if ((a == 1)) {
                if ((c > s0[(b) as usize])) {
                    if ((c > s1[(b) as usize])) {
                        s1[(b) as usize] = c;
                        s3[(b) as usize] = d;
                        p = 1;
                    }
                }
            }
            if ((a == 2)) {
                if ((c == s1[(b) as usize])) {
                    if ((c > s0[(b) as usize])) {
                        u = (((((c * 7) + ((s3[(b) as usize] + 100) * 11)) + b) + 21) % 257);
                        if ((d == u)) {
                            s0[(b) as usize] = c;
                            s1[(b) as usize] = 0;
                            s2[(b) as usize] = s3[(b) as usize];
                            s3[(b) as usize] = 0;
                            p = 1;
                        }
                    }
                }
            }
            if ((a == 3)) {
                s1[(b) as usize] = 0;
                s3[(b) as usize] = 0;
                p = 2;
            }
            if ((a == 4)) {
                p = 3;
            }
            q = s0[(b) as usize];
            r = s2[(b) as usize];
            s = s1[(b) as usize];
        }
        println!("{} {} {} {}", p, q, r, s);
    }
}
