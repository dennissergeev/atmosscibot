"""A simple logging module."""
from datetime import datetime
import logging
import os

from settings import Settings


__all__ = ["logger"]


def set_logger(log_file, name=__name__):
    """Set up a logger."""
    logger = logging.getLogger(name)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    return logger


# Get current directory path
curdir = os.path.dirname(os.path.realpath(__file__))
# Read settings
s = Settings(os.path.join(curdir, "settings.ini"))
# Set up logging
log_dir = os.path.join(curdir, s.get_log_dirname())
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
tstamp = datetime.utcnow().strftime("%Y%m%d")
log_file = os.path.join(log_dir, s.get_log_filename().format(datetime=tstamp))
logger = set_logger(log_file, name=s.get_bot_name())
