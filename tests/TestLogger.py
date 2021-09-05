# -------------------------------------------------------------------------------------------------
# A standard approach to the logging of activities, including how the requests modules should work.
# We log to both a rotating file and the screen, and you can set different logging options for both.
# -------------------------------------------------------------------------------------------------

import logging
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    def __init__(self, name, std_level=logging.DEBUG, file_level=logging.INFO):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("suds").setLevel(logging.WARNING)
        logging.getLogger("azure").setLevel(logging.WARNING)

        file_handler = TimedRotatingFileHandler(
            '%s.log' % name, when='midnight', backupCount=30
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)

        screen_handler = logging.StreamHandler()
        screen_handler.setFormatter(formatter)
        screen_handler.setLevel(std_level)
        logger.addHandler(screen_handler)
        self.logging = logging

    def debug(self, message):
        self.logging.debug(message)

    def ui_debug(self, message):
        self.logging.debug(message)

    def info(self, message):
        self.logging.info(message)

    def warn(self, message):
        self.logging.warning(message)

    def error(self, message):
        self.logging.error(message)
