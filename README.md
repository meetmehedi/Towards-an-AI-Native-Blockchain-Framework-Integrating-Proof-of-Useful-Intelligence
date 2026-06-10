# Towards an AI-Native Blockchain Framework

This repository contains the official codebase, simulation engines, security taxonomy, post-quantum cryptographic benchmarks, and the IEEE TDSC manuscript for our research proposal: **"Towards an AI-Native Blockchain Framework: Integrating Proof of Useful Intelligence, Zero-Knowledge Machine Learning Security, and Post-Quantum Cryptography"**.

Authors: **Md. Mehedi Hasan**, **Asraful Islam Sharthak**, and **Prof. Dr. Md. Abdul Based**, Principal Investigator

---

## 📂 Repository Structure

The project is structured into modular research components:

```
├── simulation/            # PoUI Consensus Simulation & Theorems (RQ1)
│   ├── trust_score_model.py     # Trust Score mathematical implementation
│   ├── run_simulation.py        # 1,000-epoch simulation engine (N=100 nodes)
│   ├── compare_pos_poui.py      # Efficiency comparison of PoUI vs. PoS
│   ├── formal_analysis.py       # Formal bounds, Sybil-resistance, & Nash Eq. proofs
│   └── results/                 # JSON outputs of simulation runs
│
├── zkml-analysis/         # ZKML Underconstrained Circuit Taxonomy (RQ2)
│   ├── zkml_taxonomy.py         # Formulations of V-I through V-V vulnerability classes
│   └── results/                 # JSON output of the ZKML security taxonomy
│
├── pqc-benchmarks/        # Post-Quantum Cryptography (PQC) Benchmarking (RQ3)
│   └── results/                 # ML-DSA and ML-KEM network and sizing overhead benchmarks
│
├── architecture/          # Co-Design Interface Contracts & Failures (RQ4, RQ5)
│   └── codesign_analysis.py     # Co-design model, slots budgets, and overhead mitigations
│
├── literature/            # PRISMA 2020 Systematic Literature Review (SLR)
│   ├── prisma_slr.py            # Automated SLR database manager (60 papers included)
│   └── prisma_database.json     # Compiled database of literature review
│
└── paper/                 # IEEE TDSC Manuscript & Figure Generators
    ├── main.tex                 # LaTeX manuscript
    ├── references.bib           # BibTeX references
    ├── generate_figures.py      # Script generating key research figures
    ├── generate_prisma.py       # Script generating the PRISMA 2020 flowchart
    └── figures/                 # PNG outputs of generated figures
```

---

## 🚀 How to Run the Simulations

### 1. Prerequisite Packages
Install dependencies (principally NumPy, SciPy, Matplotlib):
```bash
pip install numpy scipy matplotlib
```

### 2. Run PoUI vs. PoS Comparison Simulation
Evaluate the performance and security bounds of the Proof of Useful Intelligence (PoUI) Trust Score against baseline Proof of Stake (PoS):
```bash
python3 simulation/compare_pos_poui.py
```
*Key Result:* PoUI convergence is **225× faster** than PoS in identifying and excluding malicious validator nodes.

### 3. Generate Paper Figures
To regenerate all research figures (Fig. 1-4 and PRISMA Flowchart) in the `paper/figures/` folder:
```bash
# Generate core research figures
python3 paper/generate_figures.py

# Generate PRISMA flow diagram
python3 paper/generate_prisma.py
```

### 4. Regenerate PRISMA Literature Database
To recompile the systematic review stats and update the PRISMA JSON database:
```bash
python3 literature/prisma_slr.py
```

---

## 📊 Summary of Research Findings

### 🛡️ PoUI Trust Score (RQ1)
*   **Malicious Exclusion Rate:** **100%** of malicious nodes (15/15) excluded from the active validator set.
*   **Exclusion Speed:** Mean exclusion epoch of **2.53 epochs**, converging with $P \ge 0.96$ by epoch 8.
*   **Sybil Resistance:** Mathematical gap parameter $\Delta = 0.725 > 0$, rendering Sybil strategies strictly disadvantageous.
*   **Game-Theoretic Soundness:** Proven that the unique Nash Equilibrium for a rational validator is genuine computation ($A_t = 1.0$).

### 🧬 ZKML Security Taxonomy (RQ2)
Classifies the 5 major underconstrained circuit vulnerability vectors for on-chain machine learning inference:
1.  **V-I (Under-Range Constraint):** Bypassing activation range checks.
2.  **V-II (Non-Deterministic Witness Assignment):** Bypassing ArgMax/TopK sorting.
3.  **V-III (Missing Intermediate Constraint):** Skipping intermediate neural layers.
4.  **V-IV (Floating-Point Approximation Exploit):** Logit shifts via scaling factors.
5.  **V-V (Commitment-Output Mismatch):** Proving correctness on an uncommitted model.

### 🔑 Post-Quantum Cryptography Overhead (RQ3)
*   **Recommendation:** **ML-DSA-44** (signatures) + **ML-KEM-768** (key exchange).
*   **Overhead Mitigation:** Naive state growth of 20.24 MB/block is reduced to **202 KB/block** using signature aggregation (Mitigation M1).

### 🤝 Co-Design Security Properties (RQ4 & RQ5)
*   **ESP-1 (Proof-of-Identity Chain):** Establishes non-repudiation of validator outputs.
*   **ESP-3 (Layered Slash Amplification):** Cryptographic ZKML proofs make slashing decisions irrefutable.
*   **FM-CD-4 (Size Budget Overflow):** Demonstrates that without co-design mitigations, PQC-signed proofs overrun traditional block budgets.

---

*This project is released under the MIT License.*
