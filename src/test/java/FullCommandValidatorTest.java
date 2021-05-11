import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class FullCommandValidatorTest {

    FullCommandValidator fullCommandValidator;
    Bank bank;
    Account account;

    @BeforeEach
    void set_up(){
        bank = new Bank();
        fullCommandValidator = new FullCommandValidator(bank);
    }

    @Test
    void create_valid_checking_command(){
        String command = "Create Checking 12345678 1.2";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_valid_savings_command(){
        String command = "Create Savings 12345678 1.2";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_valid_cd_command(){
        String command = "create cd 12345678 0.5 1700.0";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_invalid_checking_command(){
        String command = "Create Checkings 12345678 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_invalid_savings_command(){
        String command = "Create Saving 123456789 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_invalid_cd_command(){
        String command = "Create CD 12345678 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_valid_deposit_command(){
        account = new SavingsAccount(12345678 ,1.2);
        bank.addAccount(12345678, account);
        String command = "Deposit 12345678 400";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_invalid_deposit_command(){
        account = new Account("Savings", 12345678, 1.2, 0.0);
        bank.addAccount(12345678, account);
        String command = "Deposit Savings 34243424 890";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));

    }



}
