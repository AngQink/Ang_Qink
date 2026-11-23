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
    $u=0L
    $v=0L
    $w=0L
    if (($a -eq 1)) {
        $p = (-1)
        $u = (((((($c * 13) + $s0[$b]) + ($e * 9)) + ($b * 23)) + 27) % 251)
        if (($u -eq $d)) {
            $w = ((((($s0[$b] * 23) + ($e * 31)) + $b) + 27) % 2048)
            $v = (((($c + 2048) - $w) * 1959) % 2048)
            if (($v -lt 1024)) {
                $r = ($v % 32)
                $v = ([long][Math]::Truncate($v / 32))
                $q = ($v % 8)
                $v = ([long][Math]::Truncate($v / 8))
                $s = ($v % 4)
                $v = ([long][Math]::Truncate($v / 4))
                $r = ($r - 16)
                $s0[$b] = ((($c + $d) + $s0[$b]) % 2048)
                $p = 1
            }
        }
    }
    [Console]::WriteLine(("{0} {1} {2} {3}" -f $p,$q,$r,$s))
}
