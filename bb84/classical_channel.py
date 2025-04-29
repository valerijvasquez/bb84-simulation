class ClassicalChannel:
    def __init__(self, alice, bob):
        self.alice = alice
        self.bob = bob
        self.shared_key = None
        self.error_rate = None

    def reconcile(self):
        self.shared_key = self.bob.reconcile_with(self.alice.bases)
        return self.shared_key

    def calculate_error_rate(self):
        self.error_rate = self.bob.error_rate(self.alice.bits, self.alice.bases)
        return self.error_rate
