public class CommandProcessor {
    Bank bank;
    Processor processor;

    public CommandProcessor(Bank bank){this.bank = bank;}

    public void execute(String command){
        String[] Array = command.toLowerCase().split(" ");

        switch(Array[0]){
            case "create":
                processor = new createProcessor(bank).generateCreate(Array);
                break;

            case "deposit" :
                processor = new depositProcessor(bank);
                break;

            default:
                break;
        }

    }
}

