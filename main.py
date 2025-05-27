from bb84.simulation import BB84Simulation
from bb84.otp import OneTimePad

def main():
    print("\n--- BB84 quantum key distribution simulation ---")

    message = input("Enter the message to send: ").strip()
    message_bytes = message.encode('utf-8')
    required_key_bits = len(message_bytes) * 8
    print(f"Message requires {required_key_bits} bits of key for one-time pad encryption.")

    estimated_efficiency = 0.25
    key_length = int(required_key_bits / estimated_efficiency)
    print(f"Estimated number of qubits to send: {key_length}")

    use_eve = input("Include eavesdropping? (y/n): ").strip().lower() == 'y'
    eve_fraction = 0.0
    if use_eve:
        eve_fraction = float(input("Fraction of qubits Eve should intercept (0.0 to 1.0): "))

    flip_probability = float(input("Bit flip probability (0.0 to 1.0): "))
    loss_probability = float(input("Qubit loss probability (0.0 to 1.0): "))
    error_threshold = float(input("Set error rate threshold for accepting the key (e.g., 0.1): "))

    while True:
        sim = BB84Simulation(
            key_length=key_length,
            use_eve=use_eve,
            eve_fraction=eve_fraction,
            flip_probability=flip_probability,
            loss_probability=loss_probability
        )

        sim.message = message
        sim.run()
        sim.estimate_error_from_sample()

        if sim.error_rate is not None and sim.error_rate > error_threshold:
            print(f"\nError rate too high ({round(sim.error_rate * 100, 2)}%) exceeds threshold ({error_threshold * 100}%).")
            retry = input("Try a new channel? (y/n): ").strip().lower()
            if retry != 'y':
                print("Aborting simulation.")
                break
            else:
                continue

        sim.show_results()

        if not hasattr(sim, 'final_key') or sim.final_key is None:
            print("No usable final key. ECC failed or key was too short.")
            retry = input("Try a new channel? (y/n): ").strip().lower()
            if retry != 'y':
                print("Aborting simulation.")
                break
            else:
                continue

        print("\n--- One-time pad encryption ---")
        use_message = input("Send the message using the final key? (y/n): ").strip().lower()
        if use_message == 'y':
            otp = OneTimePad(sim.final_key)
            encrypted = otp.encrypt(message)
            if encrypted is None:
                print("Final key too short for encryption.")
            else:
                decrypted = otp.decrypt(encrypted)
                print("Encrypted message:", encrypted)
                print("Decrypted message (Bob):", decrypted)
        else:
            print("Message transmission aborted.")

        print("Simulation complete and within error threshold.")
        break

if __name__ == "__main__":
    main()






