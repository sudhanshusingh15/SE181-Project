package banking;

public class CDAccount extends Account {
    public CDAccount(Integer accountID, Double account_apr, Double depositedAmount) {
        super("CD", accountID, account_apr, depositedAmount);
    }
}
