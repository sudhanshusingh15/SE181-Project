package banking;

public class savingsProcessor extends createProcessor{
    public savingsProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[2]);
        double apr = Double.parseDouble(Array[3]);
        Account savings_account = new SavingsAccount(ID,apr);
        bank.addAccount(ID, savings_account);
    }
}
