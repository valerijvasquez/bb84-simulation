from bb84.simulation import BB84Simulation

def main():
    print("\n--- BB84 quantum key distribution simulation ---")

    print("\n=== Choose simulation parameters ===")
    use_eve = input("Include eavesdropping? (y/n): ").strip().lower() == 'y'
    eve_fraction = float(input("Fraction of qubits Eve should intercept (0.0 to 1.0): ")) if use_eve else 0.0
    flip_probability = float(input("Bit flip probability (0.0 to 1.0): "))
    loss_probability = float(input("Qubit loss probability (0.0 to 1.0): "))

    print("\n=== Enter message to send ===")
    message = input("Enter the message: ").strip()
    required_bits = len(message.encode()) * 8
    efficiency = 0.25
    key_length = int(required_bits / efficiency)
    print(f"Message requires {required_bits} bits → sending {key_length} qubits.")

    sim = BB84Simulation(
        key_length=key_length,
        use_eve=use_eve,
        eve_fraction=eve_fraction,
        flip_probability=flip_probability,
        loss_probability=loss_probability
    )
    sim.message = message

    sim.run()

if __name__ == "__main__":
    main()
