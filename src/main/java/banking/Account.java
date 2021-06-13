package banking;

public class Account {
    protected Integer accountID;
    protected String accountType;
    protected Double accountBalance;
    protected Double account_apr;
    protected Integer month;


    public Account(String accountType, Integer accountID, Double account_apr, Double depositedAmount, Integer month) {
        this.accountType = accountType;
        this.month = month;

        if (this.checkAccountID(accountID)) {
            this.accountID = accountID;
        }

        this.accountBalance = 0.0 + depositedAmount;

        if (this.checkApr(account_apr)) {
            this.account_apr = account_apr;
        }

    }

    //Getters
    public Integer getAccountID() {
        return this.accountID;
    }

    public String getAccountType() {
        return this.accountType;
    }

    public void setAccountType(String accountType) {
        this.accountType = accountType;
    }

    public Double getAccountBalance() {
        return this.accountBalance;
    }

    public void setAccountBalance(Double accountBalance) {
        this.accountBalance = accountBalance;
    }

    public Double getAccount_apr() {
        return this.account_apr;
    }

    public Integer getMonth(){
        return this.month;
    }

    //Setters
    public boolean setAccountID(Integer accountID) {
        if (checkAccountID(accountID)) {
            this.accountID = accountID;

            return true;
        }

        return false;
    }

    public boolean setAccount_apr(Double account_apr) {
        if (checkApr(account_apr)) {
            return true;
        }
        return false;
    }

    public void setMonth(){
        this.month++ ;
    }

    //Deposit into checking or savings account
    public void depositIntoAccount(Double depositAmount) {
        this.accountBalance += depositAmount;

    }

    //Withdraw from account
    public void withdrawFromAccount(Double withdrawAmount) {
        if (this.accountBalance - withdrawAmount >= 0) {
            this.accountBalance -= withdrawAmount;
        } else {
            this.accountBalance = 0.0;
        }
    }


    //Helper function for setAccountID()
    public boolean checkAccountID(Integer accountID) {
        int count = String.valueOf(accountID).length();
        if (count != 8) {
            return false;
        }

        return true;
    }

    //Helper function for setAccount_apr()
    public boolean checkApr(Double account_apr) {
        if (account_apr > 10.0 || account_apr < 0.0) {
            return false;
        }
        return true;
    }

    public void interestDeposit(Double Interest){
        this.accountBalance += Interest;
    }

}




