public class blockScopeDemo {
    private static int x;

    public static void main(String [] args) {
        x = 5;

        {
            int x = 7;
            int y = 12;
            System.out.printf("Inside the block x=%d\n", x);
            System.out.printf("Inside the block y=%d\n", y);
        }

        System.out.printf("Outside the block x=%d\n", x);
        // You can't do this: System.out.printf("Outside the block y=%d\n", y);
        // y is not defined in this lexicographical scope
    }
}