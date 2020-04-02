import shutil
from unittest import TestCase

import pandas as pd

from source.IO.dataset_import.DatasetImportParams import DatasetImportParams
from source.IO.dataset_import.IRISImport import IRISImport
from source.data_model.dataset.ReceptorDataset import ReceptorDataset
from source.data_model.dataset.SequenceDataset import SequenceDataset
from source.data_model.receptor.TCABReceptor import TCABReceptor
from source.data_model.receptor.receptor_sequence.ReceptorSequence import ReceptorSequence
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.util.PathBuilder import PathBuilder


class TestIRISImport(TestCase):
    def _create_dummy_data(self, path, number_of_repertoires, add_metadata):

        for i in range(number_of_repertoires):
            with open(path + "receptors_{}.tsv".format(i+1), "w") as file:
                file.write(
"Cell type	Clonotype ID	Chain: TRA (1)	TRA - V gene (1)	TRA - D gene (1)	TRA - J gene (1)	Chain: TRA (2)	TRA - V gene (2)	TRA - D gene (2)	TRA - J gene (2)	Chain: TRB (1)	TRB - V gene (1)	TRB - D gene (1)	TRB - J gene (1)	Chain: TRB (2)	TRB - V gene (2)	TRB - D gene (2)	TRB - J gene (2)\n\
TCR_AB	181	ALPHA	TRAV4*01	null	TRAJ4*01	DUALALPHA	TRAV4*01	null	TRAJ4*01	BETA	TRBV4*01	null	TRBJ4*01	DUALBETA	TRBV4*01	null	TRBJ4*01\n\
TCR_AB	591	MULTIV	TRAV7-2*01 | TRAV12-3*02	null	TRAJ21*01	null	null	null	null	null	null	null	null	null	null	null	null\n\
TCR_AB	1051	VVNII	TRAV12-1*01 | TRAV12-1*02	null	TRAJ3*01 | TRAJ4*02	null	null	null	null	null	null	null	null	null	null	null	null\n\
TCR_AB	1341	LNKLT	TRAV2*01	null	TRAJ10*01	null	null	null	null	null	null	null	null	null	null	null	null\n\
TCR_AB	1411	AVLY	TRAV8-3*01	null	TRAJ18*01	null	null	null	null	null	null	null	null	null	null	null	null\n\
TCR_AB	1421	AT	TRAV12-3*01	null	TRAJ17*01	null	null	null	null	null	null	null	null	null	null	null	null")

        if add_metadata:
            metadata = {
                "filename": ["receptors_{}.tsv".format(i+1) for i in range(number_of_repertoires)],
                "label1": [i % 2 for i in range(number_of_repertoires)]
            }

            pd.DataFrame(metadata).to_csv(path + "metadata.csv")

    def test_load_repertoire_dataset_minimal(self):
        # loading with minimal data (no dual genes, no duplicate V/J segments)

        number_of_repertoires = 5

        path = EnvironmentSettings.tmp_test_path + "importseqsiris_mini/"
        PathBuilder.build(path)
        self._create_dummy_data(path, number_of_repertoires=number_of_repertoires, add_metadata=True)


        # case: minimal dataset (all dual chains and all genes = False)
        dataset = IRISImport.import_dataset(DatasetImportParams(result_path=path, metadata_file=path + "metadata.csv", path=path,
                                                                 column_mapping=None, misc = {"all_dual_chains": False,
                                                                                              "all_genes": False}))

        self.assertEqual(number_of_repertoires, dataset.get_example_count())
        self.assertEqual(number_of_repertoires, len(dataset.get_data()))

        for repertoire in dataset.get_data(2):
            self.assertTrue(repertoire.metadata["label1"] in {0, 1})
            self.assertEqual(7, len(repertoire.sequences)) # 6 alpha + 1 beta
            self.assertEqual(1, len(repertoire.receptors)) # 1 alpha/beta pair (dual chain (1))

        shutil.rmtree(path)

    def test_load_repertoire_dataset_maximal(self):
        # loading with maximal data (all dual genes, all duplicate V/J segments)

        number_of_repertoires = 5

        path = EnvironmentSettings.tmp_test_path + "importseqsiris_maxi/"
        PathBuilder.build(path)
        self._create_dummy_data(path, number_of_repertoires=number_of_repertoires, add_metadata=True)

        dataset = IRISImport.import_dataset(DatasetImportParams(result_path=path, metadata_file=path + "metadata.csv", path=path,
                                                                column_mapping=None, misc={"all_dual_chains": True,
                                                                                           "all_genes": True}))

        self.assertEqual(number_of_repertoires, dataset.get_example_count())
        self.assertEqual(number_of_repertoires, len(dataset.get_data()))

        for repertoire in dataset.get_data(2):
            self.assertTrue(repertoire.metadata["label1"] in {0, 1})
            self.assertEqual(11, len(repertoire.sequences)) # 4 (dual a/b) + 2 (multi V) + 2 (multi J, not V) + 3
            self.assertEqual(4, len(repertoire.receptors)) # 4 combinations of dual a/b


        shutil.rmtree(path)

    def test_load_sequence_dataset_unpaired(self):
        path = EnvironmentSettings.tmp_test_path + "importseqsiris_sequencedataset/"
        PathBuilder.build(path)
        self._create_dummy_data(path, number_of_repertoires=1, add_metadata=False)



        sequence_dataset = IRISImport.import_dataset(DatasetImportParams(result_path=path, path=path,
                                                                column_mapping=None, misc={"all_dual_chains": True,
                                                                                           "all_genes": True},
                                                                file_size=1000, paired=False))

        self.assertIsInstance(sequence_dataset, SequenceDataset)

        for seq in sequence_dataset.get_data():
            self.assertIsInstance(seq, ReceptorSequence)

        self.assertEqual(len(list(sequence_dataset.get_data())), 11)

        shutil.rmtree(path)

    def test_load_sequence_dataset_paired(self):
        path = EnvironmentSettings.tmp_test_path + "importseqsiris_sequencedataset/"
        PathBuilder.build(path)
        self._create_dummy_data(path, number_of_repertoires=1, add_metadata=False)

        receptor_dataset = IRISImport.import_dataset(DatasetImportParams(result_path=path, path=path,
                                                                column_mapping=None, misc={"all_dual_chains": True,
                                                                                           "all_genes": True},
                                                                file_size=1000, paired=True))

        self.assertIsInstance(receptor_dataset, ReceptorDataset)

        for rec in receptor_dataset.get_data():
            self.assertIsInstance(rec, TCABReceptor)

        self.assertEqual(len(list(receptor_dataset.get_data())), 4)


        shutil.rmtree(path)

