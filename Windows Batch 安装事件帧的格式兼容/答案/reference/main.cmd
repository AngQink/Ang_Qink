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
set /a w=0
if !a! EQU 1 (
    set /a "p=(-1)"
    set /a "u=((((((c * 19) + s0_%b%) + (e * 7)) + (b * 29)) + 33) %% 251)"
    if !u! EQU !d! (
        set /a "w=(((((s0_%b% * 29) + (e * 43)) + b) + 33) %% 2048)"
        set /a "v=((((c + 2048) - w) * 1463) %% 2048)"
        if !v! LSS 1024 (
            set /a "r=(v %% 32)"
            set /a "v=(v / 32)"
            set /a "q=(v %% 8)"
            set /a "v=(v / 8)"
            set /a "s=(v %% 4)"
            set /a "v=(v / 4)"
            set /a "r=(r - 16)"
            set /a "s0_%b%=(((c + d) + s0_%b%) %% 2048)"
            set /a "p=1"
        )
    )
)
echo !p! !q! !r! !s!
exit /b 0
