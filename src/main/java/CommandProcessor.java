public class CommandProcessor {
    Bank bank;

    public CommandProcessor(Bank bank) {
        this.bank = bank;
    }

    public Processor createProcessor(String command) {
        String[] Array = command.toLowerCase().split(" ");

        if (Array[0].equals("create")) {
            return new createProcessor(bank).process(Array);
        } else if (Array[0].equals("deposit")) {
            return new depositProcessor(bank);
        } else {
            return new falseProcessor(bank);
        }
    }
}

