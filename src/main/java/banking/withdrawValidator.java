package banking;

public class withdrawValidator extends commonValidator {
    public withdrawValidator(Bank bank) {
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 3) {
            if (checkID(Array[1])) {
                if (!ID_exists(Array[1])) {
                    if (check_withdraw_isValid(Array)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    protected boolean check_withdraw_isValid(String[] array){
        Integer ID = Integer.parseInt(array[1]);
        Double Withdraw = Double.parseDouble(array[2]);
        return bank.checkWithdraw(ID, Withdraw);
    }
}
