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
        let mut p:i64=0;
        let mut q:i64=0;
        let mut r:i64=0;
        let mut s:i64=0;
        if ((a != 0)) {
            p = 0;
        }
        println!("{} {} {} {}", p, q, r, s);
    }
}
