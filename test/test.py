
import sys
import os.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.basename(sys.argv[0]), os.pardir, os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

import time


class SampleTest(pausable_unittest.TestCase):
    def test_reboot(self):
        start = time.time()
        self.reboot()
        end = time.time()
        margin = 0.5
        self.assertTrue(start + 1 - margin < end, "%f + 2 - %f should be less than %f." % (start, margin, end))
        self.assertTrue(start + 1 + margin > end, "%f + 2 + %f should be more than %f." % (start, margin, end))

    def test_exec_for_reboot(self):
        for i in range(3):
            start = time.time()
            self.exec_for_reboot("echo exec_for_reboot: %d" % i)
            end = time.time()
            margin = 0.5
            self.assertTrue(start + 1 - margin < end, "%f + 2 - %f should be less than %f." % (start, margin, end))
            self.assertTrue(start + 1 + margin > end, "%f + 2 + %f should be more than %f." % (start, margin, end))

if __name__ == "__main__":
    pausable_unittest.main(testpauser.Pauser())


