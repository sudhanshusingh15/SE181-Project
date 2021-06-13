package banking;

import java.math.RoundingMode;
import java.text.DecimalFormat;

public class withdrawProcessor extends Processor{
    public withdrawProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        Integer withdrawal_amount = Integer.parseInt(Array[2]);
        bank.withdraw(ID, withdrawal_amount);
        bank.getAccounts().get(ID).getTransactionHistory().add("Withdraw " + ID + " " + withdrawal_amount );

    }
}
