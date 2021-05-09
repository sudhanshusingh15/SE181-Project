public class createValidator extends commonValidator{
    public createValidator(Bank bank){
        super(bank);
    }

    public commonValidator checkAccountType(String[] Array){
        if(Array[1].equals("checking")){
            return new checkingValidator(bank);
        }
        else if(Array[1].equals("savings")){
            return new savingsValidator(bank);
        }
        else if(Array[1].equals("cd")){
            return new CDValidator(bank);
        } else {
            return new falseValidator(bank);
        }
    }

}

