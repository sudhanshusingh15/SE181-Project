public class Account {
    private Integer accountID;
    private String accountType;
    private Double accountBalance;
    private Double account_apr;


    public Account(String accountType, Integer accountID, Double account_apr, Double depositedAmount) {
        this.accountType = accountType;

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

    //Deposit into checking or savings account
    public void depositIntoAccount(Double depositAmount) {
        this.accountBalance += depositAmount;

    }

    //Deposit into CD account
    //   public void depositIntoCDAccount(Double depositAmount) {
    //       this.accountBalance = depositAmount;
    //   }

    //Withdraw from account
    public void withdrawFromAccount(Double withdrawAmount) {
        if (this.accountBalance - withdrawAmount >= 0) {
            this.accountBalance -= withdrawAmount;
        }
    }

    //Helper function for setAccountID()
    public Boolean checkAccountID(Integer accountID) {
        int count = String.valueOf(accountID).length();
        if (count > 8 || count < 8) {
            return false;
        }

        return true;
    }

    //Helper function for setAccount_apr()
    public Boolean checkApr(Double account_apr) {
        if (account_apr > 10.0 || account_apr < 0.0) {
            return false;
        }
        return true;
    }

}




