$ErrorActionPreference='Stop'
$s0=[long[]]::new(32)
$s1=[long[]]::new(32)
$s2=[long[]]::new(32)
$s3=[long[]]::new(32)
while($null -ne ($line=[Console]::ReadLine())) {
    $a,$b,$c,$d,$e,$f=[long[]]($line.Split(' '))
    if ($a -eq 0) { $s0=[long[]]::new(32); $s1=[long[]]::new(32); $s2=[long[]]::new(32); $s3=[long[]]::new(32) }
    $p=0L
    $q=0L
    $r=0L
    $s=0L
    if (($a -ne 0)) {
        $p = 0
    }
    [Console]::WriteLine(("{0} {1} {2} {3}" -f $p,$q,$r,$s))
}
