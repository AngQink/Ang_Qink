use strict;
use warnings;
my @s0=(0)x32;
my @s1=(0)x32;
my @s2=(0)x32;
my @s3=(0)x32;
while(<STDIN>) {
    my ($a,$b,$c,$d,$e,$f)=split;
    if($a==0) { @s0=(0)x32; @s1=(0)x32; @s2=(0)x32; @s3=(0)x32; }
    my ($p,$q,$r,$s)=(0)x4;
    if (($a != 0)) {
        $p = 0;
    }
    print "$p $q $r $s\n";
}
