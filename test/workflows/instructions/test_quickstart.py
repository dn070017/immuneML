import os
import shutil
from glob import glob
from unittest import TestCase

from immuneML.environment.EnvironmentSettings import EnvironmentSettings
from immuneML.util.PathBuilder import PathBuilder
from immuneML.workflows.instructions.quickstart import Quickstart


class TestQuickstart(TestCase):
    def test(self):
        path = EnvironmentSettings.tmp_test_path / "quickstart/"
        PathBuilder.build(path)

        quickstart = Quickstart()
        quickstart.run(path)

        self.assertTrue(os.path.isfile(path / "quickstart/full_specs.yaml"))
        self.assertEqual(4, len(glob(str(path / "quickstart/inst1/split_1/**/test_predictions.csv"), recursive=True)))
        self.assertTrue(os.path.isfile(glob(str(path / "quickstart/inst1/split_1/**/test_predictions.csv"), recursive=True)[0]))

        shutil.rmtree(path, ignore_errors=True)
