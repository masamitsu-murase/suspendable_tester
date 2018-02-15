
import sys
import os.path
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.pardir))
sys.path.append(ROOT_DIR)

import pausable_unittest
import testpauser

import time
import logging

class SampleTest(pausable_unittest.TestCase):
    def test_reboot(self):
        start = time.time()
        self.reboot()
        end = time.time()
        margin = 3
        self.assertTrue(start + 0.75 < end, "start + 0.75 should be less than end.")
        self.assertTrue(start + 1 + margin > end, "start + 1 + margin should be more than end.")

    def test_chdir(self):
        dir1 = os.path.abspath(os.getcwd())
        self.reboot()
        dir2 = os.path.abspath(os.getcwd())
        # self.assertEqual(dir1, dir2)
        self.assertTrue(dir1 == dir2)  # Keep independency of the test code.

        os.chdir(os.path.pardir)
        dir3 = os.path.abspath(os.getcwd())
        self.reboot()
        dir4 = os.path.abspath(os.getcwd())
        # self.assertEqual(dir3, dir4)
        self.assertTrue(dir3 == dir4)  # Keep independency of the test code

        os.chdir(dir1)

    def test_version(self):
        self.assertIsInstance(pausable_unittest.__version__, str, "__version__ should be string")

    def test_options(self):
        self.assertEqual(self.assertion_log, self.options.get("test", False))

    def test_exec_for_reboot(self):
        for i in range(3):
            start = time.time()
            if sys.platform == "win32":
                self.exec_for_reboot("cmd /c echo test_exec_for_reboot %d" % i)
            else:
                self.exec_for_reboot("bash -c 'echo test_exec_for_reboot %d'" % i)
            end = time.time()
            margin = 3
            self.assertTrue(start + 0.75 < end, "start + 0.75 should be less than end." )
            self.assertTrue(start + 1 + margin > end, "start + 1 + margin should be more than end.")

    def test_assert_raises(self):
        num = 1
        with self.assertRaises(ZeroDivisionError, "msg") as cm:
            self.reboot()
            1 / (num - 1)
        self.assertEqual(type(cm.exception), ZeroDivisionError)
        self.assertRaises(ZeroDivisionError, lambda x: 1 / x, 0)

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "debug":
        pausable_unittest.main(testpauser.Pauser(), loglevel=logging.DEBUG,
                               assertion_log=True, options={"test": True})
    else:
        pausable_unittest.main(testpauser.Pauser())

