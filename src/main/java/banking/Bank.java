package banking;

import java.util.HashMap;
import java.util.Map;

public class Bank {
    private HashMap<Integer, Account> accounts;

    Bank() {
        accounts = new HashMap<>();
    }

    public HashMap<Integer, Account> getAccounts() {
        return accounts;
    }

    public void addAccount(Integer ID, Account Account) {

        accounts.put(ID, Account);

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

    public boolean checkWithdraw(Integer ID, double amount){
        if (accounts.get(ID).getAccountType().equals("Checking")){
            if (amount > 0.0 && amount <= 400.0)
                return true;
            else
                return false;
        }
        else if (accounts.get(ID).getAccountType().equals("Savings")){
            if (amount > 0.0 && amount <= 1000.0)
                return true;
            else
                return false;
        }
        else
            return false;
    }

    public boolean checkTransfer(Integer ID){
        if (accounts.get(ID).getAccountType().equals("CD")){
            return false;
        } else{
            return true;
        }
    }

    public void withdraw(Integer ID, double amount) {
        if(checkWithdraw(ID, amount)){
            double currAmount = accounts.get(ID).getAccountBalance();
            if (amount <= currAmount) {
                accounts.get(ID).withdrawFromAccount(amount);
            } else if (amount > currAmount) {
                accounts.get(ID).withdrawFromAccount(currAmount);
            }
        }
    }

//    public void pass_time_remove_account(Integer month){
//        while (month !=0){
//            for (Integer key : accounts.keySet()){
//                if (accounts.get(key).getAccountBalance() == 0){
//                    accounts.remove(key);
//                } else {
//                    accounts.get(key).setMonth();
//                }
//
//            }
//            month-- ;
//        }
//    }
//
//    public void pass_time_deduction(Integer month){
//        while (month != 0) {
//            for (Integer key : accounts.keySet()){
//                if (accounts.get(key).getAccountBalance() < 100.0){
//                    accounts.get(key).withdrawFromAccount(25.0);
//                }
//                accounts.get(key).setMonth();
//            }
//            month-- ;
//        }
//    }
//
//    public void pass_time_apr_accrue(Integer month){
//        while (month != 0){
//            for (Map.Entry mapElement : accounts.entrySet()){
//                Integer key = (Integer)mapElement.getKey();
//                Double APR = accounts.get(key).getAccount_apr();
//                APR = (APR/100.0)/12.0;
//                Double Interest = 0.0;
//                if (accounts.get(key).getAccountType().equals("CD")){
//                    Interest = (accounts.get(key).getAccountBalance()) * APR * 4;
//                } else {
//                    Interest = (accounts.get(key).getAccountBalance()) * APR;
//                }
//                accounts.get(key).interestDeposit(Interest);
//                accounts.get(key).setMonth();
//            }
//            month-- ;
//        }
//    }



}