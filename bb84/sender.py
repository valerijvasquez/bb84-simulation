import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bits, bases

class QubitSender:
    """
    Simulates Alice’s role in the BB84 protocol.
    Generates a random bit string and basis sequence, and prepares qubits for transmission.

    Attributes:
        key_length (int): Number of qubits to prepare.
        bits (np.ndarray): Randomly chosen bit values (0 or 1).
        bases (np.ndarray): Randomly chosen bases ('+' or 'x') for encoding.
        sample_indices (list): Indices of the key selected for error rate sampling.
        reconciled_key (list): Final key after reconciliation.
    """

    def __init__(self, key_length):
        """
        Initialize the sender with a given key length.

        Args:
            key_length (int): Number of qubits to send.
        """
        self.key_length = key_length
        self.bits = None
        self.bases = None
        self.sample_indices = []
        self.reconciled_key = None

    def prepare_qubits(self):
        """
        Randomly generate the bit string and basis sequence.
        """
        self.bits = np.random.choice(bits, self.key_length)
        self.bases = np.random.choice(bases, self.key_length)

    def encode_single_qubit(self, index):
        """
        Encode a single bit as a quantum state in the chosen basis.

        Args:
            index (int): Index of the bit/basis to encode.

        Returns:
            np.ndarray: Corresponding quantum state.
        """
        bit = self.bits[index]
        basis = self.bases[index]
        if basis == '+':
            return ket_0 if bit == 0 else ket_1
        elif basis == 'x':
            return ket_plus if bit == 0 else ket_minus

    def choose_sample_indices(self, key_length, fraction=0.2):
        """
        Select a random subset of indices to use for error estimation.

        Args:
            key_length (int): Length of the reconciled key.
            fraction (float): Fraction of key to sample (default is 0.2).

        Returns:
            list: Sorted list of selected sample indices.
        """
        indices = sorted(np.random.choice(key_length, int(fraction * key_length), replace=False))
        self.sample_indices = indices
        return indices
