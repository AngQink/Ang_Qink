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
                        u = (d - s1[(int)(b)]);
                        if ((u > 0)) {
                            v = (s2[(int)(b)] + e);
                            if ((v >= 0)) {
                                if ((v <= 66)) {
                                    s1[(int)(b)] = d;
                                    s2[(int)(b)] = v;
                                    s3[(int)(b)] = f;
                                    p = 1;
                                }
                            }
                        }
                    }
                }
                q = s0[(int)(b)];
                r = s1[(int)(b)];
                s = s2[(int)(b)];
            }
            System.out.println(p+" "+q+" "+r+" "+s);
        }
    }
}
