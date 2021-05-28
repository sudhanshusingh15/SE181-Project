public class createProcessor extends Processor{
    public createProcessor(Bank bank){super(bank);}

    public Processor createAccountProcessor(String[] Array){
        if(Array[1].equals("checking")){
            return new checkingProcessor(bank);
        }
        else if(Array[1].equals("savings")){
            return new savingsProcessor(bank);
        }
        else{
            return new CDProcessor(bank);
        }
    }
}
