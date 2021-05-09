public class FullCommandValidator {
    public Bank bank;

    public FullCommandValidator(Bank bank){
        this.bank = bank;
    }

    public commonValidator Validator(String command){
        String[] Array = command.toLowerCase().split(" ");
            if(Array[0].equals("create")){
                return new createValidator(bank).checkAccountType(Array);
            }
            else if (Array[0].equals("deposit")){
                return new depositValidator(bank);
            } else {
                return new falseValidator(bank);
            }
    }
}