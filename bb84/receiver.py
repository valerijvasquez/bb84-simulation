import numpy as np
from .globals import bases, identity, hadamard


class QubitReceiver:
    def __init__(self):
        self.bases = []
        self.received_states = []
        self.measured_bits = []
        self.reconciled_key = None
        self.sample_indices = []

    def receive_single_qubit(self, state, index):
        basis = np.random.choice(bases)
        self.bases.append(str(basis))
        self.received_states.append(state)

        if state is None:
            self.measured_bits.append(None)
            return

        rotation = identity if basis == '+' else hadamard
        rotated = rotation @ state

        prob_0 = abs(rotated[0])**2
        prob_1 = abs(rotated[1])**2
        bit = np.random.choice([0, 1], p=[prob_0, prob_1])

        self.measured_bits.append(int(bit))

    def reconcile_with(self, alice_bases):
        matching_indices = np.where(self.bases == alice_bases)[0]
        self.reconciled_key = [int(self.measured_bits[i]) for i in matching_indices]
        return self.reconciled_key

    def receive_sample_indices(self, indices):
        self.sample_indices = indices

    def compare_sample(self, bob_key, alice_key):
        sample_a = [alice_key[i] for i in self.sample_indices]
        sample_b = [bob_key[i] for i in self.sample_indices]
        errors = sum(a != b for a, b in zip(sample_a, sample_b))
        return errors / len(self.sample_indices)

    def set_corrected_key(self, corrected_key):
        self.reconciled_key = corrected_key
