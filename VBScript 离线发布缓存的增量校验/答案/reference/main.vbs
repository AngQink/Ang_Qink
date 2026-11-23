Option Explicit
Dim s0(31)
Dim s1(31)
Dim s2(31)
Dim s3(31)
Dim a, b, c, d, e, f, p, q, r, s, i, tokens
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
    If (a <> 0) Then
        If (a = 1) Then
            s0(b) = (((((((c * 41) + (d * 28)) + (e * 7)) + f) + 32) Mod 4093) + 1)
            s1(b) = (((((d * 18) + (f * 14)) + (e * 23)) Mod 1297) + 1)
        End If
        If (a = 2) Then
            If (s0(b) <> 0) Then
                If (c = s0(b)) Then
                    If (d = s1(b)) Then
                        s2(b) = c
                        s3(b) = d
                        p = 1
                    End If
                End If
            End If
        End If
        If (a = 3) Then
            If (s2(b) <> 0) Then
                If (c = s2(b)) Then
                    If (d = s3(b)) Then
                        s2(b) = 0
                        s3(b) = 0
                        p = 1
                    End If
                End If
            End If
        End If
        q = s0(b)
        r = s1(b)
        If (q <> 0) Then
            If (q = s2(b)) Then
                If (r = s3(b)) Then
                    s = 1
                End If
            End If
            If (a = 1) Then
                p = (3 - s)
            End If
            If (a = 4) Then
                p = (3 - s)
            End If
        End If
    End If
    WScript.Echo p & " " & q & " " & r & " " & s
Loop
