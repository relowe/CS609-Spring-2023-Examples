public class SideEffect
{
    public static void main(String [] args) {
        int x=0;

        System.out.print("X Before: ");
        System.out.println(x);

        System.out.print("X=5 Effect: ");
        System.out.println(x=5);

        System.out.print("X=5 Side Effect X after: ");
        System.out.println(x);
    }
}