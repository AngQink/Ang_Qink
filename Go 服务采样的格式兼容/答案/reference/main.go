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
        if row[0]==0 { s0=[32]int64{}; s1=[32]int64{}; s2=[32]int64{}; s3=[32]int64{}; _ = s1; _ = s2; _ = s3; }
        a, b, c, d, e := row[0], row[1], row[2], row[3], row[4]
        var p, q, r, s, u, v, w int64
        if (a == 1) {
            p = (-1)
            u = ((((((c * 8) + s0[b]) + (e * 12)) + (b * 18)) + 22) % 251)
            if (u == d) {
                w = (((((s0[b] * 18) + (e * 21)) + b) + 22) % 2048)
                v = ((((c + 2048) - w) * 1733) % 2048)
                if (v < 1024) {
                    q = (v % 8)
                    v = (v / 8)
                    r = (v % 32)
                    v = (v / 32)
                    s = (v % 4)
                    v = (v / 4)
                    r = (r - 16)
                    s0[b] = (((c + d) + s0[b]) % 2048)
                    p = 1
                }
            }
        }
        fmt.Fprintln(output,p, q, r, s)
    }
}
