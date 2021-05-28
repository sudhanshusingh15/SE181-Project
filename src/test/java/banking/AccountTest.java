package banking;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;


public class AccountTest {
    CheckingAccount checkingAccount = new CheckingAccount(12345678, 1.2);
    SavingsAccount savingsAccount = new SavingsAccount(12345678, 1.2);
    CDAccount cdAccount = new CDAccount(12345678, 1.2, 1500.0);

    @Test
    void check_checkingAccount() {
        assertTrue(checkingAccount.getAccountType() == "Checking");
        assertFalse(checkingAccount.getAccountType() == "Savings");
    }

    @Test
    void check_savingsAccount() {
        assertTrue(savingsAccount.getAccountType() == "Savings");
        assertFalse(savingsAccount.getAccountType() == "CD");
    }

    @Test
    void check_CDAccount() {
        assertTrue(cdAccount.getAccountType() == "CD");
        assertFalse(cdAccount.getAccountType() == "Checking");
    }

    @Test
    void check_valid_accountID() {
        assertTrue(checkingAccount.setAccountID(12345678));
        assertTrue(savingsAccount.setAccountID(45678901));
        assertTrue(cdAccount.setAccountID(78901234));
    }

    @Test
    void check_invalid_accountID() {
        assertFalse(checkingAccount.setAccountID(123));
        assertFalse(savingsAccount.setAccountID(4567));
        assertFalse(cdAccount.setAccountID(78901));
    }

    @Test
    void check_valid_apr() {
        assertTrue(checkingAccount.setAccount_apr(1.8));
        assertTrue(savingsAccount.setAccount_apr(10.0));
        assertTrue(cdAccount.setAccount_apr(5.5));
    }

    @Test
    void check_invalid_apr() {
        assertFalse(checkingAccount.setAccount_apr(-1.0));
        assertFalse(savingsAccount.setAccount_apr(10.1));
        assertFalse(cdAccount.setAccount_apr(12.9));
    }


    @Test
    void check_checking_deposit() {
        checkingAccount.depositIntoAccount(500.0);
        assertEquals(500, checkingAccount.getAccountBalance());
    }

    @Test
    void check_checking_deposit_twice() {
        checkingAccount.depositIntoAccount(500.0);
        assertEquals(500, checkingAccount.getAccountBalance());
        checkingAccount.depositIntoAccount(550.0);
        assertEquals(1050, checkingAccount.getAccountBalance());
    }

    @Test
    void check_savings_deposit() {
        savingsAccount.depositIntoAccount(250.0);
        assertEquals(250, savingsAccount.getAccountBalance());
    }

    @Test
    void check_savings_deposit_twice() {
        savingsAccount.depositIntoAccount(250.0);
        assertEquals(250, savingsAccount.getAccountBalance());
        savingsAccount.depositIntoAccount(350.0);
        assertEquals(600, savingsAccount.getAccountBalance());
    }

    @Test
    void check_CD_deposit() {
        cdAccount.depositIntoAccount(700.0);
        assertEquals(2200.0, cdAccount.getAccountBalance());
    }

    @Test
    void check_CD_deposit_twice() {
        cdAccount.depositIntoAccount(100.0);
        assertEquals(1600.0, cdAccount.getAccountBalance());
        cdAccount.depositIntoAccount(700.0);
        assertEquals(2300.0, cdAccount.getAccountBalance());
    }

    @Test
    void check_checking_withdrawal() {
        checkingAccount.depositIntoAccount(500.0);
        checkingAccount.withdrawFromAccount(300.0);
        assertEquals(200, checkingAccount.getAccountBalance());
    }

    @Test
    void check_checking_withdrawal_more_than_once() {
        checkingAccount.depositIntoAccount(500.0);
        checkingAccount.withdrawFromAccount(300.0);
        assertEquals(200, checkingAccount.getAccountBalance());
        checkingAccount.withdrawFromAccount(100.0);
        assertEquals(100, checkingAccount.getAccountBalance());
        checkingAccount.withdrawFromAccount(200.0);
        assertEquals(0.0, checkingAccount.getAccountBalance());

    }


    @Test
    void check_savings_withdrawal() {
        savingsAccount.depositIntoAccount(600.0);
        savingsAccount.withdrawFromAccount(100.0);
        assertEquals(500, savingsAccount.getAccountBalance());
    }

    @Test
    void check_savings_withdrawal_more_than_once() {
        savingsAccount.depositIntoAccount(600.0);
        savingsAccount.withdrawFromAccount(100.0);
        assertEquals(500, savingsAccount.getAccountBalance());
        savingsAccount.withdrawFromAccount(100.0);
        assertEquals(400, savingsAccount.getAccountBalance());
        savingsAccount.withdrawFromAccount(500.0);
        assertEquals(0.0, savingsAccount.getAccountBalance());
    }

    @Test
    void check_CD_withdrawal() {
        cdAccount.withdrawFromAccount(1500.0);
        assertEquals(0.0, cdAccount.getAccountBalance());
    }


}

