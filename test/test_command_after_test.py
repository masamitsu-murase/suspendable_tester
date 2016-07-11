
import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

class SampleTest(pausable_unittest.TestCase):
    def test_dummy(self):
        self.reboot()
        self.assertTrue(True)

def command_after_test(info):
    with open("command_after_test.txt", "w") as f:
        f.write("done")

if __name__ == "__main__":
    pausable_unittest.main(testpauser.Pauser(), command_after_test=command_after_test)

