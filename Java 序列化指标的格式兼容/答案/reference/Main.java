import java.io.*;
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader reader=new BufferedReader(new InputStreamReader(System.in));
        long[] s0=new long[32];
        long[] s1=new long[32];
        long[] s2=new long[32];
        long[] s3=new long[32];
        String line;
        while ((line=reader.readLine())!=null) {
            String[] tok=line.split(" ");
            if (tok[0].equals("0")) { s0=new long[32]; s1=new long[32]; s2=new long[32]; s3=new long[32]; }
            long a=Long.parseLong(tok[0]), b=Long.parseLong(tok[1]), c=Long.parseLong(tok[2]), d=Long.parseLong(tok[3]), e=Long.parseLong(tok[4]);
            long p=0, q=0, r=0, s=0, u=0, v=0, w=0;
            if ((a == 1)) {
                p = (-1);
                u = ((((((c * 4) + s0[(int)(b)]) + (e * 8)) + (b * 14)) + 18) % 251);
                if ((u == d)) {
                    w = (((((s0[(int)(b)] * 14) + (e * 13)) + b) + 18) % 2048);
                    v = ((((c + 2048) - w) * 1229) % 2048);
                    if ((v < 1024)) {
                        r = (v % 32);
                        v = (v / 32);
                        s = (v % 4);
                        v = (v / 4);
                        q = (v % 8);
                        v = (v / 8);
                        r = (r - 16);
                        s0[(int)(b)] = (((c + d) + s0[(int)(b)]) % 2048);
                        p = 1;
                    }
                }
            }
            System.out.println(p+" "+q+" "+r+" "+s);
        }
    }
}
