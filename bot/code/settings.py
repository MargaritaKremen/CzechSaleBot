import logging
import os
from dotenv import load_dotenv

logging. basicConfig(format="%(levelname)s:%(message)s",
                     level=logging.WARNING)
load_dotenv()
try:
    BOTTOKEN = os.environ['BOTTOKEN']
except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message:{err}")
    raise KeyError(err)
