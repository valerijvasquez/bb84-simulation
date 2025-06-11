import itertools

def generate_codeword_ecc32(x1, x2, x3, x4, x5, s):
    # Define parity bits
    p1  = x1 ^ x2
    p2  = x1 ^ x3
    p3  = x1 ^ x4
    p4  = x1 ^ x5
    p5  = x2 ^ x3
    p6  = x2 ^ x4
    p7  = x2 ^ x5
    p8  = x3 ^ x4
    p9  = x3 ^ x5
    p10 = x4 ^ x5

    p11 = x1 ^ x2 ^ x3
    p12 = x1 ^ x2 ^ x4
    p13 = x1 ^ x2 ^ x5
    p14 = x1 ^ x3 ^ x4
    p15 = x1 ^ x3 ^ x5
    p16 = x1 ^ x4 ^ x5
    p17 = x2 ^ x3 ^ x4
    p18 = x2 ^ x3 ^ x5
    p19 = x2 ^ x4 ^ x5
    p20 = x3 ^ x4 ^ x5

    p21 = x1 ^ x2 ^ x3 ^ x4
    p22 = x1 ^ x2 ^ x3 ^ x5
    p23 = x1 ^ x2 ^ x4 ^ x5
    p24 = x1 ^ x3 ^ x4 ^ x5
    p25 = x2 ^ x3 ^ x4 ^ x5

    p26 = x1 ^ x2 ^ x3 ^ x4 ^ x5

    # Codeword
    codeword = [x1, x2, x3, x4, x5,
                p1, p2, p3, p4, p5,
                p6, p7, p8, p9, p10,
                p11, p12, p13, p14, p15,
                p16, p17, p18, p19, p20,
                p21, p22, p23, p24, p25, p26]

    # Apply flipping rule to all parity bits
    for i in range(26):
        if (s >> i) & 1:
            codeword[5 + i] ^= 1
        

    return codeword

def find_rule_for_alice_block(block):
    x1, x2, x3, x4, x5 = block[:5]
    for s in range(2**26):
        candidate = generate_codeword_ecc32(x1, x2, x3, x4, x5, s)
        if candidate == block:
            return s

    return None

def correct_bob_block(bob_block, s):
    min_dist = 32
    best_block = None
    for xbits in itertools.product([0, 1], repeat=5):
        candidate = generate_codeword_ecc32(*xbits, s)
        dist = sum((a != b) for a, b in zip(candidate, bob_block))
        if dist < min_dist:
            min_dist = dist
            best_block = candidate
    return best_block
 

class ECC32:
    def __init__(self, alice_key, bob_key):
        self.alice_key = alice_key
        self.bob_key = bob_key
        self.corrected_key = []
        self.failed_blocks = 0

    def run(self):
        print("\n=== Information reconciliation: running ECC32 ===")

        key_len = len(self.alice_key)
        truncate_len = (key_len // 31) * 31
        alice_key = self.alice_key[:truncate_len]
        bob_key = self.bob_key[:truncate_len]

        corrected_blocks = []
        failed_blocks = 0

        for i in range(0, truncate_len, 31):
            alice_block = alice_key[i:i+31]
            bob_block = bob_key[i:i+31]

            # Alice selects s for this block
            found_s = find_rule_for_alice_block(alice_block)

            # Bob corrects his block
            corrected_block = correct_bob_block(bob_block, found_s)

            # Check correction result
            dist = sum(a != b for a, b in zip(corrected_block, alice_block))
            if dist > 0:
                print(f"Block {i//31}: correction failed, distance = {dist}")
                failed_blocks += 1
                continue

            # Success
            corrected_blocks.extend(corrected_block)

        print(f"\nECC32 finished: {failed_blocks} blocks failed.")
        print(f"Corrected key length: {len(corrected_blocks)} bits")

        self.corrected_key = corrected_blocks
        self.failed_blocks = failed_blocks

        if failed_blocks == 0:
            return "SUCCESS", corrected_blocks
        else:
            return "FAILURE", corrected_blocks




