program main
    implicit none
    integer :: status
    integer(kind=8) :: a, b, c, d, e, f, p, q, r, s, u, v
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
        u=0
        v=0
        if ((a /= 0_8)) then
            if ((a == 2_8)) then
                if ((c > s0(b))) then
                    s0(b) = c
                    s1(b) = d
                    s2(b) = 0_8
                    s3(b) = 0_8
                    p = 1_8
                end if
            end if
            if ((a == 3_8)) then
                p = 2_8
            end if
            if ((a == 1_8)) then
                if ((c <= s0(b))) then
                    u = mod(((d + 64_8) - s1(b)), 64_8)
                    if ((u > 0_8)) then
                        if ((u < 32_8)) then
                            v = (s2(b) + e)
                            if ((v >= 0_8)) then
                                if ((v <= 105_8)) then
                                    s1(b) = d
                                    s2(b) = v
                                    s3(b) = f
                                    p = 1_8
                                end if
                            end if
                        end if
                    end if
                end if
            end if
            q = s0(b)
            r = s1(b)
            s = s2(b)
        end if
        write(*,'(i0,1x,i0,1x,i0,1x,i0)') p, q, r, s
    end do
end program main
