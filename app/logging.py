import logging

from .enums import WorkflowEnum


LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevels(WorkflowEnum):
    info = "info"
    warn = "warn"
    error = "error"
    debug = "debug"

def configure_logging(): 
    log_level = str(LOG_LEVEL).upper()
    log_levels = list(LogLevels)

    if log_level not in log_levels: 
        return None
    
    logging.basicConfig()

    logging.getLogger().setLevel()



