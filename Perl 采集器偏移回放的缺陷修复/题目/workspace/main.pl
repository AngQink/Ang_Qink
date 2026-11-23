use strict;
use warnings;
my @s0=(0)x32;
my @s1=(0)x32;
my @s2=(0)x32;
my @s3=(0)x32;
while(<STDIN>) {
    my ($a,$b,$c,$d,$e,$f)=split;
    if($a==0) { @s0=(0)x32; @s1=(0)x32; @s2=(0)x32; @s3=(0)x32; }
    my ($p,$q,$r,$s,$u,$v)=(0)x6;
    if (($a != 0)) {
        if (($a == 2)) {
            if (($c > $s0[$b])) {
                $s0[$b] = $c;
                $s1[$b] = $d;
                $s2[$b] = 0;
                $s3[$b] = 0;
                $p = 1;
            }
        }
        if (($a == 3)) {
            $p = 2;
        }
        if (($a == 1)) {
            if (($c <= $s0[$b])) {
                $u = ($d - $s1[$b]);
                if (($u == 1)) {
                    $v = ($s2[$b] + $e);
                    if (($v >= 0)) {
                        if (($v <= 99)) {
                            $s1[$b] = $d;
                            $s2[$b] = $v;
                            $s3[$b] = $f;
                            $p = 1;
                        }
                    }
                }
            }
        }
        $q = $s0[$b];
        $r = $s1[$b];
        $s = $s2[$b];
    }
    print "$p $q $r $s\n";
}
