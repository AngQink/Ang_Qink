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
            long a=long.Parse(tok[0]), b=long.Parse(tok[1]), c=long.Parse(tok[2]), d=long.Parse(tok[3]);
            long p=0, q=0, r=0, s=0, u=0;
            if ((a != 0)) {
                if ((a == 1)) {
                    if ((c > s0[(int)(b)])) {
                        if ((c > s1[(int)(b)])) {
                            s1[(int)(b)] = c;
                            s3[(int)(b)] = d;
                            p = 1;
                        }
                    }
                }
                if ((a == 2)) {
                    if ((c == s1[(int)(b)])) {
                        if ((c > s0[(int)(b)])) {
                            u = (((((c * 11) + ((s3[(int)(b)] + 100) * 7)) + b) + 25) % 257);
                            if ((d == u)) {
                                s0[(int)(b)] = c;
                                s1[(int)(b)] = 0;
                                s2[(int)(b)] = s3[(int)(b)];
                                s3[(int)(b)] = 0;
                                p = 1;
                            }
                        }
                    }
                }
                if ((a == 3)) {
                    s1[(int)(b)] = 0;
                    s3[(int)(b)] = 0;
                    p = 2;
                }
                if ((a == 4)) {
                    p = 3;
                }
                q = s0[(int)(b)];
                r = s2[(int)(b)];
                s = s1[(int)(b)];
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
