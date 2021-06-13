package banking;

public class TransferValidator extends commonValidator {
    public TransferValidator(Bank bank) {super(bank);}

    @Override
    public boolean check_if_valid(String command) {
        String[] Array = command.toLowerCase().split(" ");
        if (Array.length == 4) {
            if ( (checkID(Array[1])) && (checkID(Array[2])) ) {
                if ( (!ID_exists(Array[1])) && (!ID_exists(Array[2])) ) {
                    if (check_transfer_isValid(Array)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    protected boolean check_transfer_isValid(String[] array){
        Integer ID_1 = Integer.parseInt(array[1]);
        Integer ID_2 = Integer.parseInt(array[2]);
        Double amount = Double.parseDouble(array[3]);

        if ( (bank.checkWithdraw(ID_1,amount)) && (bank.checkDeposit(ID_2, amount)) && (bank.checkTransfer(ID_1)) && (bank.checkTransfer(ID_2)) ){
            return true;
        } else{
            return false;
        }
    }
}
