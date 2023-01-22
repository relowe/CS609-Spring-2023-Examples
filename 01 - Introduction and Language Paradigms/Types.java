public class Types {
   public static void main(String [] args) {
    int x=0;
    double d = 1.9999999;

    // NOTE: In java we have to cast to do this
    x = (int) d;
    d = x;
    System.out.printf("x: %d, d: %f\n", x, d);
   } 
}
