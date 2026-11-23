package main
import ("bufio";"fmt";"os")
func main(){
    input:=bufio.NewReader(os.Stdin)
    output:=bufio.NewWriter(os.Stdout)
    defer output.Flush()
    var s0, s1, s2, s3 [32]int64
    for {
        var row [6]int64
        if n,_:=fmt.Fscan(input,&row[0],&row[1],&row[2],&row[3],&row[4],&row[5]); n!=6 { break }
        if row[0]==0 { s0=[32]int64{}; s1=[32]int64{}; s2=[32]int64{}; s3=[32]int64{};  }
        a, b, c, d, e, f := row[0], row[1], row[2], row[3], row[4], row[5]
        var p, q, r, s, u, v int64
        if (a != 0) {
            if (a == 2) {
                if (c > s0[b]) {
                    s0[b] = c
                    s1[b] = d
                    s2[b] = 0
                    s3[b] = 0
                    p = 1
                }
            }
            if (a == 3) {
                p = 2
            }
            if (a == 1) {
                if (c <= s0[b]) {
                    u = (((d + 64) - s1[b]) % 64)
                    if (u > 0) {
                        if (u < 32) {
                            v = (s2[b] + e)
                            if (v >= 0) {
                                if (v <= 78) {
                                    s1[b] = d
                                    s2[b] = v
                                    s3[b] = f
                                    p = 1
                                }
                            }
                        }
                    }
                }
            }
            q = s0[b]
            r = s1[b]
            s = s2[b]
        }
        fmt.Fprintln(output,p, q, r, s)
    }
}
