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
            long p=0, q=0, r=0, s=0, u=0;
            if ((a != 0)) {
                if ((a == 1)) {
                    u = (c / 5);
                    s0[(int)(b)] = 1;
                    s1[(int)(b)] = (u + (e * 10));
                }
                if ((a == 2)) {
                    s2[(int)(b)] = c;
                    s3[(int)(b)] = 0;
                    if ((c == 1)) {
                        s3[(int)(b)] = d;
                    }
                }
                if ((s2[(int)(b)] == 1)) {
                    p = 1;
                    q = s3[(int)(b)];
                }
                if ((s2[(int)(b)] == 0)) {
                    if ((s0[(int)(b)] != 0)) {
                        p = 1;
                        q = s1[(int)(b)];
                    }
                }
                if ((s2[(int)(b)] == 2)) {
                    p = 2;
                }
                r = s1[(int)(b)];
                s = s0[(int)(b)];
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
