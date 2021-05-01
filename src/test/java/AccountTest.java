import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class AccountTest {
    Account checkingAccount = new Account("Checking", 12345678, 1.2, 0.0);
    Account savingsAccount = new Account("Savings", 12345678, 1.2, 0.0);
    Account CDAccount = new Account("CD", 12345678, 1.2, 1500.0);

    @Test
    void check_checkingAccount() {
        assertTrue(checkingAccount.getAccountType() == "Checking");
        Account checkingAccount = new Account("Chckng", 12345678, 1.2, 0.0);
        assertFalse(checkingAccount.getAccountType() == "Checking");
    }

    @Test
    void check_savingsAccount() {
        assertTrue(savingsAccount.getAccountType() == "Savings");
        Account savingsAccount = new Account("Savng", 12345678, 1.2, 0.0);
        assertFalse(savingsAccount.getAccountType() == "Savings");
    }

    @Test
    void check_CDAccount() {
        assertTrue(CDAccount.getAccountType() == "CD");
        Account CDAccount = new Account("CeeDee", 12345678, 1.2, 1200.0);
        assertFalse(CDAccount.getAccountType() == "CD");
    }

    @Test
    void check_valid_accountID() {
        assertTrue(checkingAccount.setAccountID(12345678));
        assertTrue(savingsAccount.setAccountID(45678901));
        assertTrue(CDAccount.setAccountID(78901234));
    }

    @Test
    void check_invalid_accountID() {
        assertFalse(checkingAccount.setAccountID(123));
        assertFalse(savingsAccount.setAccountID(4567));
        assertFalse(CDAccount.setAccountID(78901));
    }

    @Test
    void check_valid_apr() {
        assertTrue(checkingAccount.setAccount_apr(1.8));
        assertTrue(savingsAccount.setAccount_apr(10.0));
        assertTrue(CDAccount.setAccount_apr(5.5));
    }

    @Test
    void check_invalid_apr() {
        assertFalse(checkingAccount.setAccount_apr(-1.0));
        assertFalse(savingsAccount.setAccount_apr(10.1));
        assertFalse(CDAccount.setAccount_apr(12.9));
    }


    @Test
    void check_checking_deposit() {
        checkingAccount.depositIntoAccount(500.0);
        assertEquals(500, checkingAccount.getAccountBalance());
        checkingAccount.depositIntoAccount(550.0);
        assertEquals(1050, checkingAccount.getAccountBalance());
    }

    @Test
    void check_savings_deposit() {
        savingsAccount.depositIntoAccount(250.0);
        assertEquals(250, savingsAccount.getAccountBalance());
        savingsAccount.depositIntoAccount(350.0);
        assertEquals(600, savingsAccount.getAccountBalance());
    }

    @Test
    void check_CD_deposit() {
        CDAccount.depositIntoAccount(100.0);
        assertEquals(1600.0, CDAccount.getAccountBalance());
        CDAccount.depositIntoAccount(700.0);
        assertEquals(2300.0, CDAccount.getAccountBalance());
    }

    @Test
    void check_checking_withdrawal() {
        checkingAccount.depositIntoAccount(500.0);
        checkingAccount.withdrawFromAccount(300.0);
        assertEquals(200, checkingAccount.getAccountBalance());
        checkingAccount.withdrawFromAccount(100.0);
        assertEquals(100, checkingAccount.getAccountBalance());
        checkingAccount.withdrawFromAccount(200.0);
        assertNotEquals(0.0, checkingAccount.getAccountBalance());

    }

    @Test
    void check_savings_withdrawal() {
        savingsAccount.depositIntoAccount(600.0);
        savingsAccount.withdrawFromAccount(100.0);
        assertEquals(500, savingsAccount.getAccountBalance());
        savingsAccount.withdrawFromAccount(100.0);
        assertEquals(400, savingsAccount.getAccountBalance());
        savingsAccount.withdrawFromAccount(500.0);
        assertNotEquals(0.0, savingsAccount.getAccountBalance());
    }

    @Test
    void check_CD_withdrawal() {
        CDAccount.withdrawFromAccount(1500.0);
        assertEquals(0.0, CDAccount.getAccountBalance());
    }


}

