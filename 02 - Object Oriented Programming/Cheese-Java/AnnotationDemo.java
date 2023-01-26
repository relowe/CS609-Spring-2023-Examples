import java.lang.annotation.Annotation;

public class AnnotationDemo {
    public static void main(String [] args) {
        Dangerous d = new Dangerous();

        Class c = d.getClass();
        for(Annotation a : c.getAnnotations()) {
            System.out.println(a);
        }
    }    
}
