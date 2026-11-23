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
    if (($a -ne 0)) {
        if (($a -eq 2)) {
            if (($c -gt $s0[$b])) {
                $s0[$b] = $c
                $s1[$b] = $d
                $s2[$b] = 0
                $s3[$b] = 0
                $p = 1
            }
        }
        if (($a -eq 3)) {
            $p = 2
        }
        if (($a -eq 1)) {
            if (($c -le $s0[$b])) {
                $u = ($d - $s1[$b])
                if (($u -gt 0)) {
                    $v = ($s2[$b] + $e)
                    if (($v -ge 0)) {
                        if (($v -le 93)) {
                            $s1[$b] = $d
                            $s2[$b] = $v
                            $s3[$b] = $f
                            $p = 1
                        }
                    }
                }
            }
        }
        $q = $s0[$b]
        $r = $s1[$b]
        $s = $s2[$b]
    }
    [Console]::WriteLine(("{0} {1} {2} {3}" -f $p,$q,$r,$s))
}
