@echo off
setlocal EnableExtensions EnableDelayedExpansion
for /f "usebackq tokens=1-6" %%A in ("%~1") do call :step %%A %%B %%C %%D %%E %%F
exit /b 0

:step
set /a a=%1
set /a b=%2
set /a c=%3
set /a d=%4
set /a e=%5
set /a f=%6
if !a! EQU 0 for /l %%I in (0,1,31) do (set /a s0_%%I=0 & set /a s1_%%I=0 & set /a s2_%%I=0 & set /a s3_%%I=0)
set /a p=0
set /a q=0
set /a r=0
set /a s=0
set /a u=0
set /a v=0
if !a! NEQ 0 (
    if !a! EQU 2 (
        if !c! GTR !s0_%b%! (
            set /a "s0_%b%=c"
            set /a "s1_%b%=d"
            set /a "s2_%b%=0"
            set /a "s3_%b%=0"
            set /a "p=1"
        )
    )
    if !a! EQU 3 (
        set /a "p=2"
    )
    if !a! EQU 1 (
        if !c! EQU !s0_%b%! (
            set /a "u=(d - s1_%b%)"
            if !u! GTR 0 (
                set /a "v=(s2_%b% + e)"
                if !v! GEQ 0 (
                    if !v! LEQ 111 (
                        set /a "s1_%b%=d"
                        set /a "s2_%b%=v"
                        set /a "s3_%b%=f"
                        set /a "p=1"
                    )
                )
            )
        )
    )
    set /a "q=s0_%b%"
    set /a "r=s1_%b%"
    set /a "s=s2_%b%"
)
echo !p! !q! !r! !s!
exit /b 0
