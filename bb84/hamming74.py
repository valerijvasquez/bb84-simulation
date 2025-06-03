class Hamming74:
    @staticmethod
    def encode_block(data_bits):
        d1, d2, d3, d4 = data_bits
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        return [p1, p2, d1, p3, d2, d3, d4]

    @staticmethod
    def decode_block(codeword):
        c = codeword[:]
        s1 = c[0] ^ c[2] ^ c[4] ^ c[6]
        s2 = c[1] ^ c[2] ^ c[5] ^ c[6]
        s3 = c[3] ^ c[4] ^ c[5] ^ c[6]
        error_position = s1 + (s2 << 1) + (s3 << 2)
        if 1 <= error_position <= 7:
            c[error_position - 1] ^= 1
        return [c[2], c[4], c[5], c[6]]

    @staticmethod
    def encode_key(bits):
        length = (len(bits) // 4) * 4
        bits = bits[:length]
        codewords = []
        for i in range(0, length, 4):
            codewords.extend(Hamming74.encode_block(bits[i:i+4]))
        return codewords

    @staticmethod
    def decode_key(codewords):
        recovered = []
        for i in range(0, len(codewords), 7):
            recovered.extend(Hamming74.decode_block(codewords[i:i+7]))
        return recovered


class Hamming74Corrector:
    def __init__(self):
        self.encoder = Hamming74

    def correct(self, bob_bits, reference):
        # Truncate to multiple of 4
        length = (min(len(bob_bits), len(reference)) // 4) * 4
        bob_bits = bob_bits[:length]
        reference = reference[:length]

        # Generate codewords from reference
        encoded = self.encoder.encode_key(reference)

        # Replace data bits with Bob’s bits
        received = []
        for i in range(0, len(encoded), 7):
            block = encoded[i:i+7]
            # Replace data part with Bob's bits
            block[2] = bob_bits[(i // 7) * 4 + 0]
            block[4] = bob_bits[(i // 7) * 4 + 1]
            block[5] = bob_bits[(i // 7) * 4 + 2]
            block[6] = bob_bits[(i // 7) * 4 + 3]
            received.extend(block)

        corrected = self.encoder.decode_key(received)

        # Compare hashes (optional, match your pipeline)
        from hashlib import sha256
        ha = sha256(bytes(reference)).hexdigest()
        hb = sha256(bytes(corrected)).hexdigest()

        if ha == hb:
            return corrected
        else:
            return None
