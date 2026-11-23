using System;
public class Entry {
    static void Main() {

        long[] s0=new long[32];
        long[] s1=new long[32];
        long[] s2=new long[32];
        long[] s3=new long[32];
        string line;
        while ((line=Console.ReadLine())!=null) {
            string[] tok=line.Split(' ');
            if (tok[0]=="0") { s0=new long[32]; s1=new long[32]; s2=new long[32]; s3=new long[32]; }
            long a=long.Parse(tok[0]), b=long.Parse(tok[1]), c=long.Parse(tok[2]), d=long.Parse(tok[3]), e=long.Parse(tok[4]), f=long.Parse(tok[5]);
            long p=0, q=0, r=0, s=0;
            if ((a != 0)) {
                if ((a == 1)) {
                    s0[(int)(b)] = (((((((c * 27) + (d * 21)) + (e * 7)) + f) + 25) % 4093) + 1);
                    s1[(int)(b)] = (((((d * 11) + (f * 7)) + (e * 23)) % 1297) + 1);
                }
                if ((a == 2)) {
                    if ((s0[(int)(b)] != 0)) {
                        if ((c == s0[(int)(b)])) {
                            if ((d == s1[(int)(b)])) {
                                s2[(int)(b)] = c;
                                s3[(int)(b)] = d;
                                p = 1;
                            }
                        }
                    }
                }
                if ((a == 3)) {
                    if ((s2[(int)(b)] != 0)) {
                        if ((c == s2[(int)(b)])) {
                            if ((d == s3[(int)(b)])) {
                                s2[(int)(b)] = 0;
                                s3[(int)(b)] = 0;
                                p = 1;
                            }
                        }
                    }
                }
                q = s0[(int)(b)];
                r = s1[(int)(b)];
                if ((q != 0)) {
                    if ((q == s2[(int)(b)])) {
                        if ((r == s3[(int)(b)])) {
                            s = 1;
                        }
                    }
                    if ((a == 1)) {
                        p = (3 - s);
                    }
                    if ((a == 4)) {
                        p = (3 - s);
                    }
                }
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
