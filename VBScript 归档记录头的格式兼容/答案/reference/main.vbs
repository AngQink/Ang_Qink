Option Explicit
Dim s0(31)
Dim s1(31)
Dim s2(31)
Dim s3(31)
Dim a, b, c, d, e, f, p, q, r, s, u, v, w, i, tokens
Do Until WScript.StdIn.AtEndOfStream
    tokens=Split(WScript.StdIn.ReadLine," ")
    a=CLng(tokens(0))
    b=CLng(tokens(1))
    c=CLng(tokens(2))
    d=CLng(tokens(3))
    e=CLng(tokens(4))
    f=CLng(tokens(5))
    If a=0 Then
        For i=0 To 31
            s0(i)=0
            s1(i)=0
            s2(i)=0
            s3(i)=0
        Next
    End If
    p=0
    q=0
    r=0
    s=0
    u=0
    v=0
    w=0
    If (a = 1) Then
        p = (-1)
        u = ((((((c * 18) + s0(b)) + (e * 14)) + (b * 28)) + 32) Mod 251)
        If (u = d) Then
            w = (((((s0(b) * 28) + (e * 41)) + b) + 32) Mod 2048)
            v = ((((c + 2048) - w) * 1229) Mod 2048)
            If (v < 1024) Then
                q = (v Mod 8)
                v = (v \ 8)
                s = (v Mod 4)
                v = (v \ 4)
                r = (v Mod 32)
                v = (v \ 32)
                r = (r - 16)
                s0(b) = (((c + d) + s0(b)) Mod 2048)
                p = 1
            End If
        End If
    End If
    WScript.Echo p & " " & q & " " & r & " " & s
Loop
