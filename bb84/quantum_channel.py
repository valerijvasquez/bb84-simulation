import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus

class QuantumChannel:
    def __init__(self, flip_probability=0.0, loss_probability=0.0, eavesdropper=None):
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.eavesdropper = eavesdropper
        self.loss_count = 0
        self.flip_count = 0

    def transmit(self, state, position):
    
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

