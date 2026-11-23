package main
import (
    "bufio"
    "fmt"
    "hash/crc32"
    "os"
    "path/filepath"
    "strconv"
    "strings"
)

func checked(err error) {
    if err!=nil { panic(err) }
}
func files(path string) []byte {
    raw,err:=os.ReadFile(path);checked(err);return raw
}
func assemble(dir string) {
    n,err:=strconv.Atoi(strings.TrimSpace(string(files(filepath.Join(dir,"count.txt")))));checked(err)
    chunks:=make([][]byte,n)
    present:=make([]bool,n)
    scan:=bufio.NewScanner(strings.NewReader(string(files(filepath.Join(dir,"fragments.tsv")))))
    for scan.Scan() {
        fields:=strings.Split(scan.Text(),"\t")
        i,err:=strconv.Atoi(fields[0]);checked(err)
        data:=files(filepath.Join(dir,fields[1]))
        _ = crc32.ChecksumIEEE(data)
        chunks[i]=data
        present[i]=true
    }
    checked(scan.Err())
    var output []byte
    for i,ok:=range present {
        if !ok {
            checked(os.WriteFile(filepath.Join(dir,"status.txt"),[]byte(fmt.Sprintf("missing %d\n",i)),0644))
            return
        }
        output=append(output,chunks[i]...)
    }
    checked(os.WriteFile(filepath.Join(dir,"bundle.bin"),output,0644))
    checked(os.WriteFile(filepath.Join(dir,"status.txt"),[]byte("complete\n"),0644))
}
func main() {
    f,err:=os.Open(os.Args[1]);checked(err);defer f.Close()
    scan:=bufio.NewScanner(f)
    for scan.Scan() {assemble(filepath.Join(filepath.Dir(os.Args[1]),scan.Text()))}
    checked(scan.Err())
}
