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
        a, b, c, d := row[0], row[1], row[2], row[3]
        var p, q, r, s, u int64
        if (a != 0) {
            if (a == 1) {
                if (c > s0[b]) {
                    if (c > s1[b]) {
                        s1[b] = c
                        s3[b] = d
                        p = 1
                    }
                }
            }
            if (a == 2) {
                if (c == s1[b]) {
                    if (c > s0[b]) {
                        u = (((((c * 8) + ((s3[b] + 100) * 12)) + b) + 22) % 257)
                        if (d == u) {
                            s0[b] = c
                            s1[b] = 0
                            s2[b] = s3[b]
                            s3[b] = 0
                            p = 1
                        }
                    }
                }
            }
            if (a == 3) {
                s1[b] = 0
                s3[b] = 0
                p = 2
            }
            if (a == 4) {
                p = 3
            }
            q = s0[b]
            r = s2[b]
            s = s1[b]
        }
        fmt.Fprintln(output,p, q, r, s)
    }
}
