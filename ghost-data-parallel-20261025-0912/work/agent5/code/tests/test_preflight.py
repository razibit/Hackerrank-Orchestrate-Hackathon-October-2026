import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "tools"))

from preflight import build_parser


class PreflightArgumentsTests(unittest.TestCase):
    def test_explicit_dataset_path_is_respected(self):
        dataset = Path("external-dataset")
        self.assertEqual(build_parser().parse_args(["--dataset", str(dataset)]).dataset, dataset)


if __name__ == "__main__":
    unittest.main()
