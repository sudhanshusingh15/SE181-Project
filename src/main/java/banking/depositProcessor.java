package banking;

import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.ArrayList;

public class depositProcessor extends Processor{
    Account account;
    public depositProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        Integer deposited_amount = Integer.parseInt(Array[2]);
        bank.deposit(ID,deposited_amount);
        bank.getAccounts().get(ID).getTransactionHistory().add("Deposit " + ID + " " + deposited_amount);
    }
}
