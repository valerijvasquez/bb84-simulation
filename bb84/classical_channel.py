class ClassicalChannel:
    def __init__(self, alice, bob):
        self.alice = alice
        self.bob = bob
        self.shared_key = None
        self.error_rate = None

    def reconcile_key(self):
        alice_key = []
        bob_key = []

        for a_bit, a_base, b_base, b_bit in zip(
            self.alice.bits, self.alice.bases, self.bob.bases, self.bob.measured_bits
        ):
            if a_base == b_base and b_bit is not None:
                alice_key.append(int(a_bit))
                bob_key.append(int(b_bit))

        self.bob_key = bob_key
        self.alice.reconciled_key = alice_key
        self.bob.reconciled_key = bob_key

        return alice_key

    def estimate_error_rate(self):
        self.error_rate = self.bob.error_rate(self.alice.bits, self.alice.bases)
        return self.error_rate

    def send_sample_indices_to_bob(self, indices):
        self.bob.receive_sample_indices(indices)
