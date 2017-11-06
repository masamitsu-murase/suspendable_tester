
import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser
import logging

class NullHandler(logging.Handler):
    """A Handler that does nothing."""
    def emit(self, record):
        pass

# logger shares Logger.manager, so it prevents pickle.
logger = logging.getLogger("another_log")
logger.addHandler(NullHandler())

class SampleTest(pausable_unittest.TestCase):
    def test_dummy(self):
        self.reboot()
        self.assertTrue(True)

def command_after_test(info):
    results = info["result"].results
    if len(results)==1 and results[0][0] == "success":
        with open("command_after_test.txt", "w") as f:
            f.write("done")

if __name__ == "__main__":
    pausable_unittest.main(testpauser.Pauser(), command_after_test=command_after_test)

