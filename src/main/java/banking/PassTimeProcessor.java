package banking;

public class PassTimeProcessor extends Processor {
    public PassTimeProcessor(Bank bank) {super(bank);}

    @Override
    public void execute(String command){
        String[] Array =  command.toLowerCase().split(" ");
        Integer month = Integer.parseInt(Array[1]);
        bank.pass_time_remove_account(month);
        bank.pass_time_deduction(month);
        bank.pass_time_apr_accrue(month);
    }
}
