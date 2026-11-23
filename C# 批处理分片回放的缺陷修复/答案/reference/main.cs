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
            long p=0, q=0, r=0, s=0, u=0, v=0;
            if ((a != 0)) {
                if ((a == 2)) {
                    if ((c > s0[(int)(b)])) {
                        s0[(int)(b)] = c;
                        s1[(int)(b)] = d;
                        s2[(int)(b)] = 0;
                        s3[(int)(b)] = 0;
                        p = 1;
                    }
                }
                if ((a == 3)) {
                    p = 2;
                }
                if ((a == 1)) {
                    if ((c == s0[(int)(b)])) {
                        u = (((d + 64) - s1[(int)(b)]) % 64);
                        if ((u > 0)) {
                            if ((u < 32)) {
                                v = (s2[(int)(b)] + e);
                                if ((v >= 0)) {
                                    if ((v <= 87)) {
                                        s1[(int)(b)] = d;
                                        s2[(int)(b)] = v;
                                        s3[(int)(b)] = f;
                                        p = 1;
                                    }
                                }
                            }
                        }
                    }
                }
                q = s0[(int)(b)];
                r = s1[(int)(b)];
                s = s2[(int)(b)];
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
