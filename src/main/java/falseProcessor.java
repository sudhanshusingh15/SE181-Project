public class falseProcessor extends Processor {
    public falseProcessor(Bank bank) {super(bank);}

    @Override
    public void execute(String string) {System.err.println(string);}

}
