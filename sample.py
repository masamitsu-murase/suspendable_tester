
import unittest
import suspendable_runner
import suspendable_tester

class SampleTest(unittest.TestCase):
    def setUp(self):
        print("setUp")

    def run(self, result=None):
        print("run: result = %d" % id(result))
        self.runner = result.runner
        print("run: runner = %d" % id(result.runner))
        super(SampleTest, self).run(result)

    def test_sample1(self):
        for i in range(2):
            self.assertEqual("abc", "abcd")
            print("test_sample1: runner = %d" % id(self.runner))
            self.runner.suspend()
            print("test_sample1: runner = %d" % id(self.runner))
            self.assertEqual("abc", "abc")

    def test_sample2(self):
        print("test_sample2: runner = %d" % id(self.runner))
        self.runner.suspend()
        print("test_sample2: runner = %d" % id(self.runner))
        self.assertEqual("abc", "abc")

    def test_sample3(self):
        print("test_sample3: runner = %d" % id(self.runner))
        self.assertEqual("abc", "abc")

suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
suspendable_tester.Runner("C:/temp/hoge.bin").run(suite)

