public class savingsProcessor extends createProcessor{
    public savingsProcessor(Bank bank){super(bank);}

    public void create_savings_account(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        double apr = Double.parseDouble(Array[2]);
        Account savings_account = new SavingsAccount(ID,apr);
        bank.addAccount(ID, savings_account);
    }
}
