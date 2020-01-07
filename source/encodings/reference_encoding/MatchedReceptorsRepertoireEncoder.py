import numpy as np
import pandas as pd

from source.analysis.SequenceMatcher import SequenceMatcher
from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.data_model.encoded_data.EncodedData import EncodedData
from source.data_model.repertoire.SequenceRepertoire import SequenceRepertoire
from source.encodings.EncoderParams import EncoderParams
from source.encodings.reference_encoding.MatchedReceptorsEncoder import MatchedReceptorsEncoder


class MatchedReceptorsRepertoireEncoder(MatchedReceptorsEncoder):

    def _encode_new_dataset(self, dataset, params: EncoderParams):
        encoded_dataset = RepertoireDataset(repertoires=dataset.repertoires, params=dataset.params,
                                            metadata_file=dataset.metadata_file)

        feature_annotations = self._get_feature_info()
        encoded_repertoires, labels, example_ids = self._encode_repertoires(dataset, params)

       # example_ids = [repertoire.identifier for repertoire in dataset.get_data()] if self.one_file_per_donor \
       #     else labels["donor"]

        encoded_dataset.add_encoded_data(EncodedData(
            # examples contains a np.ndarray with counts
            examples=encoded_repertoires,
            # example_ids contains a list of repertoire identifiers
            example_ids=example_ids,
            # feature_names contains a list of reference sequence identifiers
            feature_names=["{id}.{chain}".format(id=row['id'], chain=row['chain']) for index, row in feature_annotations.iterrows()],
            # feature_annotations contains a PD dataframe with sequence and VDJ gene usage per reference receptor
            feature_annotations=feature_annotations,
            labels=labels,
            encoding=MatchedReceptorsRepertoireEncoder.__name__
        ))

        self.store(encoded_dataset, params)
        return encoded_dataset

    def _get_feature_info(self):
        # returns a pandas dataframe containing:
        # - receptor id
        # - receptor chain
        # - amino acid sequence
        # - v gene
        # - j gene

        features = [[] for i in range(0, len(self.reference_sequences) * 2)]

        for i, receptor in enumerate(self.reference_sequences):
            id = receptor.identifier
            chains = receptor.get_chains()
            first_chain = receptor.get_chain(chains[0])
            second_chain = receptor.get_chain(chains[1])

            features[i * 2] = [id, chains[0], first_chain.amino_acid_sequence, first_chain.metadata.v_gene, first_chain.metadata.j_gene]
            features[i * 2 + 1] = [id, chains[1], second_chain.amino_acid_sequence, second_chain.metadata.v_gene, second_chain.metadata.j_gene]

        features = pd.DataFrame(features,
                                columns=['id', 'chain', 'sequence', 'v_gene', 'j_gene'])

        return features

    def _encode_repertoires(self, dataset: RepertoireDataset, params):
        # Rows = repertoires, Columns = reference chains (two per sequence receptor)
        encoded_repertories = np.zeros((dataset.get_example_count(),
                                        len(self.reference_sequences) * 2),
                                       dtype=int)
        labels = {label: [] for label in params["label_configuration"].get_labels_by_name()}

        for i, repertoire in enumerate(dataset.get_data()):
            encoded_repertories[i] = self._match_repertoire_to_receptors(repertoire)

            for label in params["label_configuration"].get_labels_by_name():
                labels[label].append(repertoire.metadata[label])

        example_ids = [repertoire.identifier for repertoire in dataset.get_data()]

        if self.one_file_per_donor:
            return encoded_repertories, labels, example_ids
        else:
            return self._collapse_encoding_per_donor(encoded_repertories, labels)

    def _match_repertoire_to_receptors(self, repertoire: SequenceRepertoire):
        matcher = SequenceMatcher()
        matches = np.zeros(len(self.reference_sequences) * 2, dtype=int)

        for i, ref_receptor in enumerate(self.reference_sequences):
            chains = ref_receptor.get_chains()
            first_chain = ref_receptor.get_chain(chains[0])
            second_chain = ref_receptor.get_chain(chains[1])

            for rep_seq in repertoire.sequences:
                # Match with first chain: add to even columns in matches.
                # Match with second chain: add to odd columns
                if matcher.matches_sequence(first_chain, rep_seq, 0):
                    matches[i * 2] += rep_seq.metadata.count
                if matcher.matches_sequence(second_chain, rep_seq, 0):
                    matches[i * 2 + 1] += rep_seq.metadata.count

        return matches

    def _collapse_encoding_per_donor(self, encoded_repertories, labels):
        if not "donor" in labels.keys():
            raise KeyError("When using the option one_file_per_donor = False, the label 'donor' must be specified in metadata")

        donor_ids = sorted(set(labels["donor"]))
        ids_to_idx = {id: idx for idx, id in enumerate(donor_ids)}

        encoded_donors = np.zeros((len(donor_ids), encoded_repertories.shape[1]),
                                       dtype=int)

        for repertoire_idx in range(0, encoded_repertories.shape[0]):
            donor_id = labels["donor"][repertoire_idx]
            encoded_donors[ids_to_idx[donor_id]] += encoded_repertories[repertoire_idx]

        # Only save the first occurrence of the label (it is assumed labels will be the same within donors)
        donor_labels = {key: [] for key in labels.keys()}
        for donor_id in donor_ids:
            first_occurrence = labels["donor"].index(donor_id)
            for key, value_list in labels.items():
                donor_labels[key].append(value_list[first_occurrence])

        example_ids = donor_labels.pop("donor")

        return encoded_donors, donor_labels, example_ids