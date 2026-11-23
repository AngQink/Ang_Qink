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
        if row[0]==0 { s0=[32]int64{}; s1=[32]int64{}; s2=[32]int64{}; s3=[32]int64{}; _ = s0; _ = s1; _ = s2; _ = s3; }
        a := row[0]
        var p, q, r, s int64
        if (a != 0) {
            p = 0
        }
        fmt.Fprintln(output,p, q, r, s)
    }
}
