import java.util.List;

public class MasterControl {
    Bank bank;
    FullCommandValidator fullCommandValidator;
    CommandProcessor commandProcessor;
    InvalidStorage invalidStorage;

    public MasterControl(Bank bank, FullCommandValidator fullCommandValidator, CommandProcessor commandProcessor, InvalidStorage invalidStorage){
        this.bank = bank;
        this.fullCommandValidator = fullCommandValidator;
        this.commandProcessor = commandProcessor;
        this.invalidStorage = invalidStorage;

    }

//    public List<String> start(List<String> input) {
//        for(String command : input){
//            if(fullCommandValidator.Validator(command).check_if_valid(command)){
//                commandProcessor.execute(command);
//            } else {
//                invalidStorage.addInvalidCommand();
//            }
//        }
//        return invalidStorage.getInvalidCommands();
//    }
}
