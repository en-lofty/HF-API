import logging
import os
from datetime import datetime

if not os.path.exists("logs/"):
    os.mkdir("logs/")

logging.basicConfig(filename='logs/app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
logger = logging.getLogger(__name__)


def log(message: str, *args):
    for arg in args:
        message += " " + str(arg)
    formatted_message = "[{}] {}".format(datetime.now().strftime('%c'), message)
    # print(formatted_message)
    logger.debug(formatted_message)
    print(formatted_message)


def exception(e: Exception, quit_program=False):
    logger.exception(e)
    if quit_program:
        log("Error thrown, exiting. Please refer to app.log.")
        exit(1)
    else:
        log("Error thrown. Please refer to app.log.")
