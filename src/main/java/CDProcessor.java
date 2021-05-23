public class CDProcessor extends createProcessor{
    public CDProcessor(Bank bank){super(bank);}

    public void create_CD_account(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer ID = Integer.parseInt(Array[1]);
        double apr = Double.parseDouble(Array[2]);
        double deposited_amount = Double.parseDouble(Array[3]);
        Account cd_account = new CDAccount(ID, apr, deposited_amount);
        bank.addAccount(ID, cd_account);
    }
}
