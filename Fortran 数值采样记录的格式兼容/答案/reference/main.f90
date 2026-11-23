program main
    implicit none
    integer :: status
    integer(kind=8) :: a, b, c, d, e, f, p, q, r, s, u, v, w
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
        w=0
        if ((a == 1_8)) then
            p = (-1_8)
            u = mod((((((c * 17_8) + s0(b)) + (e * 13_8)) + (b * 27_8)) + 31_8), 251_8)
            if ((u == d)) then
                w = mod(((((s0(b) * 27_8) + (e * 39_8)) + b) + 31_8), 2048_8)
                v = mod((((c + 2048_8) - w) * 683_8), 2048_8)
                if ((v < 1024_8)) then
                    s = mod(v, 4_8)
                    v = (v / 4_8)
                    q = mod(v, 8_8)
                    v = (v / 8_8)
                    r = mod(v, 32_8)
                    v = (v / 32_8)
                    r = (r - 16_8)
                    s0(b) = mod(((c + d) + s0(b)), 2048_8)
                    p = 1_8
                end if
            end if
        end if
        write(*,'(i0,1x,i0,1x,i0,1x,i0)') p, q, r, s
    end do
end program main
