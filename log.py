import logging
import re
from logging.handlers import TimedRotatingFileHandler
import os

LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."), 'logs')

logger = logging.getLogger(__name__)

file_handler = TimedRotatingFileHandler(filename=f"{LOG_FILE}\\Mylog.log", when="MIDNIGHT", interval=1, backupCount=30)
file_handler.suffix = "%Y-%m-%d.log"
file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")

logging.basicConfig(format="%(levelname)s %(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[file_handler])

if __name__ == '__main__':
    logger.info("This is a info log")