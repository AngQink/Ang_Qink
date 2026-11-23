Imports System
Module Entry
    Sub Main()
        Dim s0(31) As Long
        Dim s1(31) As Long
        Dim s2(31) As Long
        Dim s3(31) As Long
        Dim a, b, c, d, e, f, p, q, r, s, u, i As Long
        While True
            Dim line As String=Console.ReadLine()
            If line Is Nothing Then Exit While
            Dim tokens As String()=line.Split(" "c)
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
            If (a <> 0) Then
                If (a = 1) Then
                    u = (c \ 6)
                    If ((c Mod 6) <> 0) Then
                        u = (u + 1)
                    End If
                    s0(b) = 1
                    s1(b) = (u + (e * 11))
                    If (d = 0) Then
                        s0(b) = 0
                        s1(b) = 0
                    End If
                End If
                If (a = 2) Then
                    s2(b) = c
                    s3(b) = 0
                    If (c = 1) Then
                        s3(b) = d
                    End If
                End If
                If (s2(b) = 1) Then
                    p = 1
                    q = s3(b)
                End If
                If (s2(b) = 0) Then
                    If (s0(b) <> 0) Then
                        p = 1
                        q = s1(b)
                    End If
                End If
                If (s2(b) = 2) Then
                    p = 2
                End If
                r = s1(b)
                s = s0(b)
            End If
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s)
        End While
    End Sub
End Module
