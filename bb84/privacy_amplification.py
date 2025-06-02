import hashlib
import secrets

class PrivacyAmplifier:
    """
    Applies privacy amplification to reduce Eve's partial knowledge
    of the key using a seeded SHAKE-256 universal hash function.

    Attributes:
        output_bits (int): Number of output bits to extract.
        output_bytes (int): Number of output bytes (derived from output_bits).
        seed (bytes): Random 128-bit seed used for the hash function.
    """

    def __init__(self, output_bits: int = 40):
        """
        Initialize the privacy amplifier with a desired output length.

        Args:
            output_bits (int): Desired number of final bits after hashing.
        """
        self.output_bits = output_bits
        self.output_bytes = (output_bits + 7) // 8
        self.seed = secrets.token_bytes(16)

    def apply(self, key_bits: list) -> list:
        """
        Apply SHAKE-256 hashing with seed to compress and randomize the input key.

        Args:
            key_bits (list): List of bits (0s and 1s) from the reconciled key.

        Returns:
            list: Truncated and hashed output key as a list of bits.
        """
        key_bits = [int(b) for b in key_bits]

        # Pad key_bits to ensure its length is divisible by 8
        padded_len = ((len(key_bits) + 7) // 8) * 8
        padded_bits = key_bits + [0] * (padded_len - len(key_bits))

        # Convert padded bit list to a byte string
        bitstring = ''.join(str(b) for b in padded_bits)
        key_bytes = int(bitstring, 2).to_bytes(padded_len // 8, byteorder='big')

        # Apply SHAKE-256 hash with secret seed
        shake = hashlib.shake_256()
        shake.update(self.seed + key_bytes)
        digest = shake.digest(self.output_bytes)

        # Convert hash output to a list of bits
        digest_bits = ''.join(f"{byte:08b}" for byte in digest)
        return [int(bit) for bit in digest_bits[:self.output_bits]]
