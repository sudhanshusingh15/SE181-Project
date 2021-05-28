package banking;

public class falseValidator extends commonValidator {
    public falseValidator(Bank bank){
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command){
        return false;
    }
}
