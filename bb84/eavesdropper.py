import random
import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bases

class Eavesdropper:
    """
    Simulates an eavesdropper (Eve) in the BB84 protocol.
    Eve randomly chooses whether to intercept each qubit, performs a measurement in
    a random basis, and resends a newly encoded quantum state to the receiver.

    Attributes:
        intercept_fraction (float): Probability of intercepting a given qubit.
        intercepted_positions (set): Indices of intercepted qubits.
        bases (dict): Measurement bases used for each intercepted position.
        intercepted_bits (dict): Measured bit values at each intercepted position.
    """

    def __init__(self, intercept_fraction=1.0):
        """
        Initialize Eve with an interception probability.

        Args:
            intercept_fraction (float): Fraction of qubits Eve will attempt to intercept.
        """
        self.intercept_fraction = intercept_fraction
        self.intercepted_positions = set()
        self.bases = {}
        self.intercepted_bits = {}

    def should_intercept(self, position):
        """
        Randomly determine if Eve will intercept a qubit at a given index.

        Args:
            position (int): Index of the qubit in the transmission.

        Returns:
            bool: True if the qubit is intercepted, False otherwise.
        """
        if random.random() < self.intercept_fraction:
            self.intercepted_positions.add(position)
            return True
        return False

    def intercept(self, state, position=None):
        """
        Measure and re-encode a qubit after interception.

        Args:
            state (np.ndarray): Quantum state of the incoming qubit.
            position (int, optional): Index of the qubit in the transmission.

        Returns:
            np.ndarray: New quantum state encoded using Eve’s measurement result and basis.
        """
        basis = random.choice(bases)
        if position is not None:
            self.bases[position] = basis

        measured_bit = self.measure(state, basis)

        if position is not None:
            self.intercepted_bits[position] = measured_bit

        return self.encode(measured_bit, basis)

    def measure(self, state, basis):
        """
        Perform a simulated projective measurement in the given basis.

        Args:
            state (np.ndarray): Quantum state to measure.
            basis (str): Basis in which to measure ('+' or 'x').

        Returns:
            int: Measured classical bit (0 or 1).
        """
        if basis == 'x':
            return 0 if np.allclose(state, ket_plus) else 1
        elif basis == '+':
            return 0 if np.allclose(state, ket_0) else 1

    def encode(self, bit, basis):
        """
        Encode a classical bit into a quantum state using the specified basis.

        Args:
            bit (int): Bit value to encode (0 or 1).
            basis (str): Basis for encoding ('+' or 'x').

        Returns:
            np.ndarray: Corresponding quantum state.
        """
        if basis == 'x':
            return ket_plus if bit == 0 else ket_minus
        elif basis == '+':
            return ket_0 if bit == 0 else ket_1



