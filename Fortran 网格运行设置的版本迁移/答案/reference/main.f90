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
                u = (c / 6_8)
                s0(b) = 1_8
                s1(b) = (u + (e * 16_8))
            end if
            if ((a == 2_8)) then
                s2(b) = c
                s3(b) = 0_8
                if ((c == 1_8)) then
                    s3(b) = d
                end if
            end if
            if ((s2(b) == 1_8)) then
                p = 1_8
                q = s3(b)
            end if
            if ((s2(b) == 0_8)) then
                if ((s0(b) /= 0_8)) then
                    p = 1_8
                    q = s1(b)
                end if
            end if
            if ((s2(b) == 2_8)) then
                p = 2_8
            end if
            r = s1(b)
            s = s0(b)
        end if
        write(*,'(i0,1x,i0,1x,i0,1x,i0)') p, q, r, s
    end do
end program main
