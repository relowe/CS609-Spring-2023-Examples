import java.security.Identity;

// Encapsulation in Java
//    public - Everyone has access
//    private - Only the class has access
// CAUTION, the two below violate OOP principles
//    protected - Only the class and subclasses 
//    < package > - Only code within the same package
public class Person {
    // Attributes (should be private)
    private String name;
    private String id;
    private String email;

    // Constructor
    public Person() {
        // blank
    }


    public String getName(){
        return name;
    }

    public void setName(String name) {
        this.name = name;

    }


    public String getId(){
        return id;
    }

    public void setId(String id) {
        this.id = id;

    }

    public String getEmail(){
        return email;
    }

    public void setEmail(String email) {
        this.email = email;

    }

    
}