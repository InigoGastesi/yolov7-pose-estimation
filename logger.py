import logging

def getLogger():
    # Create a logger
    logger = logging.getLogger('OI_LOGGER')
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    fh = logging.FileHandler('my_log.log')
    fh.setLevel(logging.DEBUG)

    # Create a stream handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

# Log some messages
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')