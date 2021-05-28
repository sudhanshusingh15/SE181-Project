package banking;

public class checkingValidator extends createValidator {
    public checkingValidator(Bank bank){
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command){
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 4){
            if (checkID(Array[2])){
                if (ID_exists(Array[2])){
                    if (check_apr_is_valid(Array[3])){
                        return true;
                    }
                }
            }
        } return false;
        }
    }


