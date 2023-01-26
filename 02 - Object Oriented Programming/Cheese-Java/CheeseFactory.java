import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

public class CheeseFactory {
    public static double makeCheese(Object m) throws NoSuchMethodException, IllegalArgumentException, InvocationTargetException, IllegalAccessException {
        //use introspection to find the milk method
        Class oc = m.getClass();
        Method milk = oc.getMethod("milk");

        // use intercession to invoke the method
        double milk_qty = (double) milk.invoke(m);

        // What I did above, is a very bad idea. 
        // Doing this throws away all of the OOP advantages.

        return milk_qty * 0.5;
    }

    public static void main(String [] args) {
        Cow c = new Cow();
        Goat g = new Goat();
        Soy s = new Soy();
        String str = "Hello";

        try {
            System.out.printf("The cow helped us make %f cheese.\n", makeCheese(c));
            System.out.printf("The goat helped us make %f cheese.\n", makeCheese(g));
            System.out.printf("The soy plant helped us make %f cheese.\n", makeCheese(s));
            System.out.printf("The string helped us make %f cheese.\n", makeCheese(str));
        } catch(Exception e) {
            System.out.println("Something went wrong");
        }

    }
}