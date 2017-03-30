
import logging
import time
import os.path
import sys

FORMAT = '[%(asctime)s] %(levelname)5s -- : %(message)s'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

class PicklableHandler(logging.Handler):
    def __init__(self, fmt=FORMAT, date_format=DATE_FORMAT):
        super(PicklableHandler, self).__init__()
        self.setFormatter(logging.Formatter(fmt, date_format))

    def prepare_for_pause(self):
        self.lock = None

    def resume_from_pause(self):
        self.createLock()


class PicklableStreamHandler(PicklableHandler):
    MAX_LOG_COUNT = 1000

    def __init__(self, stream_type="stdout", fmt=FORMAT, date_format=DATE_FORMAT, max_log_count=MAX_LOG_COUNT):
        super(PicklableStreamHandler, self).__init__()
        self.__log_count = 0
        self.__max_log_count = max_log_count
        self.__log_list = []
        self.__stream_type = stream_type

    def emit(self, record):
        log = self.format(record)
        self.raw_writeln(log)

    def raw_writeln(self, text):
        if self.__max_log_count and self.__log_count >= self.__max_log_count:
            self.__log_list[self.__log_count % self.__max_log_count] = text
        else:
            self.__log_list.append(text)
        self.__log_count += 1
        if self.__stream_type == "stderr":
            sys.stderr.write(text + "\n")
        else:
            sys.stdout.write(text + "\n")

    def resume_from_pause(self):
        super(PicklableStreamHandler, self).resume_from_pause()
        self.print_all_logs()

    def print_all_logs(self):
        if self.__stream_type == "stderr":
            output = sys.stderr
        else:
            output = sys.stdout
        if self.__max_log_count and self.__log_count >= self.__max_log_count:
            output.write("...snip...\n")
            for i in range(self.__max_log_count):
                index = (self.__log_count - self.__max_log_count + i) % self.__max_log_count
                output.write(self.__log_list[index] + "\n")
        else:
            for log in self.__log_list:
                output.write(log + "\n")

class PicklableFileHandler(PicklableHandler):
    def __init__(self, filename=None, fmt=FORMAT, date_format=DATE_FORMAT):
        super(PicklableFileHandler, self).__init__()
        if filename is None:
            self.filename = os.path.abspath(time.strftime("log_%Y%m%d_%H%M%S.txt"))
        else:
            self.filename = os.path.abspath(filename)
        self.__file = None

    def open(self):
        if self.__file is None:
            self.__file = open(self.filename, "a")

    def close(self):
        if self.__file is not None:
            self.__file.close()
            self.__file = None

    def emit(self, record):
        log = self.format(record)
        self.raw_writeln(log)

    def raw_writeln(self, text):
        self.open()
        self.__file.write(text + "\n")

    def prepare_for_pause(self):
        super(PicklableFileHandler, self).prepare_for_pause()
        self.close()

