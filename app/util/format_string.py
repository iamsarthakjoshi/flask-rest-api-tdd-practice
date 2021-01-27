import logging, traceback

from config import error_levels as el


def format_error_log(at=None, message=None, data=None, level=logging.ERROR):
    return f" Error occured at {at}. \n\n Data: {data} \n\n Message: {message} \n\n Error Level: {el[level]} ({level}) \n\n {traceback.format_exc()}"
