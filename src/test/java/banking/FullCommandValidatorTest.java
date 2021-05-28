package banking;

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
    void valid_create_checking_command(){
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
        String command = "Create Savings 123456789 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void create_invalid_cd_command(){
        String command = "Create CD 12345678 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void duplicate_id_exists(){
        Account account = new CheckingAccount(12345678, 1.2);
        bank.addAccount(12345678, account);
        String command = "Create Savings 12345678 1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void invalid_apr(){
        String command = "Create Checking 12345678 [1.6]";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void invalid_cd_amount(){
        String command = "Create CD 12345678 1.2 100000";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void negative_cd_amount(){
        String command = "Create CD 1234578 1.2 -1000";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void negative_apr(){
        String command = "Create Checking -1.2";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void case_insensitive_create(){
        String command = "CrEAte ChEckIng 12345678 1.2";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }


    /////////////DEPOSIT TESTS////////////////

    @Test
    void valid_deposit_command(){
        account = new SavingsAccount(12345678 ,1.2);
        bank.addAccount(12345678, account);
        String command = "Deposit 12345678 400";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void invalid_deposit_command(){
        account = new Account("Savings", 12345678, 1.2, 0.0);
        bank.addAccount(12345678, account);
        String command = "Deposit Savings 34243424 890";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void deposit_amount_too_high(){
        account = new Account("Savings", 12345678, 1.2, 0.0);
        bank.addAccount(12345678, account);
        String command = "Deposit Savings 12345678 100000";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void deposit_amount_negative(){
        account = new Account("Savings", 12345678, 1.2, 0.0);
        bank.addAccount(12345678, account);
        String command = "Deposit Savings 12345678 -1000";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void invalid_deposit_amount(){
        account = new Account("Checking", 12345678, 1.2, 0.0);
        bank.addAccount(12345678, account);
        String command = "Deposit Checking 12345678 [1000]";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void cant_deposit_into_CD_account(){
        account = new Account("CD", 12345678, 1.2, 5000.0);
        bank.addAccount(12345678, account);
        String command = "Deposit CD 12345678 1000";
        assertFalse(fullCommandValidator.Validator(command).check_if_valid(command));
    }

    @Test
    void case_insensitive_deposit(){
        account = new SavingsAccount(12345678 ,1.2);
        bank.addAccount(12345678, account);
        String command = "DePOsIt 12345678 400";
        assertTrue(fullCommandValidator.Validator(command).check_if_valid(command));
    }

}
