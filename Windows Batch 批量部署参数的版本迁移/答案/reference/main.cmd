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
        set /a "u=(c / 3)"
        set /a "s0_%b%=1"
        set /a "s1_%b%=(u + (e * 18))"
    )
    if !a! EQU 2 (
        set /a "s2_%b%=c"
        set /a "s3_%b%=0"
        if !c! EQU 1 (
            set /a "s3_%b%=d"
        )
    )
    if !s2_%b%! EQU 1 (
        set /a "p=1"
        set /a "q=s3_%b%"
    )
    if !s2_%b%! EQU 0 (
        if !s0_%b%! NEQ 0 (
            set /a "p=1"
            set /a "q=s1_%b%"
        )
    )
    if !s2_%b%! EQU 2 (
        set /a "p=2"
    )
    set /a "r=s1_%b%"
    set /a "s=s0_%b%"
)
echo !p! !q! !r! !s!
exit /b 0
