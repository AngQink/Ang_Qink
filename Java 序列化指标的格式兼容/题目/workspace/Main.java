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
            long a=Long.parseLong(tok[0]);
            long p=0, q=0, r=0, s=0;
            if ((a != 0)) {
                p = 0;
            }
            System.out.println(p+" "+q+" "+r+" "+s);
        }
    }
}
