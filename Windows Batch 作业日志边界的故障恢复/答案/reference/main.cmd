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
if !a! NEQ 0 (
    if !a! EQU 1 (
        if !c! GTR !s0_%b%! (
            if !c! GTR !s1_%b%! (
                set /a "s1_%b%=c"
                set /a "s3_%b%=d"
                set /a "p=1"
            )
        )
    )
    if !a! EQU 2 (
        if !c! EQU !s1_%b%! (
            if !c! GTR !s0_%b%! (
                set /a "u=(((((c * 19) + ((s3_%b% + 100) * 7)) + b) + 33) %% 257)"
                if !d! EQU !u! (
                    set /a "s0_%b%=c"
                    set /a "s1_%b%=0"
                    set /a "s2_%b%=s3_%b%"
                    set /a "s3_%b%=0"
                    set /a "p=1"
                )
            )
        )
    )
    if !a! EQU 3 (
        set /a "s1_%b%=0"
        set /a "s3_%b%=0"
        set /a "p=2"
    )
    if !a! EQU 4 (
        set /a "p=3"
    )
    set /a "q=s0_%b%"
    set /a "r=s2_%b%"
    set /a "s=s1_%b%"
)
echo !p! !q! !r! !s!
exit /b 0
