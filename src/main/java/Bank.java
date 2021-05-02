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

    public void deposit(Integer ID, double amount) {
        if (amount > 0) {
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