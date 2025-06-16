import hashlib
from itertools import product

class ECCXOR:
    """
    Implements a simple parity-based error-correcting code for BB84 post-processing.
    Uses 3-bit chunks with 4 parity bits for a total of 7 bits per codeword.

    Attributes:
        codebook (dict): Maps valid 7-bit codewords to their original 3-bit data.
    """

    def __init__(self):
        """
        Initialize the error corrector and generate the codebook.
        """
        self.codebook = self._generate_codebook()

    def _generate_codebook(self):
        """
        Generate a mapping of all 3-bit input combinations to their 7-bit codewords.

        Returns:
            dict: Codebook with 7-bit tuples as keys and 3-bit lists as values.
        """
        codebook = {}
        for x1, x2, x3 in product([0, 1], repeat=3):
            data = [x1, x2, x3]
            codeword = [
                x1, x2, x3,
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]
            codebook[tuple(codeword)] = data
        return codebook

    def _hamming_distance(self, a, b):
        """
        Compute the Hamming distance between two binary vectors.

        Args:
            a (list): First binary list.
            b (list): Second binary list.

        Returns:
            int: Number of differing bits.
        """
        return sum(x != y for x, y in zip(a, b))

    def _decode_block(self, noisy_block):
        """
        Decode a 7-bit noisy block using minimum Hamming distance.

        Args:
            noisy_block (list): Received 7-bit codeword.

        Returns:
            list: Best-matching 3-bit decoded chunk.
        """
        min_dist = 8
        best = None
        for codeword, data in self.codebook.items():
            dist = self._hamming_distance(noisy_block, codeword)
            if dist < min_dist:
                min_dist = dist
                best = data
        return best

    def encode(self, bits):
        """
        Encode a binary message using 3-bit blocks expanded to 7-bit codewords.

        Args:
            bits (list): Binary input list (0s and 1s).

        Returns:
            list: Encoded binary list of 7-bit codewords.
        """
        encoded = []
        for i in range(0, len(bits), 3):
            chunk = bits[i:i+3]
            while len(chunk) < 3:
                chunk += [0]
            x1, x2, x3 = chunk
            encoded += [
                x1, x2, x3,
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]
        return encoded

    def correct(self, alice_bits, bob_bits):
        """
        Attempt to correct Bob's bits using parity reconstruction from Alice's bits.

        Args:
            alice_bits (list): Alice's reconciled key bits.
            bob_bits (list): Bob's reconciled key bits.

        Returns:
            list or None: Corrected key if the hash matches, else None.
        """
        length = (min(len(alice_bits), len(bob_bits)) // 3) * 3
        alice_bits = alice_bits[:length]
        bob_bits = bob_bits[:length]

        corrected = []
        for i in range(0, length, 3):
            a_block = alice_bits[i:i+3]
            b_block = bob_bits[i:i+3]
            if len(b_block) < 3:
                continue

            x1, x2, x3 = a_block
            received = [
                b_block[0], b_block[1], b_block[2],
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]

            decoded = self._decode_block(received)
            corrected += decoded

        ha = self.hash_bits(alice_bits)
        hb = self.hash_bits(corrected)

        if ha == hb:
            return corrected
        else:
            return None

    def hash_bits(self, bits):
        """
        Compute SHA-256 hash of a binary list.

        Args:
            bits (list): Binary list (0s and 1s).

        Returns:
            str: Hex digest of the hash.
        """
        return hashlib.sha256(''.join(map(str, bits)).encode()).hexdigest()
    
    def run(self, alice_key, bob_key):
        corrected = self.correct(alice_key, bob_key)
        print("\nECCXOR finished: checking key consistency via hash.")
        if corrected:
            print("ECCXOR attempt successful: all blocks corrected.")
            return "SUCCESS", corrected
        else:
            print("ECCXOR attempt failed: key mismatch detected.")
            return "FAILURE", None



