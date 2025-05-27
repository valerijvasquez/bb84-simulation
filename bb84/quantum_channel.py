import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus

class QuantumChannel:
    """
    Models a quantum channel that can introduce qubit loss, bit flip noise,
    and optional eavesdropping during transmission.
    
    Attributes:
        flip_probability (float): Probability that a transmitted qubit is flipped.
        loss_probability (float): Probability that a qubit is lost during transmission.
        eavesdropper (Eavesdropper or None): Eve instance to optionally intercept qubits.
        loss_count (int): Number of qubits lost so far.
        flip_count (int): Number of qubits flipped so far.
    """

    def __init__(self, flip_probability=0.0, loss_probability=0.0, eavesdropper=None):
        """
        Initialize the quantum channel.

        Args:
            flip_probability (float): Probability of a bit flip during transmission.
            loss_probability (float): Probability of qubit loss during transmission.
            eavesdropper (Eavesdropper, optional): Eve instance to intercept qubits.
        """
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.eavesdropper = eavesdropper
        self.loss_count = 0
        self.flip_count = 0

    def transmit(self, state, position):
        """
        Simulate transmission of a qubit through the quantum channel.

        Args:
            state (np.ndarray): The qubit state to be transmitted.
            position (int): Index of the qubit in the sequence.

        Returns:
            np.ndarray or None: The resulting qubit state, or None if lost.
        """
        if np.random.rand() < self.loss_probability:
            self.loss_count += 1
            return None

        if self.eavesdropper and self.eavesdropper.should_intercept(position):
            state = self.eavesdropper.intercept(state, position)

        if np.random.rand() < self.flip_probability:
            self.flip_count += 1
            if np.allclose(state, ket_0):
                state = ket_1
            elif np.allclose(state, ket_1):
                state = ket_0
            elif np.allclose(state, ket_plus):
                state = ket_minus
            elif np.allclose(state, ket_minus):
                state = ket_plus

        return state

