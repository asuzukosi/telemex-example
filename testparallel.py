from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d : %H:%M:%S")

messages = [
    "SPEED", "RPM", "ACCELERATOR_POS_D",
    "ACCELERATOR_POS_E", "AMBIANT_AIR_TEMP", "BAROMETRIC_PRESSURE", "COOLANT_TEMP"
]

def print_message(message):
    print("the message: ", message)
    return "done"

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(print_message, message) for message in messages]
    
    # for future in as_completed(futures):
    #     try:
    #         result = future.result()
    #         print(result)
    #         logging.info("complete")
    #     except Exception as e:
    #         logging.error(f"failed with exception {e}")

            
        
    