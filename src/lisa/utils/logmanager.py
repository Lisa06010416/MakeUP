import logging
import datetime
import os


_default_level = logging.DEBUG
_default_formatter = logging.Formatter(
    '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    datefmt='%Y%m%d %H:%M:%S')
_default_logger_save_path = ""
_default_handler_list = ["stream", "file"]


def _set_log_save_path(filename, savepath="."):
    filename = datetime.datetime.now().strftime(filename)
    global _default_logger_save_path
    _default_logger_save_path = os.path.join(savepath,filename)


_set_log_save_path("%Y-%m-%d.log")


def _add_handler(logger):
    global _default_handler_list
    for handler_name in _default_handler_list:
        if "stream" in handler_name:
            handler = logging.StreamHandler()
        elif "file" in handler_name:
            handler = logging.FileHandler(_default_logger_save_path)
        else:
            assert 0, "_default_handler_list setting error, must be stream or file"
        handler.setLevel(_default_level)
        handler.setFormatter(_default_formatter)
        logger.addHandler(handler)
    return logger


def get_logger(name):
    logger = logging.getLogger(name)
    return _add_handler(logger)