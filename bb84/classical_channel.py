class ClassicalChannel:
    def __init__(self, alice, bob):
        self.alice = alice
        self.bob = bob
        self.shared_key = None
        self.error_rate = None
    
    def reconcile(self):
        alice_key = []
        bob_key = []
        for a_bit, a_base, b_base, b_bit in zip(self.alice.bits, self.alice.bases, self.bob.bases, self.bob.measured_bits):
            if a_base == b_base and b_bit is not None:
                alice_key.append(a_bit)
                bob_key.append(b_bit)
        self.bob_key = bob_key  # store for error rate calculation
        return alice_key

    def calculate_error_rate(self):
        self.error_rate = self.bob.error_rate(self.alice.bits, self.alice.bases)
        return self.error_rate

    def send_sample_indices(self, indices):
        self.bob.receive_sample_indices(indices)
