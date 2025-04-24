#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 09:58:11 2025

@author: valerijvasquez
"""

import numpy as np
import hashlib

# Quantum state definitions
ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])
ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

bits = [0, 1]
bases = ['+', 'x']

class QubitSender:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bits = None
        self.bases = None

    def prepare_qubits(self):
        self.bits = np.random.choice(bits, self.key_length)
        self.bases = np.random.choice(bases, self.key_length)

    def encode_qubits(self):
        states = []
        for bit, basis in zip(self.bits, self.bases):
            if basis == '+':
                state = ket_0 if bit == 0 else ket_1
            else:
                state = ket_plus if bit == 0 else ket_minus
            states.append((state, basis))
        self.encoded_qubits = states


class QubitReceiver:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bases = None
        self.measured_bits = None

    def choose_bases(self):
        self.bases = np.random.choice(bases, self.key_length)

    def measure_qubits(self, encoded_qubits):
        measured = []
        for i, (state, alice_basis) in enumerate(encoded_qubits):
            if state is None:
                measured.append(None)
                continue
            bob_basis = self.bases[i]
            if bob_basis == alice_basis:
                bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1
            else:
                bit = np.random.choice(bits)
            measured.append(bit)
        self.measured_bits = measured

    def reconcile_with(self, alice_bases):
        matching_indices = (self.bases == alice_bases) & (np.array(self.measured_bits) != None)
        self.reconciled_key = np.array(self.measured_bits)[matching_indices]
        return self.reconciled_key

    def error_rate(self, alice_bits, alice_bases):
        matching_indices = (self.bases == alice_bases) & (np.array(self.measured_bits) != None)
        alice_reconciled = alice_bits[matching_indices]
        bob_reconciled = np.array(self.measured_bits)[matching_indices]

        if len(alice_reconciled) == 0:
            return None

        errors = alice_reconciled != bob_reconciled
        return np.mean(errors)


class Channel:
    def __init__(self, sender, receiver, eavesdropper=None, flip_probability=0.0, loss_probability=0.0):
        self.sender = sender
        self.receiver = receiver
        self.eavesdropper = eavesdropper
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.loss_count = 0
        self.flip_count = 0

    def transmit(self):
        if self.eavesdropper:
            qubits = self.eavesdropper.intercept(self.sender.encoded_qubits)
        else:
            qubits = self.sender.encoded_qubits

        noisy_qubits = []
        for state, basis in qubits:
            if np.random.rand() < self.loss_probability:
                self.loss_count += 1
                noisy_qubits.append((None, basis))
            else:
                if np.random.rand() < self.flip_probability:
                    self.flip_count += 1
                    flipped_bit = 1 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 0
                    flipped_state = ket_1 if flipped_bit == 1 else ket_0
                    noisy_qubits.append((flipped_state, basis))
                else:
                    noisy_qubits.append((state, basis))

        self.receiver.measure_qubits(noisy_qubits)


class Eavesdropper:
    def __init__(self, interception_fraction=1.0):
        self.interception_fraction = interception_fraction
        self.bases = None
        self.intercepted_bits = None

    def intercept(self, encoded_qubits):
        total = len(encoded_qubits)
        num_to_intercept = int(total * self.interception_fraction)
        indices_to_intercept = np.random.choice(total, num_to_intercept, replace=False)

        measured_bits = []
        measured_bases = []

        for i, (state, alice_basis) in enumerate(encoded_qubits):
            if i in indices_to_intercept:
                eve_basis = np.random.choice(bases)
                if eve_basis == alice_basis:
                    bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1
                else:
                    bit = np.random.choice(bits)
            else:
                eve_basis = alice_basis
                bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1

            measured_bases.append(eve_basis)
            measured_bits.append(bit)

        self.bases = np.array(measured_bases)
        self.intercepted_bits = np.array(measured_bits)

        return list(zip([ket_0 if b == 0 else ket_1 for b in measured_bits], measured_bases))


class BB84Simulation:
    def __init__(self, key_length=20, use_eve=False, eve_fraction=1.0,
                 use_hashing=False, flip_probability=0.0, loss_probability=0.0):
        self.key_length = key_length
        self.use_eve = use_eve
        self.eve_fraction = eve_fraction
        self.use_hashing = use_hashing
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.alice = None
        self.bob = None
        self.eve = None
        self.channel = None
        self.shared_key = None
        self.error_rate = None
        self.hashed_key = None

    def run(self):
        self.alice = QubitSender(self.key_length)
        self.bob = QubitReceiver(self.key_length)
        self.eve = Eavesdropper(self.eve_fraction) if self.use_eve else None

        self.alice.prepare_qubits()
        self.alice.encode_qubits()
        self.bob.choose_bases()

        self.channel = Channel(
            self.alice,
            self.bob,
            self.eve,
            flip_probability=self.flip_probability,
            loss_probability=self.loss_probability
        )
        self.channel.transmit()

        self.shared_key = self.bob.reconcile_with(self.alice.bases)
        self.error_rate = self.bob.error_rate(self.alice.bits, self.alice.bases)

        if self.use_hashing:
            bitstring = ''.join(map(str, self.shared_key))
            self.hashed_key = hashlib.sha256(bitstring.encode()).hexdigest()

    def show_results(self):
        print("Alice bits:       ", self.alice.bits)
        print("Alice bases:      ", self.alice.bases)
        if self.eve:
            print("Eve bases:        ", self.eve.bases)
            print("Eve bits:         ", self.eve.intercepted_bits)
        print("Bob bases:        ", self.bob.bases)
        print("Bob measurements: ", self.bob.measured_bits)
        print("Matching bases:   ", self.alice.bases == self.bob.bases)
        print("Reconciled key:   ", self.shared_key)
        print("Error rate:       ", "N/A" if self.error_rate is None else f"{round(self.error_rate * 100, 2)}%")
        print(f"Channel lost qubits: {self.channel.loss_count}")
        print(f"Channel flipped qubits: {self.channel.flip_count}")
        if self.hashed_key:
            print("Final hashed key (SHA-256):", self.hashed_key)



def main():
    print("\n--- BB84 Quantum Key Distribution Simulation ---")

    key_length = int(input("How many qubits to send? "))

    use_eve_input = input("Include eavesdropping? (y/n): ").strip().lower()
    use_eve = use_eve_input == 'y'
    eve_fraction = 0.0
    if use_eve:
        eve_fraction = float(input("Fraction of qubits Eve should intercept (e.g., 0.5): "))

    flip_probability = float(input("Bit flip probability (0.0 to 1.0): "))
    loss_probability = float(input("Qubit loss probability (0.0 to 1.0): "))

    use_hashing_input = input("Use SHA-256 hashing for privacy amplification? (y/n): ").strip().lower()
    use_hashing = use_hashing_input == 'y'

    error_threshold = float(input("Set error rate threshold for accepting the key (e.g., 0.1): "))

    while True:
        sim = BB84Simulation(
            key_length=key_length,
            use_eve=use_eve,
            eve_fraction=eve_fraction,
            use_hashing=use_hashing,
            flip_probability=flip_probability,
            loss_probability=loss_probability
        )

        sim.run()
        sim.show_results()

        if sim.error_rate is not None and sim.error_rate > error_threshold:
            print(f"\n⚠️  ERROR RATE TOO HIGH ({round(sim.error_rate * 100, 2)}%) > THRESHOLD ({error_threshold * 100}%)")
            retry = input("Do you want to try a new channel? (y/n): ").strip().lower()
            if retry != 'y':
                print("Aborting simulation.")
                break
        else:
            print("\n✅ Simulation successful and within error threshold.")
            break


if __name__ == "__main__":
    main()

    


   
    
    
