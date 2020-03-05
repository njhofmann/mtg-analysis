import logging
import psycopg2

"""Module providing common functions for logging and psycopg2 exception handling across whole of the project"""

# psycopg2 constants
PSYCOPG2_UNIQUE_VIOLATION_CODE = 23505


def init_logging(log_file):
    """
    Initializes a logger set to lowest informative level (info) for printing message to console and a logging file.
    :param: log_file: name of log file to create
    :return: logger that can write to stream and a log file
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def init_channel(channel):
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        channel.setFormatter(formatter)
        logger.addHandler(channel)

    init_channel(logging.StreamHandler())
    init_channel(logging.FileHandler(log_file, mode='w', encoding='utf-8'))
    return logger


def execute_query_pass_on_unique_violation(query_func, logger, warning_msg):
    """
    Wrapper function to execute around SQL insert queries functions being handled with psycopg2. If insert query would
    insert a entry with a primary key or unique key already in the database, catches the error psycopg2 would throw
    instead logging the duplicate insertion attempt withe given logger and warning message at level of warning.
    :param query_func: function to execute the inserts some data into a database with psycopg2
    :param logger: logger to log given warning message to in case of unique violation error
    :param warning_msg: warning message to log if unique ivolation error is caught, specific to given query function
    :return: None
    """
    try:
        query_func()
    except psycopg2.IntegrityError as e:
        if e.pgcode != PSYCOPG2_UNIQUE_VIOLATION_CODE:
            logger.warning(str(e))
            logger.warning(warning_msg)
        else:
            raise e
