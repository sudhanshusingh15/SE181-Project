import java.util.HashMap;

public class Bank {
    private HashMap<Integer, Account> accounts;

    Bank() {
        accounts = new HashMap<>();
    }

    public HashMap<Integer, Account> getAccounts() {
        return accounts;
    }

    public void addAccount(Integer Id, Account Account) {

        accounts.put(Id, Account);

    }

    public boolean checkDeposit(Integer ID, double amount){
        if (accounts.get(ID).getAccountType().equals("Checking")){
            if (amount > 0.0 && amount <= 1000.0)
                return true;
            else
                return false;
        }
        else if (accounts.get(ID).getAccountType().equals("Savings")){
            if (amount > 0.0 && amount <= 2500.0)
                return true;
            else
                return false;
        }
        else
            return false;
    }

    public void deposit(Integer ID, double amount) {
        if (checkDeposit(ID, amount)) {
            accounts.get(ID).depositIntoAccount(amount);
        }
    }


    public void withdraw(Integer ID, double amount) {
        double currAmount = accounts.get(ID).getAccountBalance();
        if (amount <= currAmount) {
            accounts.get(ID).withdrawFromAccount(amount);
        } else if (amount > currAmount) {
            accounts.get(ID).withdrawFromAccount(currAmount);
        }

    }
}