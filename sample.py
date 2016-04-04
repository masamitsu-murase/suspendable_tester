
import unittest
import suspendable_runner

class SampleTest(unittest.TestCase):
    def test_sample(self):
        self.assertEqual("abc", "abc")

suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
suspendable_runner.SuspendableTestRunner().run(suite)

