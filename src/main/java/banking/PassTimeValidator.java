package banking;

public class PassTimeValidator extends commonValidator {
    public PassTimeValidator(Bank bank) {
        super(bank);
    }

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 2) {
            Integer month = Integer.parseInt(Array[1]);
            if (month > 0 && month <= 60) {
                return true;
            }
        }
        return false;
    }
}
