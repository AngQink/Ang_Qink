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
        a, b, c, d, e := row[0], row[1], row[2], row[3], row[4]
        var p, q, r, s, u int64
        if (a != 0) {
            if (a == 1) {
                u = (c / 2)
                if ((c % 2) != 0) {
                    u = (u + 1)
                }
                s0[b] = 1
                s1[b] = (u + (e * 7))
                if (d == 0) {
                    s0[b] = 0
                    s1[b] = 0
                }
            }
            if (a == 2) {
                s2[b] = c
                s3[b] = 0
                if (c == 1) {
                    s3[b] = d
                }
            }
            if (s2[b] == 1) {
                p = 1
                q = s3[b]
            }
            if (s2[b] == 0) {
                if (s0[b] != 0) {
                    p = 1
                    q = s1[b]
                }
            }
            if (s2[b] == 2) {
                p = 2
            }
            r = s1[b]
            s = s0[b]
        }
        fmt.Fprintln(output,p, q, r, s)
    }
}
