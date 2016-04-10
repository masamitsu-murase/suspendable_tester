
import suspendable_unittest
#import windows_suspender

import time


class SampleTest(suspendable_unittest.TestCase):
    def test_sample1(self):
        for x in range(2):
            start = time.time()
            self.shutdown()
            end = time.time()
            self.assertTrue(start + 1 < end, "start should be less than end")

    def test_sample2(self):
        start = time.time()
        self.shutdown()
        end = time.time()
        self.assertTrue(start + 1 < end, "start should be less than end")

if __name__ == "__main__":
    # suspendable_unittest.main(windows_suspender.Suspender())
    import unittest
    from suspendable_unittest import dummy_suspender
    suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
    suspendable_unittest.TestRunner().run(suite, dummy_suspender.Suspender())


