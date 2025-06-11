import itertools

def find_rule_index_from_codeword(z_chunk):
    """
    Given a 7-bit ECC codeword z_chunk, find the ECC rule index (0–15)
    that reproduces this codeword using its first 3 bits.
    """
    x1, x2, x3 = z_chunk[:3]
    for s in range(16):
        candidate = generate_codeword_ecc16(x1, x2, x3, s)
        if candidate == z_chunk:
            return s
    raise ValueError("No ECC rule found that generates the codeword.")

def generate_codeword_ecc16(x1, x2, x3, s):
    """Generate a 7-bit codeword using one of the 16 ECCs (s ∈ [0,15])"""
    p1 = x1 ^ x2
    p2 = x2 ^ x3
    p3 = x1 ^ x3
    p4 = x1 ^ x2 ^ x3
    parity = [p1, p2, p3, p4]

    # Flip selected parity bits based on 4-bit index
    for i in range(4):
        if (s >> i) & 1:
            parity[i] = 1 - parity[i]

    return [x1, x2, x3] + parity

def correct_bob_codeword(bob_codeword, s):
    """Try all 8 possible first 3 bits to find the closest match"""
    min_dist = 7
    best_codeword = None

    for xbits in itertools.product([0, 1], repeat=3):
        candidate = generate_codeword_ecc16(*xbits, s)
        dist = sum((a != b) for a, b in zip(candidate, bob_codeword))
        if dist < min_dist:
            min_dist = dist
            best_codeword = candidate

    return best_codeword


class ECC16:
    def __init__(self, alice_key, bob_key):
        self.alice_key = alice_key
        self.bob_key = bob_key
        self.corrected_key = []
        self.failed_blocks = 0

    def run(self):
        print("\n=== Information reconciliation: running ECC16 ===")

        key_len = len(self.alice_key)
        truncate_len = (key_len // 7) * 7
        alice_key = self.alice_key[:truncate_len]
        bob_key = self.bob_key[:truncate_len]

        print(f"Truncated sifted key length used: {truncate_len} bits ({truncate_len // 7} full blocks).")

        corrected_blocks = []
        failed_blocks = 0

        for i in range(0, truncate_len, 7):
            alice_block = alice_key[i:i+7]
            bob_block = bob_key[i:i+7]

            # Alice finds s for her block
            try:
                found_s = find_rule_index_from_codeword(alice_block)
            except ValueError:
                print(f"Block {i//7}: could not find valid s! Skipping block.")
                failed_blocks += 1
                continue

            # Bob corrects his block
            corrected_block = correct_bob_codeword(bob_block, found_s)

            # Check correction result
            dist = sum((a != b) for a, b in zip(corrected_block, alice_block))
            if dist > 0:
                print(f"Block {i//7}: correction failed, distance = {dist}")
                failed_blocks += 1
                continue

            # Success → store full 7-bit block
            corrected_blocks.extend(corrected_block)

        print(f"\nECC16 finished: {failed_blocks} blocks failed.")
        print(f"Corrected key length: {len(corrected_blocks)} bits")

        self.corrected_key = corrected_blocks
        self.failed_blocks = failed_blocks

        if failed_blocks == 0:
            return "SUCCESS", corrected_blocks
        else:
            return "FAILURE", corrected_blocks



