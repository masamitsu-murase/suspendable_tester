
import logging

FORMAT = '[%(asctime)s] %(levelname)5s -- : %(message)s'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

class PicklableHandler(logging.Handler):
    def __init__(self, fmt=FORMAT, date_format=DATE_FORMAT):
        super(PicklableHandler, self).__init__()
        self.setFormatter(logging.Formatter(fmt, date_format))
        self.__log_list = []

    def destroyLock(self):
        self.lock = None

    def emit(self, record):
        self.__log_list.append(record)
        print(self.format(record))

    def print_all_logs(self):
        for record in self.__log_list:
            print(self.format(record))
