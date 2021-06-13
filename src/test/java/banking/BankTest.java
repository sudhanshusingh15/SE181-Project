package banking;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class BankTest {

    private Account account;
    private Bank bank;
    private Integer ID = 12345678;

    @BeforeEach
    void set_up() {
        account = new Account("Savings", ID, 1.2, 0.0,0);
        bank = new Bank();
    }


    @Test
    void bank_empty() {
        assertTrue(bank.getAccounts().isEmpty());
    }

    @Test
    void add_account_into_bank() {
        bank.addAccount(ID, account);
        assertEquals(ID, bank.getAccounts().get(ID).getAccountID());
    }

    @Test
    void deposit_amount_from_bank() {
        bank.addAccount(ID, account);
        bank.deposit(ID, 1000.0);
        assertEquals(1000, bank.getAccounts().get(ID).getAccountBalance());
    }

    @Test
    void withdraw_amount_from_bank() {
        bank.addAccount(ID, account);
        bank.deposit(ID, 1000.0);
        bank.withdraw(ID, 700.0);
        assertEquals(300, bank.getAccounts().get(ID).getAccountBalance());
    }


}
