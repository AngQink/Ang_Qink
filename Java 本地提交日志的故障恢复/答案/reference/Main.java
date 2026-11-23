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
            long a=Long.parseLong(tok[0]), b=Long.parseLong(tok[1]), c=Long.parseLong(tok[2]), d=Long.parseLong(tok[3]);
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
                            u = (((((c * 4) + ((s3[(int)(b)] + 100) * 8)) + b) + 18) % 257);
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
            System.out.println(p+" "+q+" "+r+" "+s);
        }
    }
}
