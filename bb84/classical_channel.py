class ClassicalChannel:
    """
    Handles classical post-processing between Alice and Bob
    in the BB84 protocol, including key reconciliation and
    error rate estimation.

    Attributes:
        alice: Reference to the QubitSender (Alice).
        bob: Reference to the QubitReceiver (Bob).
        shared_key (list): The reconciled key from Alice's side.
        error_rate (float): The estimated bit error rate.
    """

    def __init__(self, alice, bob):
        """
        Initialize the classical channel.

        Args:
            alice: QubitSender object.
            bob: QubitReceiver object.
        """
        self.alice = alice
        self.bob = bob
        self.shared_key = None
        self.error_rate = None

    def reconcile_key(self):
        """
        Perform key reconciliation by comparing Alice's and Bob's bases.
        Keeps only bits where their bases match and Bob has a valid measurement.

        Returns:
            list: Alice's reconciled key bits.
        """
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
        """
        Estimate the bit error rate by comparing Bob's measurements to Alice's original bits.

        Returns:
            float: The estimated error rate.
        """
        self.error_rate = self.bob.error_rate(self.alice.bits, self.alice.bases)
        return self.error_rate

    def send_sample_indices_to_bob(self, indices):
        """
        Send Alice's selected sample indices to Bob for use in error estimation.

        Args:
            indices (list): Indices of the bits to use for error checking.
        """
        self.bob.receive_sample_indices(indices)


