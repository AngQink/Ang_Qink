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
            long a=long.Parse(tok[0]);
            long p=0, q=0, r=0, s=0;
            if ((a != 0)) {
                p = 0;
            }
            Console.WriteLine("{0} {1} {2} {3}",p,q,r,s);
        }
    }
}
