package banking;

public class checkingProcessor extends createProcessor{
    public checkingProcessor(Bank bank){super(bank);}

    @Override
    public void execute (String command){

        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[2]);
        double apr = Double.parseDouble(Array[3]);
        Account checking_account = new CheckingAccount(ID, apr);
        bank.addAccount(ID, checking_account);

    }
}
