package banking;

public class Processor {
    protected Bank bank;

    public Processor(Bank bank){this.bank = bank;}

    public void execute(String string) {System.err.println(string);}


}

