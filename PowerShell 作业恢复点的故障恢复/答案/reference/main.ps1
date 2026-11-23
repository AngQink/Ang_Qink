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
            if (($c -gt $s0[$b])) {
                if (($c -gt $s1[$b])) {
                    $s1[$b] = $c
                    $s3[$b] = $d
                    $p = 1
                }
            }
        }
        if (($a -eq 2)) {
            if (($c -eq $s1[$b])) {
                if (($c -gt $s0[$b])) {
                    $u = ((((($c * 13) + (($s3[$b] + 100) * 9)) + $b) + 27) % 257)
                    if (($d -eq $u)) {
                        $s0[$b] = $c
                        $s1[$b] = 0
                        $s2[$b] = $s3[$b]
                        $s3[$b] = 0
                        $p = 1
                    }
                }
            }
        }
        if (($a -eq 3)) {
            $s1[$b] = 0
            $s3[$b] = 0
            $p = 2
        }
        if (($a -eq 4)) {
            $p = 3
        }
        $q = $s0[$b]
        $r = $s2[$b]
        $s = $s1[$b]
    }
    [Console]::WriteLine(("{0} {1} {2} {3}" -f $p,$q,$r,$s))
}
