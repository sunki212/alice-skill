import json
import logging
import traceback as tb
from pythonjsonlogger import jsonlogger
import aliceskill as game

class YcLoggingFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(YcLoggingFormatter, self).add_fields(log_record, record, message_dict)
        log_record["logger"] = record.name
        log_record["level"] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")

def configure_logger():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(YcLoggingFormatter('%(levelname)s: %(message)s'))
    logger.propagate = False
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

def handler(event, context):
    response = game.handler(event)
    return response

configure_logger()
logging.info("Инициализации Яндекс-функции")