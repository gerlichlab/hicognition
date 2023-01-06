from logging.config import dictConfig

def create_logging_config(app_config):
    dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] | %(levelname)s | %(module)s : %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": app_config.ERROR_LOG_FILE,
                "maxBytes": 1_000_000_000,
                "backupCount": 10,
            },
            "app_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": app_config.LOG_FILE,
                "maxBytes": 1_000_000_000,
                "backupCount": 10,
            }
        },
        "loggers": {
            "gunicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "apscheduler": {
                "handlers": ["console", "app_log_file"],
                "level": "WARNING",
                "propagate": True
            },
            "numexpr": {
                "handlers": ["console", "error_file"],
                "level": "WARNING",
                "propagate": True
            },
            "app": {
                "level":  "DEBUG" if app_config.DEBUG else "INFO",
                "handlers": ["console", "app_log_file"],
                "propagate": False
            }
        },
        "root": {
            "level": "DEBUG" if app_config.DEBUG else "INFO",
            "handlers": ["console", "app_log_file"],
        }
    })