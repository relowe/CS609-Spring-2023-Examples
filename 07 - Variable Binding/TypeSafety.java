public class TypeSafety {
    public static int f(int x, int y) {
        return x+y;
    }    

    public static void main(String [] args) {
        double d;
        int x;

        x = f(1,2);
        d = x;  // widening happens implicitly (coercion)
        x = (int) d; //narrowing requires a cast
    }
}
