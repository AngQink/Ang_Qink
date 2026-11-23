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
            long a=long.Parse(tok[0]), b=long.Parse(tok[1]), c=long.Parse(tok[2]), d=long.Parse(tok[3]), e=long.Parse(tok[4]);
            long p=0, q=0, r=0, s=0, u=0, v=0, w=0;
            if ((a == 1)) {
                p = (-1);
                u = ((((((c * 11) + s0[(int)(b)]) + (e * 7)) + (b * 21)) + 25) % 251);
                if ((u == d)) {
                    w = (((((s0[(int)(b)] * 21) + (e * 27)) + b) + 25) % 2048);
                    v = ((((c + 2048) - w) * 539) % 2048);
                    if ((v < 1024)) {
                        s = (v % 4);
                        v = (v / 4);
                        q = (v % 8);
                        v = (v / 8);
                        r = (v % 32);
                        v = (v / 32);
                        r = (r - 16);
                        s0[(int)(b)] = (((c + d) + s0[(int)(b)]) % 2048);
                        p = 1;
                    }
                }
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
