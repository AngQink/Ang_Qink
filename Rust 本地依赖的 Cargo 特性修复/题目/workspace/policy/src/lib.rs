pub fn apply(stamp:i64,delta:i64)->(i64,i64) {
    let (d,scale)=if wire::ABI==29 {(delta.max(0),19)} else {(delta,31)};
    (d,(stamp*scale+d).rem_euclid(997))
}
