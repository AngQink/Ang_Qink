program main
    implicit none
    integer :: status
    integer(kind=8) :: a, b, c, d, e, f, p, q, r, s, u
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
        if ((a /= 0_8)) then
            if ((a == 1_8)) then
                if ((c > s0(b))) then
                    if ((c > s1(b))) then
                        s1(b) = c
                        s3(b) = d
                        p = 1_8
                    end if
                end if
            end if
            if ((a == 2_8)) then
                if ((c == s1(b))) then
                    if ((c > s0(b))) then
                        u = mod(((((c * 17_8) + ((s3(b) + 100_8) * 13_8)) + b) + 31_8), 257_8)
                        if ((d == u)) then
                            s0(b) = c
                            s1(b) = 0_8
                            s2(b) = s3(b)
                            s3(b) = 0_8
                            p = 1_8
                        end if
                    end if
                end if
            end if
            if ((a == 3_8)) then
                s1(b) = 0_8
                s3(b) = 0_8
                p = 2_8
            end if
            if ((a == 4_8)) then
                p = 3_8
            end if
            q = s0(b)
            r = s2(b)
            s = s1(b)
        end if
        write(*,'(i0,1x,i0,1x,i0,1x,i0)') p, q, r, s
    end do
end program main
