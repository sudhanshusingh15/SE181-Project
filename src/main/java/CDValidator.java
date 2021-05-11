public class CDValidator extends createValidator {
    public CDValidator(Bank bank) {
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 5) {
            System.out.println("1");
            if (checkID(Array[2])) {
                System.out.println("2");
                if (ID_exists(Array[2])) {
                    System.out.println("3");
                    if (check_apr_is_valid(Array[3])) {
                        System.out.println("4");
                        if (check_deposited_amount(Array[4])) {
                            System.out.println("5");
                            return true;
                        }
                    }
                }
            }
        } return false;
    }
}


