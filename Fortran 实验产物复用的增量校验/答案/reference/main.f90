program main
    implicit none
    integer :: status
    integer(kind=8) :: a, b, c, d, e, f, p, q, r, s
    integer(kind=8) :: s0(0:31), s1(0:31), s2(0:31), s3(0:31)
    s0=0
    s1=0
    s2=0
    s3=0
    do
        read(*,*,iostat=status) a,b,c,d,e,f
        if(status/=0) exit
        if(a==0) then
            s0=0
            s1=0
            s2=0
            s3=0
        end if
        p=0
        q=0
        r=0
        s=0
        if ((a /= 0_8)) then
            if ((a == 1_8)) then
                s0(b) = (mod((((((c * 39_8) + (d * 27_8)) + (e * 7_8)) + f) + 31_8), 4093_8) + 1_8)
                s1(b) = (mod((((d * 17_8) + (f * 13_8)) + (e * 23_8)), 1297_8) + 1_8)
            end if
            if ((a == 2_8)) then
                if ((s0(b) /= 0_8)) then
                    if ((c == s0(b))) then
                        if ((d == s1(b))) then
                            s2(b) = c
                            s3(b) = d
                            p = 1_8
                        end if
                    end if
                end if
            end if
            if ((a == 3_8)) then
                if ((s2(b) /= 0_8)) then
                    if ((c == s2(b))) then
                        if ((d == s3(b))) then
                            s2(b) = 0_8
                            s3(b) = 0_8
                            p = 1_8
                        end if
                    end if
                end if
            end if
            q = s0(b)
            r = s1(b)
            if ((q /= 0_8)) then
                if ((q == s2(b))) then
                    if ((r == s3(b))) then
                        s = 1_8
                    end if
                end if
                if ((a == 1_8)) then
                    p = (3_8 - s)
                end if
                if ((a == 4_8)) then
                    p = (3_8 - s)
                end if
            end if
        end if
        write(*,'(i0,1x,i0,1x,i0,1x,i0)') p, q, r, s
    end do
end program main
