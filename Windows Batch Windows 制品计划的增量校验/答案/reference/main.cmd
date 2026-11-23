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
if !a! NEQ 0 (
    if !a! EQU 1 (
        set /a "s0_%b%=(((((((c * 43) + (d * 29)) + (e * 7)) + f) + 33) %% 4093) + 1)"
        set /a "s1_%b%=(((((d * 19) + (f * 7)) + (e * 23)) %% 1297) + 1)"
    )
    if !a! EQU 2 (
        if !s0_%b%! NEQ 0 (
            if !c! EQU !s0_%b%! (
                if !d! EQU !s1_%b%! (
                    set /a "s2_%b%=c"
                    set /a "s3_%b%=d"
                    set /a "p=1"
                )
            )
        )
    )
    if !a! EQU 3 (
        if !s2_%b%! NEQ 0 (
            if !c! EQU !s2_%b%! (
                if !d! EQU !s3_%b%! (
                    set /a "s2_%b%=0"
                    set /a "s3_%b%=0"
                    set /a "p=1"
                )
            )
        )
    )
    set /a "q=s0_%b%"
    set /a "r=s1_%b%"
    if !q! NEQ 0 (
        if !q! EQU !s2_%b%! (
            if !r! EQU !s3_%b%! (
                set /a "s=1"
            )
        )
        if !a! EQU 1 (
            set /a "p=(3 - s)"
        )
        if !a! EQU 4 (
            set /a "p=(3 - s)"
        )
    )
)
echo !p! !q! !r! !s!
exit /b 0
