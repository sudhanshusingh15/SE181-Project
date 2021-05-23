public class createProcessor extends Processor{
    public createProcessor(Bank bank){super(bank);}

    public Processor generateCreate(String[] Array){
        System.out.println("loda");
        if(Array[1].equals("checking")){
            System.out.println("lassan");
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
