Option Explicit
Dim s0(31)
Dim s1(31)
Dim s2(31)
Dim s3(31)
Dim a, b, c, d, e, f, p, q, r, s, u, v, i, tokens
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
    If (a <> 0) Then
        If (a = 2) Then
            If (c > s0(b)) Then
                s0(b) = c
                s1(b) = d
                s2(b) = 0
                s3(b) = 0
                p = 1
            End If
        End If
        If (a = 3) Then
            p = 2
        End If
        If (a = 1) Then
            If (c = s0(b)) Then
                u = (d - s1(b))
                If (u = 1) Then
                    v = (s2(b) + e)
                    If (v >= 0) Then
                        If (v <= 108) Then
                            s1(b) = d
                            s2(b) = v
                            s3(b) = f
                            p = 1
                        End If
                    End If
                End If
            End If
        End If
        q = s0(b)
        r = s1(b)
        s = s2(b)
    End If
    WScript.Echo p & " " & q & " " & r & " " & s
Loop
