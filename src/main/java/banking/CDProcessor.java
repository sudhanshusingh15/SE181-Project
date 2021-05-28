package banking;

public class CDProcessor extends createProcessor{
    public CDProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[2]);
        double apr = Double.parseDouble(Array[3]);
        double deposited_amount = Double.parseDouble(Array[4]);
        Account cd_account = new CDAccount(ID, apr, deposited_amount);
        bank.addAccount(ID, cd_account);
    }
}
