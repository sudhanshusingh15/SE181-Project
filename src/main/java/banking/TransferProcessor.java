package banking;

public class TransferProcessor extends Processor{
    public TransferProcessor(Bank bank){super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID_1 = Integer.parseInt(Array[1]);
        Integer ID_2 = Integer.parseInt(Array[2]);
        Double amount = Double.parseDouble(Array[3]);
        bank.withdraw(ID_1, amount);
        bank.deposit(ID_2,amount);

    }
}
