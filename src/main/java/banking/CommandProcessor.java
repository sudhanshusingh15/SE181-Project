package banking;

public class CommandProcessor {
    Bank bank;

    public CommandProcessor(Bank bank) {
        this.bank = bank;
    }

    public Processor Process(String command) {
        String[] Array = command.toLowerCase().split(" ");

        if (Array[0].equals("create")) {
            return new createProcessor(bank).createAccountProcessor(Array);
        }
        else if (Array[0].equals("deposit")) {
            return new depositProcessor(bank);
        }
        else if (Array[0].equals("withdraw")){
            return new withdrawProcessor(bank);
        }
        else if (Array[0].equals("transfer")){
            return new TransferProcessor(bank);
        }
//        else if (Array[0].equals("pass")){
//            return new PassTimeProcessor(bank);
//        }
        else {
            return new falseProcessor(bank);
        }
    }
}

