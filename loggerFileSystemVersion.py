import logging

logging.basicConfig(
    filename="data/logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)  #production level code, instead of using print, we use logging to log info and error messages to a file. This way we can keep track of the execution history and any issues that arise without cluttering the console output.    

def log_error(message):
    logging.error(message)