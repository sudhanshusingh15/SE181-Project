import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CommandProcessorTest {
    CommandProcessor commandProcessor;
    Bank bank;
    Account account;


    @BeforeEach
    void set_up(){
        bank = new Bank();
        commandProcessor = new CommandProcessor(bank);
    }

    @Test
    void valid_create_checking(){
        String command = "create checking 12345678 1.2";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Checking", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_create_savings(){
        String command = "create savings 12345678 1.2";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Savings", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_create_CD(){
        String command = "create cd 12345678 1.2 1500.00";
        commandProcessor.Process(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("CD", bank.getAccounts().get(12345678).getAccountType());
    }

    @Test
    void valid_multiple_account(){
        String command = "create checking 12345678 1.3";
        commandProcessor.Process(command).execute(command);
        String command2 = "create savings 11223344 1.9";
        commandProcessor.Process(command2).execute(command2);
        assertEquals("Checking", bank.getAccounts().get(12345678).getAccountType());
        assertEquals("Savings", bank.getAccounts().get(11223344).getAccountType());
    }

    @Test
    void valid_checking_deposit(){
        account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "deposit 12345678 750.00";
        commandProcessor.Process(command).execute(command);
        assertEquals(750.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_savings_deposit(){
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "deposit 12345678 1750.00";
        commandProcessor.Process(command).execute(command);
        assertEquals(1750.00, bank.getAccounts().get(12345678).getAccountBalance());
    }

    @Test
    void valid_multiple_deposit(){
        account = new SavingsAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        account = new CheckingAccount(11223344,1.3);
        bank.addAccount(11223344, account);
        String command = "deposit 12345678 1750.00";
        String command2 = "deposit 11223344 750.00";
        commandProcessor.Process(command).execute(command);
        commandProcessor.Process(command2).execute(command2);
        assertEquals(1750.00, bank.getAccounts().get(12345678).getAccountBalance());
        assertEquals(750.00, bank.getAccounts().get(11223344).getAccountBalance());
    }



}
