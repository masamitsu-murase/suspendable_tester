
import suspendable_unittest
import suspendable_unittest.dummysuspender

import time


class SampleTest(suspendable_unittest.TestCase):
    def test_sample1(self):
        for x in range(2):
            start = time.time()
            self.reboot()
            end = time.time()
            self.assertTrue(start + 1 < end, "start should be less than end")

    def test_sample2(self):
        start = time.time()
        self.reboot()
        end = time.time()
        self.assertTrue(start + 1 < end, "start should be less than end")

if __name__ == "__main__":
    suspendable_unittest.main(suspendable_unittest.dummysuspender.Suspender())

