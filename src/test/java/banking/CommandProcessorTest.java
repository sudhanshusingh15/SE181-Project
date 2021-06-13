package banking;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CommandProcessorTest {
    CommandProcessor commandProcessor;
    Bank bank;
    Account account;


    @BeforeEach
    void set_up() {
        bank = new Bank();
        commandProcessor = new CommandProcessor(bank);
    }

    @Test
    void valid_create_checking() {
        String command = "create checking 12345678 1.2";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Checking", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_create_savings() {
        String command = "create savings 12345678 1.2";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Savings", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_create_CD() {
        String command = "create cd 12345678 1.2 1500.00";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("CD", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void case_insensitive_create() {
        String command = "cReaTe SaVIngs 12345678 1.2";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Savings", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_multiple_account() {
        String command = "create checking 12345678 1.3";
        commandProcessor.Process(command).execute(command);
        String command2 = "create savings 11223344 1.9";
        commandProcessor.Process(command2).execute(command2);
        assertEquals("Checking", bank.getAccounts().get(12345678).getAccountType());
        assertEquals("Savings", bank.getAccounts().get(11223344).getAccountType());
    }

    @Test
    void valid_checking_deposit() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "deposit 12345678 750";
        commandProcessor.Process(command).execute(command);
        assertEquals(750.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_savings_deposit() {
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "deposit 12345678 1750";
        commandProcessor.Process(command).execute(command);
        assertEquals(1750.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void case_insensitive_deposit() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "dEpOSit 12345678 750";
        commandProcessor.Process(command).execute(command);
        assertEquals(750.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_multiple_deposit() {
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        account = new CheckingAccount(11223344, 1.3);
        bank.addAccount(11223344, account);
        String command = "deposit 12345678 1750";
        String command2 = "deposit 11223344 750";
        commandProcessor.Process(command).execute(command);
        commandProcessor.Process(command2).execute(command2);
        assertEquals(1750.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(750.00, bank.getAccounts().get(11223344).getAccountBalance());
    }

    //////////////////

    @Test
    void valid_checking_withdrawal() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 500.0);
        String command = "withdraw 12345678 250";
        commandProcessor.Process(command).execute(command);
        assertEquals(250.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_savings_withdrawal() {
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 1000.0);
        String command = "withdraw 12345678 700";
        commandProcessor.Process(command).execute(command);
        assertEquals(300.0, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void case_insensitive_withdrawal() {
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 1000.0);
        String command = "wIThDrAw 12345678 700";
        commandProcessor.Process(command).execute(command);
        assertEquals(300.0, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_multiple_withdrawal() {
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 750.0);
        account = new CheckingAccount(11223344, 1.3);
        bank.addAccount(11223344, account);
        bank.deposit(11223344, 450.0);
        String command = "withdraw 12345678 400";
        String command2 = "withdraw 11223344 100";
        commandProcessor.Process(command).execute(command);
        commandProcessor.Process(command2).execute(command2);
        assertEquals(350.0, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(350.00, bank.getAccounts().get(11223344).getAccountBalance());
    }

    @Test
    void valid_transfer() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 600.0);
        account = new SavingsAccount(11223344, 1.2);
        bank.addAccount(11223344, account);
        String command = "transfer 12345678 11223344 100";
        commandProcessor.Process(command).execute(command);
        assertEquals(500.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(100.00, bank.getAccounts().get(11223344).getAccountBalance());
    }

    @Test
    void case_insensitive_transfer() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 600.0);
        account = new SavingsAccount(11223344, 1.2);
        bank.addAccount(11223344, account);
        String command = "TRaNsfer 12345678 11223344 100";
        commandProcessor.Process(command).execute(command);
        assertEquals(500.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(100.00, bank.getAccounts().get(11223344).getAccountBalance());
    }

    @Test
    void valid_multiple_transfer() {
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        bank.deposit(12345678, 600.0);
        account = new SavingsAccount(11223344, 1.2);
        bank.addAccount(11223344, account);
        String command = "transfer 12345678 11223344 100";
        commandProcessor.Process(command).execute(command);
        assertEquals(500.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(100.00, bank.getAccounts().get(11223344).getAccountBalance());
        String command1 = "transfer 11223344 12345678 50";
        commandProcessor.Process(command).execute(command1);
        assertEquals(550.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(50.00, bank.getAccounts().get(11223344).getAccountBalance());

    }

    @Test
    void pass_apr(){
        account = new CheckingAccount(12345678, 1.2);
        account.setAccountBalance(5000.0);
        bank.addAccount(12345678,account);
        String command = "Pass 4";
        commandProcessor.Process(command).execute(command);
        assertEquals(5020.03, bank.getAccounts().get(12345678).floored_account_balance());

    }

    @Test
    void pass_deduction(){
        account = new CheckingAccount(12345678, 1.2);
        account.setAccountBalance(90.0);
        bank.addAccount(12345678,account);
        String command = "Pass 1";
        commandProcessor.Process(command).execute(command);
        assertEquals(65.07, bank.getAccounts().get(12345678).floored_account_balance());

    }

    @Test
    void pass_remove(){
        account = new CheckingAccount(12345678, 1.2);
        account.setAccountBalance(0.0);
        bank.addAccount(12345678,account);
        String command = "Pass 1";
        commandProcessor.Process(command).execute(command);
        assertEquals(null, bank.getAccounts().get(12345678));
    }



}





