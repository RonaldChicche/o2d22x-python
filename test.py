import unittest
import numpy as np
from line_analizer import LineAnalyser


class TestLineAnalyser(unittest.TestCase):
    def test_run_analizer(self):
        ip_list = ["192.168.1.110"]
        analyser = LineAnalyser(ip_list)
        result = analyser.run_analizer()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for i in result:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i[0], dict)
            self.assertIsInstance(i[1], np.ndarray)


if __name__ == '__main__':
    unittest.main()