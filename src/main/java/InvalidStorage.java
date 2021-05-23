import java.util.ArrayList;

public class InvalidStorage {
    Bank bank;

    public InvalidStorage(Bank bank){this.bank = bank;}

    ArrayList<String> invalid_commands_list = new ArrayList<>();

    public void addInvalidCommand(String command){
        invalid_commands_list.add(command);
    }

    public ArrayList<String> getInvalidCommands() {
        return invalid_commands_list;
    }
}

