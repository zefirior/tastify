import logging.config
import sys


def configure_logging():
    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'multiline_formatter': {
                    'format': '%(asctime)s [%(levelname)s] [%(name)s]: %(message)s',
                },
            },
            'handlers': {
                'console_handler': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'multiline_formatter',
                    'stream': sys.stdout,
                },
            },
            'root': {
                'handlers': ['console_handler'],
                'level': 'INFO',
            },
        }
    )
