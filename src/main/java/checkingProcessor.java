import java.util.Locale;

public class checkingProcessor extends createProcessor{
    public checkingProcessor(Bank bank){super(bank);}

    public void create_checking_account(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        double apr = Double.parseDouble(Array[2]);
        Account checking_account = new CheckingAccount(ID, apr);
        bank.addAccount(ID, checking_account);
    }
}
