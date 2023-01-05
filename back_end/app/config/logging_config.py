from logging.config import dictConfig
from .app_config import Config
from flask import request, g
import logging


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if request and g:
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user_id = g.current_user.user_id
        elif request:
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user_id = None
        else:
            record.url = None
            record.remote_addr = None
            record.user_id = None

        return super().format(record)


logging_schema = {
    # Always 1. Schema versioning may be added in a future release of logging
    "version": 1,
    # "Name of formatter" : {Formatter Config Dict}
    "formatters": {
        # Formatter Name
        "standard": {
            # class is always "logging.Formatter"
            "()": lambda format: RequestFormatter(format),
            # Optional: logging output format
            "format": "[%(asctime)s] | %(levelname)s | %(user_id)s | %(module)s : %(message)s",
        }
    },
    # Handlers use the formatter names declared above
    "handlers": {
        # Name of handler
        "console": {
            # The class of logger. A mixture of logging.config.dictConfig() and
            # logger class-specific keyword arguments (kwargs) are passed in here. 
            "class": "logging.StreamHandler",
            # This is the formatter name declared above
            "formatter": "standard",
            "level": "INFO",
            # The default is stderr
            "stream": "ext://sys.stdout"
        },
        # Same as the StreamHandler example above, but with different
        # handler-specific kwargs.
        "file": {  
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "INFO",
            "filename": Config.LOG_FILE,
            "mode": "a",
            "encoding": "utf-8",
            "maxBytes": 500000,
            "backupCount": 4
        }
    },
    # Just a standalone kwarg for the root logger
    "root" : {
        "level": "INFO",
        "handlers": ["console","file"]
    }
}


logging_config = dictConfig(logging_schema)