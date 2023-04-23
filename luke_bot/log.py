import logging
import sys


def initialise_logger():
    logger_ = logging.getLogger()
    logger_.setLevel(logging.DEBUG)
    logger_.addHandler(logging.StreamHandler(sys.stdout))
