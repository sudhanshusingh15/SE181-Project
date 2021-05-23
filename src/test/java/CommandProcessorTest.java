import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CommandProcessorTest {
    CommandProcessor commandProcessor;
    Bank bank;


    @BeforeEach
    void set_up(){
        bank = new Bank();
        commandProcessor = new CommandProcessor(bank);
    }

    @Test
    void valid_create_checking(){
        String command = "create checking 12345678 1.2";
        commandProcessor.createProcessor(command).execute(command);
        assertEquals(12345678, bank.getAccounts().get(12345678).getAccountID());
        assertEquals("Checking", bank.getAccounts().get(12345678).getAccountType());
    }
}
