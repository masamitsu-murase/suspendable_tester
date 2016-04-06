
import unittest
import suspendable_runner
import suspendable_tester

class SampleTest(suspendable_tester.TestCase):
    def setUp(self):
        print("setUp")

    def test_sample1(self):
        for i in range(2):
            self.assertEqual("abc", "abc")
            self.suspend()
            self.assertEqual("abc", "abc")

    def test_sample2(self):
        self.suspend()
        self.assertEqual("abc", "abc")

    def test_sample3(self):
        self.assertEqual("abc", "abc")

suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
suspendable_tester.Runner("C:/temp/hoge.bin").run(suite)

