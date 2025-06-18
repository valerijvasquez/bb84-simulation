# BB84 Quantum Key Distribution Simulation

This project implements a modular simulation of the BB84 quantum key distribution protocol. It models quantum transmission, optional eavesdropping, and classical post-processing including error estimation, error correction, privacy amplification, and one-time pad encryption.

The simulation was developed as part of a bachelor thesis project at Stockholm University.

---

## Features

- Fully modular BB84 protocol simulation
- Quantum channel with configurable bit flip and loss probabilities
- Optional eavesdropper (Eve) with tunable intercept fraction
- Sampling-based error estimation
- Multiple error correction strategies (ECC modules)
- Privacy amplification using SHAKE-256
- One-time pad encryption of user message

---

## Requirements

- Python 3.8+
- Standard libraries used:
  - `random`
  - `hashlib`
  - `secrets`
  - `math`
  - `itertools`
  - `numpy`

No additional external packages required.

---

## Usage

Run the simulation from the terminal or an IDE like Spyder:

```
python main.py
```

You will be prompted to:
- Enable or disable eavesdropping
- Set bit flip and qubit loss probabilities
- Enter a message to encrypt

The simulation then:
1. Simulates quantum transmission and measurement
2. Performs basis reconciliation
3. Estimates the channel error rate
4. Applies ECC if selected
5. Compresses the key using privacy amplification
6. Encrypts the message using a one-time pad

---

## Project structure

| File | Description |
|------|-------------|
| `main.py` | Entry point for full simulation |
| `simulation.py` | Core BB84 protocol logic |
| `globals.py` | Defines standard basis and qubit states |
| `sender.py` | Alice's qubit preparation and sending |
| `quantum_channel.py` | Applies loss, noise, and eavesdropping |
| `eavesdropper.py` | Models Eve's intercept-resend attack strategy |
| `receiver.py` | Bob's measurement logic |
| `ecc_*.py` | ECC modules: XOR, ECC16, ECC32, Cascade, Hamming74 |
| `privacy_amplification.py` | Applies SHAKE-256 compression |
| `otp.py` | Handles one-time pad encryption and decryption |

---

## Author

Valerij Vasquez  
Bachelor thesis, Department of Physics  
Stockholm University, 2025
