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
        if ((a != 0)) {
            if ((a == 1)) {
                u = (c / 6);
                s0[(b) as usize] = 1;
                s1[(b) as usize] = (u + (e * 6));
            }
            if ((a == 2)) {
                s2[(b) as usize] = c;
                s3[(b) as usize] = 0;
                if ((c == 1)) {
                    s3[(b) as usize] = d;
                }
            }
            if ((s2[(b) as usize] == 1)) {
                p = 1;
                q = s3[(b) as usize];
            }
            if ((s2[(b) as usize] == 0)) {
                if ((s0[(b) as usize] != 0)) {
                    p = 1;
                    q = s1[(b) as usize];
                }
            }
            if ((s2[(b) as usize] == 2)) {
                p = 2;
            }
            r = s1[(b) as usize];
            s = s0[(b) as usize];
        }
        println!("{} {} {} {}", p, q, r, s);
    }
}
