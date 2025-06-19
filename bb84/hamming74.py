import hashlib


class Hamming74:
    def __init__(self):
        pass

    def run(self, alice_key, bob_key):
        corrected = self.correct(bob_key, alice_key)
        print("\nHamming74 finished: checking key consistency via hash.")
        if corrected:
            print("Hamming74 attempt successful: all blocks corrected.")
            return "SUCCESS", corrected
        else:
            print("Hamming74 attempt failed: key mismatch detected.")
            return "FAILURE", None

    def correct(self, bob_bits, reference):
        length = (min(len(bob_bits), len(reference)) // 4) * 4
        bob_bits = bob_bits[:length]
        reference = reference[:length]

        encoded = self.encode_key(reference)

        received = []
        for i in range(0, len(encoded), 7):
            block = encoded[i:i+7]
            block[2] = bob_bits[(i // 7) * 4 + 0]
            block[4] = bob_bits[(i // 7) * 4 + 1]
            block[5] = bob_bits[(i // 7) * 4 + 2]
            block[6] = bob_bits[(i // 7) * 4 + 3]
            received.extend(block)

        corrected = self.decode_key(received)

        ha = hashlib.sha256(bytes(reference)).hexdigest()
        hb = hashlib.sha256(bytes(corrected)).hexdigest()

        return corrected if ha == hb else None

    def encode_block(self, data_bits):
        d1, d2, d3, d4 = data_bits
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        return [p1, p2, d1, p3, d2, d3, d4]

    def decode_block(self, codeword):
        c = codeword[:]
        s1 = c[0] ^ c[2] ^ c[4] ^ c[6]
        s2 = c[1] ^ c[2] ^ c[5] ^ c[6]
        s3 = c[3] ^ c[4] ^ c[5] ^ c[6]
        error_position = s1 + (s2 << 1) + (s3 << 2)
        if 1 <= error_position <= 7:
            c[error_position - 1] ^= 1
        return [c[2], c[4], c[5], c[6]]

    def encode_key(self, bits):
        length = (len(bits) // 4) * 4
        bits = bits[:length]
        codewords = []
        for i in range(0, length, 4):
            codewords.extend(self.encode_block(bits[i:i+4]))
        return codewords

    def decode_key(self, codewords):
        recovered = []
        for i in range(0, len(codewords), 7):
            recovered.extend(self.decode_block(codewords[i:i+7]))
        return recovered

