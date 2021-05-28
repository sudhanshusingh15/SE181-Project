public class CDValidator extends createValidator {
    public CDValidator(Bank bank) {
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 5) {
            if (checkID(Array[2])) {
                if (ID_exists(Array[2])) {
                    if (check_apr_is_valid(Array[3])) {
                        if (check_deposited_amount(Array[4])) {
                            return true;
                        }
                    }
                }
            }
        } return false;
    }
}


