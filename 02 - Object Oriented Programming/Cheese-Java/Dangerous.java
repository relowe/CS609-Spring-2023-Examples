import java.lang.annotation.Annotation;

public class Dangerous implements Annotation{

    @Override
    public Class<? extends Annotation> annotationType() {
        // TODO Auto-generated method stub
        return this.getClass();
    }
    
}
