use std::io::{self,BufRead};
fn main() {
    for line in io::stdin().lock().lines() {
        let line=line.unwrap();
        let mut n=line.split_whitespace().map(|x|x.parse::<i64>().unwrap());
        let stamp=n.next().unwrap();
        let delta=n.next().unwrap();
        let (d,token)=policy::apply(stamp,delta);
        println!("{stamp} {d} {} {token}",wire::ABI);
    }
}
