class OneTimePad:
    def __init__(self, key_bits):
        self.key = self._bits_to_bytes(key_bits)

    def _bits_to_bytes(self, key_bits):
        byte_chunks = [key_bits[i:i + 8] for i in range(0, len(key_bits), 8)]
        return bytes([
            int(''.join(str(bit) for bit in chunk), 2)
            for chunk in byte_chunks
        ])

    def encrypt(self, plaintext):
        message_bytes = plaintext.encode('utf-8')
        if len(self.key) < len(message_bytes):
            return None
        return bytes([m ^ k for m, k in zip(message_bytes, self.key)])

    def decrypt(self, ciphertext):
        if len(self.key) < len(ciphertext):
            return None
        decrypted = bytes([c ^ k for c, k in zip(ciphertext, self.key)])
        return decrypted.decode('utf-8', errors='ignore')
