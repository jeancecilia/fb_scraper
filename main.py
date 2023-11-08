from FGS import FGS
from FGSIO import FGSIO

def execute_scraper(input_data):

    username = 'winglin@tbnana.com'
    password = "E8MqJ.47HgFF4Fc"
    # username = 'joama@tbnana.com'
    # password = '@utomator786'

    print("Logging in facebook account of:", username)

    fgs = FGS(username,password, input_data)
    
    is_execution_successful = fgs.execute()

    while not is_execution_successful:
        
        execute_scraper(input_data)


if __name__ == "__main__":
    try:
        fgsio = FGSIO()
        fgsio.printBanner()
        input_data = fgsio.getInput()
        execute_scraper(input_data)
    except Exception as e:
        print("Error occurred:", e)
        







 


    