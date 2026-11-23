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
    if (($a -ne 0)) {
        if (($a -eq 1)) {
            $u = ([long][Math]::Truncate($c / 2))
            $s0[$b] = 1
            $s1[$b] = ($u + ($e * 12))
        }
        if (($a -eq 2)) {
            $s2[$b] = $c
            $s3[$b] = 0
            if (($c -eq 1)) {
                $s3[$b] = $d
            }
        }
        if (($s2[$b] -eq 1)) {
            $p = 1
            $q = $s3[$b]
        }
        if (($s2[$b] -eq 0)) {
            if (($s0[$b] -ne 0)) {
                $p = 1
                $q = $s1[$b]
            }
        }
        if (($s2[$b] -eq 2)) {
            $p = 2
        }
        $r = $s1[$b]
        $s = $s0[$b]
    }
    [Console]::WriteLine(("{0} {1} {2} {3}" -f $p,$q,$r,$s))
}
