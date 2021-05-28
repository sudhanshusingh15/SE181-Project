package banking;

public class commonValidator {
    Bank bank;

    public commonValidator(Bank bank) {
        this.bank = bank;
    }

    protected boolean checkID(String ID_String) {
        try {
            Integer ID = Integer.parseInt(ID_String);
            System.err.println(ID);
            if(ID_String.length()==8)
                return true;
            else
                return false;
        } catch (NumberFormatException e){
            return false;
        }
    }


    protected boolean ID_exists(String ID_String){
        Integer ID = Integer.parseInt(ID_String);
        if (bank.getAccounts().get(ID) != null)
            return false;
        else
            return true;
    }

    protected boolean check_apr_is_valid(String Apr_String){
        try{
            Double APR = Double.parseDouble(Apr_String);
            if (APR >= 0.0 && APR <= 10.0)
                return true;
            else
                return false;
        } catch (NumberFormatException e){
            return false;
        }
    }

    protected boolean check_deposited_amount(String Deposited_Amount_String){
        try {
            Double Deposited_Amount = Double.parseDouble(Deposited_Amount_String);
            if (Deposited_Amount >= 1000.0 && Deposited_Amount <= 10000.0)
                return true;
            else
                return false;
        } catch (NumberFormatException e){
            return false;
        }
    }

    public boolean check_if_valid(String command){
        return false;
    }



}
