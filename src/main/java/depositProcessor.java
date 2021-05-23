public class depositProcessor extends createProcessor{
    public depositProcessor(Bank bank){super(bank);}

    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        Double deposited_amount = Double.parseDouble(Array[2]);
        bank.deposit(ID,deposited_amount);
    }
}
