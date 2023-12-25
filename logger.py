import logging


logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
logging.getLogger().setLevel(logging.INFO)

class Logger:
    @staticmethod
    def raise_error(err_msg):
        logging.error(err_msg, exc_info=True)

    @staticmethod
    def log(msg):
        logging.info(msg)

