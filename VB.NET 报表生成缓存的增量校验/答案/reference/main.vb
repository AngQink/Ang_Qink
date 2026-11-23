Imports System
Module Entry
    Sub Main()
        Dim s0(31) As Long
        Dim s1(31) As Long
        Dim s2(31) As Long
        Dim s3(31) As Long
        Dim a, b, c, d, e, f, p, q, r, s, i As Long
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
            If (a <> 0) Then
                If (a = 1) Then
                    s0(b) = (((((((c * 29) + (d * 22)) + (e * 7)) + f) + 26) Mod 4093) + 1)
                    s1(b) = (((((d * 12) + (f * 8)) + (e * 23)) Mod 1297) + 1)
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
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s)
        End While
    End Sub
End Module
