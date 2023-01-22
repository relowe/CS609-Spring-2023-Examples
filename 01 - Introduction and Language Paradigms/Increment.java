public class Increment {
    public static void main(String [] args) {
        int x;

        // perform each type of increment
        x=1;
        System.out.printf("x=x+1 is %d\n", x = x + 1);
        System.out.printf("After x + 1: %d\n", x);

        x=1;
        System.out.printf("++x is %d\n", ++x);
        System.out.printf("After ++x: %d\n", x);

        x=1;
        System.out.printf("x++ is %d\n", x++);
        System.out.printf("After x++: %d\n", x);

        x=1;
        System.out.printf("x+=1 is %d\n", x+=1);
        System.out.printf("After x+=1: %d\n", x);

        x="asdfasdf";
    }
    
}
