import shutil
from unittest import TestCase

from source.IO.dataset_import.VDJDBLoader import VDJDBLoader
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.util.PathBuilder import PathBuilder


class TestVDJdbLoader(TestCase):
    def test_load(self):
        file_content = """complex.id	Gene	CDR3	V	J	Species	MHC A	MHC B	MHC class	Epitope	Epitope gene	Epitope species	Reference	Method	Meta	CDR3fix	Score
        3050	TRB	CASSPPRVYSNGAGLAGVGWRNEQFF	TRBV5-4*01	TRBJ2-1*01	HomoSapiens	HLA-A*11:01	B2M	MHCI	AVFDRKSDAK	EBNA4	EBV	https://www.10xgenomics.com/resources/application-notes/a-new-way-of-exploring-immunity-linking-highly-multiplexed-antigen-recognition-to-immune-repertoire-and-phenotype/#	{"frequency": "1/11684", "identification": "dextramer-sort", "sequencing": "rna-seq", "singlecell": "yes", "verification": ""}	{"cell.subset": "", "clone.id": "", "donor.MHC": "", "donor.MHC.method": "", "epitope.id": "", "replica.id": "", "samples.found": 1, "structure.id": "", "studies.found": 1, "study.id": "", "subject.cohort": "", "subject.id": "1", "tissue": ""}	{"cdr3": "CASSPPRVYSNGAGLAGVGWRNEQFF", "cdr3_old": "CASSPPRVYSNGAGLAGVGWRNEQFF", "fixNeeded": false, "good": true, "jCanonical": true, "jFixType": "NoFixNeeded", "jId": "TRBJ2-1*01", "jStart": 21, "vCanonical": true, "vEnd": 4, "vFixType": "NoFixNeeded", "vId": "TRBV5-4*01"}	0
        15760	TRB	CASSWTWDAATLWGQGALGGANVLTF	TRBV5-5*01	TRBJ2-6*01	HomoSapiens	HLA-A*03:01	B2M	MHCI	KLGGALQAK	IE1	CMV	https://www.10xgenomics.com/resources/application-notes/a-new-way-of-exploring-immunity-linking-highly-multiplexed-antigen-recognition-to-immune-repertoire-and-phenotype/#	{"frequency": "1/25584", "identification": "dextramer-sort", "sequencing": "rna-seq", "singlecell": "yes", "verification": ""}	{"cell.subset": "", "clone.id": "", "donor.MHC": "", "donor.MHC.method": "", "epitope.id": "", "replica.id": "", "samples.found": 1, "structure.id": "", "studies.found": 1, "study.id": "", "subject.cohort": "", "subject.id": "3", "tissue": ""}	{"cdr3": "CASSWTWDAATLWGQGALGGANVLTF", "cdr3_old": "CASSWTWDAATLWGQGALGGANVLTF", "fixNeeded": false, "good": true, "jCanonical": true, "jFixType": "NoFixNeeded", "jId": "TRBJ2-6*01", "jStart": 19, "vCanonical": true, "vEnd": 4, "vFixType": "NoFixNeeded", "vId": "TRBV5-5*01"}	0
        3050	TRA	CAAIYESRGSTLGRLYF	TRAV13-1*01	TRAJ18*01	HomoSapiens	HLA-A*11:01	B2M	MHCI	AVFDRKSDAK	EBNA4	EBV	https://www.10xgenomics.com/resources/application-notes/a-new-way-of-exploring-immunity-linking-highly-multiplexed-antigen-recognition-to-immune-repertoire-and-phenotype/#	{"frequency": "1/11684", "identification": "dextramer-sort", "sequencing": "rna-seq", "singlecell": "yes", "verification": ""}	{"cell.subset": "", "clone.id": "", "donor.MHC": "", "donor.MHC.method": "", "epitope.id": "", "replica.id": "", "samples.found": 1, "structure.id": "", "studies.found": 1, "study.id": "", "subject.cohort": "", "subject.id": "1", "tissue": ""}	{"cdr3": "CAAIYESRGSTLGRLYF", "cdr3_old": "CAAIYESRGSTLGRLYF", "fixNeeded": false, "good": true, "jCanonical": true, "jFixType": "NoFixNeeded", "jId": "TRAJ18*01", "jStart": 7, "oldVEnd": -1, "oldVFixType": "FailedBadSegment", "oldVId": null, "vCanonical": true, "vEnd": 3, "vFixType": "ChangeSegment", "vId": "TRAV13-1*01"}	0
        15760	TRA	CALRLNNQGGKLIF	TRAV9-2*01	TRAJ23*01	HomoSapiens	HLA-A*03:01	B2M	MHCI	KLGGALQAK	IE1	CMV	https://www.10xgenomics.com/resources/application-notes/a-new-way-of-exploring-immunity-linking-highly-multiplexed-antigen-recognition-to-immune-repertoire-and-phenotype/#	{"frequency": "1/25584", "identification": "dextramer-sort", "sequencing": "rna-seq", "singlecell": "yes", "verification": ""}	{"cell.subset": "", "clone.id": "", "donor.MHC": "", "donor.MHC.method": "", "epitope.id": "", "replica.id": "", "samples.found": 1, "structure.id": "", "studies.found": 1, "study.id": "", "subject.cohort": "", "subject.id": "3", "tissue": ""}	{"cdr3": "CALRLNNQGGKLIF", "cdr3_old": "CALRLNNQGGKLIF", "fixNeeded": false, "good": true, "jCanonical": true, "jFixType": "NoFixNeeded", "jId": "TRAJ23*01", "jStart": 6, "vCanonical": true, "vEnd": 3, "vFixType": "NoFixNeeded", "vId": "TRAV9-2*01"}	0
        """
        path = EnvironmentSettings.root_path + "test/tmp/iovdjdb/"
        PathBuilder.build(path)

        with open(path + "receptors.tsv", "w") as file:
            file.writelines(file_content)

        dataset = VDJDBLoader.load(path, {"result_path": path, "file_size": 1, "recursive": False, "paired": True})

        self.assertEqual(2, dataset.get_example_count())
        self.assertEqual(2, len(dataset.get_filenames()))

        for receptor in dataset.get_data(2):
            self.assertTrue(receptor.metadata["epitope_species"] in ["EBV", "CMV"])
            self.assertTrue(receptor.metadata["epitope"] in ["AVFDRKSDAK", "KLGGALQAK"])
            self.assertTrue(receptor.metadata["epitope_gene"] in ["EBNA4", "IE1"])

        shutil.rmtree(path)