class OneTimePad:
    """
    Provides one-time pad encryption and decryption
    using a binary key derived from BB84 key bits.

    Attributes:
        key (bytes): Byte representation of the binary key bits.
    """

    def __init__(self, key_bits):
        """
        Initialize the OneTimePad with key bits.

        Args:
            key_bits (list): List of 0s and 1s representing the final key.
        """
        self.key = self._bits_to_bytes(key_bits)

    def _bits_to_bytes(self, key_bits):
        """
        Convert a list of bits into a bytes object.

        Args:
            key_bits (list): List of bits (0s and 1s).

        Returns:
            bytes: Corresponding bytes object.
        """
        byte_chunks = [key_bits[i:i + 8] for i in range(0, len(key_bits), 8)]
        return bytes([
            int(''.join(str(bit) for bit in chunk), 2)
            for chunk in byte_chunks
        ])

    def encrypt(self, plaintext):
        """
        Encrypt a plaintext message using the one-time pad.

        Args:
            plaintext (str): The input message.

        Returns:
            bytes or None: Encrypted bytes, or None if key is too short.
        """
        message_bytes = plaintext.encode('utf-8')
        if len(self.key) < len(message_bytes):
            return None
        return bytes([m ^ k for m, k in zip(message_bytes, self.key)])

    def decrypt(self, ciphertext):
        """
        Decrypt a one-time pad ciphertext.

        Args:
            ciphertext (bytes): Encrypted message.

        Returns:
            str or None: Decoded string, or None if key is too short.
        """
        if len(self.key) < len(ciphertext):
            return None
        decrypted = bytes([c ^ k for c, k in zip(ciphertext, self.key)])
        return decrypted.decode('utf-8', errors='ignore')
