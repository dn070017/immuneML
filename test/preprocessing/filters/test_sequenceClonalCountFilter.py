import shutil
from unittest import TestCase

from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.preprocessing.filters.SequenceClonalCountFilter import SequenceClonalCountFilter
from source.util.PathBuilder import PathBuilder
from source.util.RepertoireBuilder import RepertoireBuilder


class TestSequenceClonalCountFilter(TestCase):
    def test_process(self):
        path = EnvironmentSettings.root_path + "test/tmp/sequenceclonalcountfilter/"
        PathBuilder.build(path)
        dataset = RepertoireDataset(repertoires=RepertoireBuilder.build([["ACF", "ACF", "ACF"],
                                                                         ["ACF", "ACF"],
                                                                         ["ACF", "ACF", "ACF", "ACF"]], path,
                                                                        seq_metadata=[[{"count": 1}, {"count": 2}, {"count": 3}],
                                                                                      [{"count": 4}, {"count": 1}],
                                                                                      [{"count": 5}, {"count": 6}, {"count": None},
                                                                                       {"count": 1}]])[0])

        dataset1 = SequenceClonalCountFilter.process(dataset, {"low_count_limit": 2, "remove_without_count": True,
                                                               "result_path": path, "batch_size": 4})
        self.assertEqual(2, dataset1.repertoires[0].get_sequence_aas().shape[0])

        dataset2 = SequenceClonalCountFilter.process(dataset, {"low_count_limit": 5, "remove_without_count": True,
                                                               "result_path": path, "batch_size": 4})
        self.assertEqual(0, dataset2.repertoires[0].get_sequence_aas().shape[0])

        dataset3 = SequenceClonalCountFilter.process(dataset, {"low_count_limit": 0, "remove_without_count": True,
                                                               "result_path": path, "batch_size": 4})
        self.assertEqual(3, dataset3.repertoires[2].get_sequence_aas().shape[0])

        dataset = RepertoireDataset(repertoires=RepertoireBuilder.build([["ACF", "ACF", "ACF"],
                                                                         ["ACF", "ACF"],
                                                                         ["ACF", "ACF", "ACF", "ACF"]], path)[0])

        dataset4 = SequenceClonalCountFilter.process(dataset, {"low_count_limit": 0, "remove_without_count": True,
                                                               "result_path": path, "batch_size": 4})
        self.assertEqual(0, dataset4.repertoires[0].get_sequence_aas().shape[0])
        self.assertEqual(0, dataset4.repertoires[1].get_sequence_aas().shape[0])
        self.assertEqual(0, dataset4.repertoires[2].get_sequence_aas().shape[0])

        shutil.rmtree(path)