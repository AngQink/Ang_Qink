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
            long a=Long.parseLong(tok[0]), b=Long.parseLong(tok[1]), c=Long.parseLong(tok[2]), d=Long.parseLong(tok[3]), e=Long.parseLong(tok[4]), f=Long.parseLong(tok[5]);
            long p=0, q=0, r=0, s=0;
            if ((a != 0)) {
                if ((a == 1)) {
                    s0[(int)(b)] = (((((((c * 13) + (d * 14)) + (e * 7)) + f) + 18) % 4093) + 1);
                    s1[(int)(b)] = (((((d * 4) + (f * 8)) + (e * 23)) % 1297) + 1);
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
            System.out.println(p+" "+q+" "+r+" "+s);
        }
    }
}
