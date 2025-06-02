import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bases, identity, hadamard

class QubitReceiver:
    """
    Simulates Bob’s side of the BB84 protocol.
    Bob receives and measures qubits, selects bases, and supports reconciliation
    and error rate estimation.

    Attributes:
        bases (list): Measurement bases chosen for each qubit.
        received_states (list): List of received quantum states.
        measured_bits (list): Measured classical bit outcomes.
        reconciled_key (list): Final key after reconciliation or correction.
        sample_indices (list): Indices used for error estimation.
    """

    def __init__(self):
        """
        Initialize an empty receiver ready to accept qubits.
        """
        self.bases = []
        self.received_states = []
        self.measured_bits = []
        self.reconciled_key = None
        self.sample_indices = []

    def receive_single_qubit(self, state, index):
        """
        Select a random basis, measure an incoming qubit, and store the result.

        Args:
            state (np.ndarray or None): Incoming quantum state (or None if lost).
            index (int): Index of the qubit in the sequence.
        """
        basis = np.random.choice(bases)
        self.bases.append(str(basis))
        self.received_states.append(state)

        if state is None:
            self.measured_bits.append(None)
            return

        # Rotate state into standard basis for measurment
        rotation = identity if basis == '+' else hadamard
        rotated = rotation @ state

        prob_0 = abs(rotated[0])**2
        prob_1 = abs(rotated[1])**2
        bit = np.random.choice([0, 1], p=[prob_0, prob_1])

        self.measured_bits.append(int(bit))

    def reconcile_with(self, alice_bases):
        """
        Extract bits where Alice's and Bob's bases match.

        Args:
            alice_bases (list): The basis choices used by Alice.

        Returns:
            np.ndarray: Bob's key bits from matched basis positions.
        """
        matching_indices = np.where(self.bases == alice_bases)[0]
        self.reconciled_key = [int(self.measured_bits[i]) for i in matching_indices]
        return self.reconciled_key

    def receive_sample_indices(self, indices):
        """
        Store the sample indices provided by Alice.

        Args:
            indices (list): Indices of key bits to compare for error estimation.
        """
        self.sample_indices = indices

    def compare_sample(self, bob_key, alice_key):
        """
        Compare Bob's and Alice's key bits at the sample indices.

        Args:
            bob_key (list): Bob's reconciled key bits.
            alice_key (list): Alice's reconciled key bits.

        Returns:
            float: Estimated error rate over the sample.
        """
        sample_a = [alice_key[i] for i in self.sample_indices]
        sample_b = [bob_key[i] for i in self.sample_indices]
        errors = sum(a != b for a, b in zip(sample_a, sample_b))
        return errors / len(self.sample_indices)

    def set_corrected_key(self, corrected_key):
        """
        Store a key after ECC correction.

        Args:
            corrected_key (list): The corrected key bits.
        """
        self.reconciled_key = corrected_key
