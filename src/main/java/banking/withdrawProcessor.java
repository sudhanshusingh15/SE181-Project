package banking;

public class withdrawProcessor extends Processor{
    public withdrawProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        Double withdrawal_amount = Double.parseDouble(Array[2]);
        bank.withdraw(ID, withdrawal_amount);
    }
}
