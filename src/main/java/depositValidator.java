import java.lang.reflect.Array;

public class depositValidator extends commonValidator {
    public depositValidator(Bank bank) {
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 3) {
            if (checkID(Array[1])) {
                if (ID_exists(Array[1])) {
                    if (check_deposit_isValid(Array)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    protected boolean check_deposit_isValid(String[] array){
        Integer ID = Integer.parseInt(array[1]);
        Double Deposit = Double.parseDouble(array[2]);
        return bank.checkDeposit(ID, Deposit);
    }
}