# Cipher-Sync: Zero-Knowledge Steganographic Vault

**Author:** Ahmad Amad Abu Zayed 
**Field:** Computer Science 

## Overview
Cipher-Sync is an academic-grade steganography engine that weaves highly encrypted payloads into the frequency domain of standard JPEG images. It acts as a zero-knowledge local vault, allowing users to hide sensitive files inside ordinary photos without altering the image's visual integrity or triggering standard forensic statistical anomalies.

## Core Architecture
This project implements a multi-layered security pipeline:
1. **Cryptography:** AES-256-GCM authenticated encryption utilizing high-iteration PBKDF2 key derivation.
2. **Error Correction:** Reed-Solomon $GF(2^8)$ mathematical armor to auto-heal bit-flips caused by compression.
3. **Scatter Pathing:** Deterministic Pseudo-Random Number Generation (PRNG) to distribute data chaotically across the image matrix, defeating localized forensic analysis.
4. **Direct Matrix Hooking:** Bypasses standard image compression by injecting directly into Quantized DCT mid-frequency coefficients via `libjpeg-turbo`.

## Usability
Cipher-Sync features a modern, dark-mode graphical interface built with `CustomTkinter`, allowing non-technical users to lock and recover files via a simple drag-and-drop workflow.

## Installation for Developers
```bash
git clone [https://github.com/yourusername/Cipher-Sync.git](https://github.com/yourusername/Cipher-Sync.git)
cd Cipher-Sync
pip install -r requirements.txt
python3 app_gui.py
