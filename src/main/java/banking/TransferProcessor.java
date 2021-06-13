package banking;

import java.math.RoundingMode;
import java.text.DecimalFormat;

public class TransferProcessor extends Processor{
    public TransferProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID_1 = Integer.parseInt(Array[1]);
        Integer ID_2 = Integer.parseInt(Array[2]);
        Integer amount = Integer.parseInt(Array[3]);
        bank.withdraw(ID_1, amount);
        bank.deposit(ID_2,amount);
        bank.getAccounts().get(ID_1).getTransactionHistory().add("Transfer " + ID_1 + " " + ID_2 + " " + amount);
        bank.getAccounts().get(ID_2).getTransactionHistory().add("Transfer " + ID_1 + " " + ID_2 + " " + amount);
    }
}
