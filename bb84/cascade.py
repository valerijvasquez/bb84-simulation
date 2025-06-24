import random
import hashlib

class Cascade:
    
    
    def __init__(self, subset_fraction=0.1):
        self.subset_fraction = subset_fraction

    def largest_power_of_two_leq(self, n):
        power = 1
        while power * 2 <= n:
            power *= 2
        return power

    def get_block_indices(self, block_size):
        num_full_blocks = len(self.alice_key) // block_size
        blocks = []
        for i in range(num_full_blocks):
            block = list(range(i * block_size, (i + 1) * block_size))
            blocks.append(block)

        remainder = len(self.alice_key) % block_size
        if remainder > 0:
            last_block = list(range(num_full_blocks * block_size, len(self.alice_key)))
            blocks.append(last_block)
            self.log.append(f"Remainder block of size {len(last_block)}")
        return blocks
    
    def get_parity(self, block_indices):
        self.parity_counter += 1
        return sum([self.alice_key[i] for i in block_indices]) % 2

    def get_bob_parity(self, block_indices):
        self.parity_counter += 1
        return sum([self.bob_key[i] for i in block_indices]) % 2

    def reshuffle_keys(self):
        indices = list(range(len(self.alice_key)))
        random.shuffle(indices)

        self.alice_key = [self.alice_key[i] for i in indices]
        self.bob_key = [self.bob_key[i] for i in indices]
        self.log.append("Keys reshuffled\n")

    def check_hash_on_subset(self):
        subset_size = max(1, int(self.subset_fraction * len(self.alice_key)))
        subset_indices = random.sample(range(len(self.alice_key)), subset_size)

        alice_bits = [self.alice_key[i] for i in subset_indices]
        bob_bits = [self.bob_key[i] for i in subset_indices]

        alice_hash = hashlib.sha256(bytes(alice_bits)).hexdigest()
        bob_hash = hashlib.sha256(bytes(bob_bits)).hexdigest()

        match = (alice_hash == bob_hash)
        self.log.append(f"Hash check on subset ({subset_size} bits) → {'PASS' if match else 'FAIL'}")
        return match

    def check_full_key_hash(self):
        alice_bits = bytes(self.alice_key)
        bob_bits = bytes(self.bob_key)

        alice_hash = hashlib.sha256(alice_bits).hexdigest()
        bob_hash = hashlib.sha256(bob_bits).hexdigest()

        match = (alice_hash == bob_hash)
        self.log.append(f"FINAL FULL KEY HASH CHECK → {'PASS' if match else 'FAIL'}")
        return match

    def binary_search_full(self, block_indices):
        if len(block_indices) == 1:
            i = block_indices[0]
            self.bob_key[i] ^= 1
            self.log.append(f"Corrected bit at index {i}")
            return

        mid = len(block_indices) // 2
        first_half = block_indices[:mid]
        second_half = block_indices[mid:]

        alice_parity_first = self.get_parity(first_half)
        bob_parity_first = self.get_bob_parity(first_half)
        self.parity_counter += 1

        if alice_parity_first != bob_parity_first:
            self.binary_search_full(first_half)

        else:
            alice_parity_second = self.get_parity(second_half)
            bob_parity_second = self.get_bob_parity(second_half)
            self.parity_counter += 1

            if alice_parity_second != bob_parity_second:
                self.binary_search_full(second_half)

    def run_full_cascade(self, num_global_rounds=6):

        self.parity_counter = 0  

        stopping_block_sizes = [16, 8, 4, 4, 4, 2] 

        for global_round in range(1, num_global_rounds + 1):
            print(f"\n=== Global round {global_round} ===")
        
            current_block_size = self.initial_block_size
            round_num = 1

            min_block_size = stopping_block_sizes[global_round - 1]

            while current_block_size >= min_block_size:
                print(f"\n--- Round {round_num} ---")
                print(f"Current block size: {current_block_size}")

                blocks = self.get_block_indices(current_block_size)

                num_mismatches = 0
                for block in blocks:
                    alice_parity = self.get_parity(block)
                    bob_parity = self.get_bob_parity(block)

                    if alice_parity != bob_parity:
                        num_mismatches += 1
                        self.binary_search_full(block)

                print(f"Block size {current_block_size}: {num_mismatches} mismatches corrected.")
                print("Reshuffling keys...")
                self.reshuffle_keys()

                current_block_size = current_block_size // 2
                round_num += 1

            if self.check_hash_on_subset():
                print("Hash on subset OK. Terminating early.")
                break

        if self.check_full_key_hash():
            print("Cascade SUCCESS: keys match fully.")
            return "SUCCESS"
        else:
            print("Cascade FAILED: keys still differ.")
            return "FAILURE"
        
    def run(self, alice_key, bob_key):
        self.alice_key = alice_key
        self.bob_key = bob_key
        self.parity_counter = 0
        self.log = []

        key_len = len(self.alice_key)
        self.initial_block_size = self.largest_power_of_two_leq(key_len // 2)
        print(f"Initial block size selected: {self.initial_block_size}")

        result = self.run_full_cascade()

        if result == "SUCCESS":
            return "SUCCESS", self.bob_key
        else:
            return "FAILURE", None
