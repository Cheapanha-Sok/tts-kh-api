from logging.config import dictConfig

def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "access": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stderr",
            },
            "app_file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": "/var/log/tts-kh-gateway/app.log",
            },
            "access_file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "access",
                "filename": "/var/log/tts-kh-gateway/access.log",
            },
        },

        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "access_file"],
                "propagate": False
            },
        },

        "root": {
            "level": "INFO",
            "handlers": ["console", "app_file"]
        },
    })
