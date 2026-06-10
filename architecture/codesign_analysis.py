"""
Phase 5: Architectural Co-Design — Interface Contracts & Interaction Analysis (RQ4, RQ5)
========================================================================================
Defines formal interface contracts between the three architectural pillars:
  Layer 1 — PoUI Consensus Layer
  Layer 2 — ZKML Proof Generation & Verification Layer
  Layer 3 — PQC Signature & Key Encapsulation Layer

RQ4: Formal interface contracts governing PoUI ↔ ZKML ↔ PQC integration
RQ5: Emergent security properties and failure modes from co-design

Authors: Md. Mehedi Hasan (Team Lead), Antigravity AI (Research Assistant)
Project: Towards an AI-Native Blockchain Framework
"""

import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


# =============================================================================
# SECTION 1: LAYER DEFINITIONS
# =============================================================================

class LayerID(str, Enum):
    CONSENSUS = "L1-PoUI"
    ZKML      = "L2-ZKML"
    PQC       = "L3-PQC"


@dataclass
class InterfaceContract:
    """
    Formal interface contract between two architectural layers.
    Specifies the exact data structures, guarantees, and failure modes
    at each layer boundary.
    """
    contract_id: str
    caller_layer: LayerID
    callee_layer: LayerID
    operation: str

    # Pre-conditions: what caller must guarantee before calling
    preconditions: List[str]

    # Post-conditions: what callee guarantees on success
    postconditions: List[str]

    # Failure modes: what can go wrong at this interface
    failure_modes: List[str]

    # Data types exchanged
    input_types: Dict[str, str]
    output_types: Dict[str, str]

    # Performance contract
    max_latency_ms: float
    max_size_bytes: int


# =============================================================================
# SECTION 2: INTERFACE CONTRACTS (RQ4)
# =============================================================================

CONTRACTS: List[InterfaceContract] = [

    # ─── L1 ↔ L2: Consensus requests ZKML proof ────────────────────────────
    InterfaceContract(
        contract_id="IC-01",
        caller_layer=LayerID.CONSENSUS,
        callee_layer=LayerID.ZKML,
        operation="RequestInferenceProof",
        preconditions=[
            "PRE-1: Input x ∈ ℝⁿ is a valid, normalized AI inference task",
            "PRE-2: Model commitment H(θ) = committed_root is registered on-chain",
            "PRE-3: Validator node is not currently slashed (S_t = 0)",
            "PRE-4: Validator has valid PQC-signed session key from L3 (IC-03 completed)",
        ],
        postconditions=[
            "POST-1: π is a valid ZK proof: Verify(C, x, y, π) = 1 ⟹ y = f_θ(x)",
            "POST-2: y is the genuine inference output of model θ on input x",
            "POST-3: Proof π binds to the committed model: MerkleRoot(weights) = H(θ)",
            "POST-4: π is generated within max_latency_ms (circuit proving budget)",
        ],
        failure_modes=[
            "FM-01a: Proving timeout (circuit too large for slot budget) → ZKML layer returns TIMEOUT",
            "FM-01b: Underconstrained circuit (V-I through V-V) → forged proof accepted → Trust Score inflated",
            "FM-01c: OOM during witness generation → validator offline → Tₜ penalized via Uₜ term",
        ],
        input_types={
            "x": "float32[n]",
            "model_commitment": "bytes32 (Merkle root)",
            "epoch": "uint64",
            "validator_id": "bytes32",
        },
        output_types={
            "y": "float32[m] (inference output)",
            "pi": "bytes (ZK proof, ~100KB for typical EZKL circuit)",
            "proof_hash": "bytes32 (H(pi))",
        },
        max_latency_ms=5000.0,   # 5s proving budget per consensus round
        max_size_bytes=200_000,  # 200KB max proof size
    ),

    # ─── L2 ↔ L1: ZKML returns verified output to consensus ────────────────
    InterfaceContract(
        contract_id="IC-02",
        caller_layer=LayerID.ZKML,
        callee_layer=LayerID.CONSENSUS,
        operation="SubmitVerifiedOutput",
        preconditions=[
            "PRE-1: ZK proof π has been generated successfully (IC-01 post-conditions met)",
            "PRE-2: Proof π has been PQC-signed by the validator's ML-DSA key (IC-04 completed)",
            "PRE-3: Submission is within the consensus slot window",
        ],
        postconditions=[
            "POST-1: PoUI consensus layer accepts y as the validator's AI output for epoch t",
            "POST-2: Trust Score Tₜ is computed using y to derive Aₜ = accuracy(y)",
            "POST-3: Slash flag Sₜ = 0 (no fraud detected at submission time)",
        ],
        failure_modes=[
            "FM-02a: Late submission (after slot deadline) → Sₜ not updated, Uₜ penalized",
            "FM-02b: Invalid PQC signature on proof → submission rejected → validator slashed",
            "FM-02c: Proof verification fails on-chain → Sₜ = 1 → Trust Score collapses",
        ],
        input_types={
            "y": "float32[m]",
            "pi": "bytes",
            "pqc_signature": "bytes (ML-DSA signature on H(pi))",
            "validator_id": "bytes32",
            "epoch": "uint64",
        },
        output_types={
            "accepted": "bool",
            "slash_flag": "uint8 (0 or 1)",
            "trust_score_delta": "float64",
        },
        max_latency_ms=100.0,
        max_size_bytes=10_000,
    ),

    # ─── L1 ↔ L3: Consensus requests PQC key for validator ─────────────────
    InterfaceContract(
        contract_id="IC-03",
        caller_layer=LayerID.CONSENSUS,
        callee_layer=LayerID.PQC,
        operation="RegisterValidatorKey",
        preconditions=[
            "PRE-1: Validator has staked minimum collateral (economic security)",
            "PRE-2: ML-DSA public key pk is freshly generated (not previously registered)",
            "PRE-3: ML-KEM public key ek is provided for epoch key encapsulation",
        ],
        postconditions=[
            "POST-1: pk_validator committed on-chain: H(pk_validator) stored in registry",
            "POST-2: ML-KEM ciphertext c delivered to validator for session key establishment",
            "POST-3: Validator can now sign consensus messages with sk_validator",
        ],
        failure_modes=[
            "FM-03a: Duplicate key registration → rejected (replay attack prevention)",
            "FM-03b: ML-KEM decapsulation failure → session key not established → validator offline",
            "FM-03c: Weak key (low entropy) → detected by on-chain health check → rejected",
        ],
        input_types={
            "pk_validator": "bytes (ML-DSA-44 public key, 1312 bytes)",
            "ek_validator": "bytes (ML-KEM-768 encapsulation key, 1184 bytes)",
            "stake_proof": "bytes32",
        },
        output_types={
            "registry_commitment": "bytes32",
            "kem_ciphertext": "bytes (ML-KEM-768 ciphertext, 1088 bytes)",
            "session_id": "uint64",
        },
        max_latency_ms=500.0,
        max_size_bytes=5_000,
    ),

    # ─── L2 ↔ L3: ZKML proof is PQC-signed before submission ───────────────
    InterfaceContract(
        contract_id="IC-04",
        caller_layer=LayerID.ZKML,
        callee_layer=LayerID.PQC,
        operation="SignProofHash",
        preconditions=[
            "PRE-1: ZK proof π has been generated (IC-01 post-conditions met)",
            "PRE-2: Validator holds valid ML-DSA secret key sk_validator",
            "PRE-3: Epoch has not expired (no key rotation pending)",
        ],
        postconditions=[
            "POST-1: σ = ML-DSA.Sign(sk_validator, H(π)) is valid",
            "POST-2: σ binds the proof π to the specific validator identity",
            "POST-3: Any tampering with π after signing is detectable via ML-DSA.Verify",
        ],
        failure_modes=[
            "FM-04a: Key expired (epoch boundary) → signing fails → must re-register",
            "FM-04b: ML-DSA signing overhead exceeds slot budget → validator misses slot",
            "FM-04c: Side-channel attack on signing → sk_validator compromised (hardware mitigation needed)",
        ],
        input_types={
            "proof_hash": "bytes32 (H(π))",
            "sk_validator": "bytes (ML-DSA-44 secret key, 2560 bytes, in secure memory)",
            "epoch": "uint64",
        },
        output_types={
            "signature": "bytes (ML-DSA-44 signature, 2420 bytes)",
            "signing_time_us": "uint64",
        },
        max_latency_ms=1.0,    # ML-DSA-44 sign ≈ 195µs << 1ms budget
        max_size_bytes=2_500,
    ),
]


# =============================================================================
# SECTION 3: CO-DESIGN INTERACTION MATRIX (RQ5)
# =============================================================================

CODESIGN_INTERACTIONS = {
    "emergent_security_properties": [
        {
            "id": "ESP-1",
            "name": "Proof-of-Identity Chain",
            "description": (
                "When L3 (PQC) signs L2 (ZKML) proof hashes, the result is a "
                "cryptographically bound chain: validator_identity → model_weights → inference_output. "
                "This property DOES NOT exist when any single layer is deployed alone. "
                "It enables on-chain non-repudiation of AI outputs — a validator cannot "
                "later deny having submitted a specific inference result."
            ),
            "present_without_codesign": False,
            "security_benefit": "Non-repudiation + validator accountability",
        },
        {
            "id": "ESP-2",
            "name": "Quantum-Safe AI Governance",
            "description": (
                "The combination of PoUI (consensus), ZKML (verifiability), and ML-DSA (quantum resistance) "
                "creates an AI governance layer that is secure against both classical and quantum adversaries. "
                "A quantum computer cannot forge validator identities (ML-DSA), "
                "cannot generate false ZK proofs (ZKML soundness), "
                "and cannot manipulate consensus without exposing their Trust Score."
            ),
            "present_without_codesign": False,
            "security_benefit": "Post-quantum AI consensus security",
        },
        {
            "id": "ESP-3",
            "name": "Layered Slash Amplification",
            "description": (
                "A validator caught submitting a forged ZKML proof (V-I through V-V) "
                "has their PQC-signed evidence permanently recorded on-chain. "
                "The slash flag Sₜ = 1 in the Trust Score formula is backed by "
                "cryptographic evidence that cannot be repudiated. "
                "This makes slashing more credible than in classical PoS."
            ),
            "present_without_codesign": False,
            "security_benefit": "Cryptographically-evidenced slashing",
        },
    ],

    "failure_modes": [
        {
            "id": "FM-CD-1",
            "name": "Proving-Slot Race Condition",
            "description": (
                "ZKML proof generation (IC-01, up to 5000ms) + ML-DSA signing (IC-04, ~0.195ms) "
                "+ network submission must complete within the consensus slot window. "
                "If proving takes > slot_time - network_latency, the validator misses the slot "
                "even though their AI computation was correct. "
                "This penalizes computationally heavy validators via the Uₜ term."
            ),
            "root_cause": "ZKML proving time dominates combined overhead",
            "mitigation": "Asynchronous proof pre-computation; reduce circuit size via V-III mitigation",
            "severity": "High",
        },
        {
            "id": "FM-CD-2",
            "name": "Key Rotation Desynchronization",
            "description": (
                "ML-DSA keys rotate at epoch boundaries (IC-03). If the ZKML layer "
                "generates a proof that is signed with an expired key (wrong epoch), "
                "the signature is invalid (IC-04 FM-04a), the proof is rejected, "
                "and the validator is penalized — despite correct AI computation."
            ),
            "root_cause": "Tight coupling between epoch clock (L1), proof generation (L2), and key state (L3)",
            "mitigation": "Overlap window: accept proofs signed with key from epoch t-1 for grace_period slots",
            "severity": "Medium",
        },
        {
            "id": "FM-CD-3",
            "name": "Quantum-Safe Bootstrap Paradox",
            "description": (
                "Initial validator registration (IC-03) uses ML-KEM for session key establishment. "
                "But the on-chain registration transaction itself is published via classical channel. "
                "A harvest-now-decrypt-later adversary could intercept the initial registration "
                "and decrypt the session key when a quantum computer becomes available, "
                "compromising the validator's identity before ML-DSA protection kicks in."
            ),
            "root_cause": "Classical channel used for PQC key bootstrapping",
            "mitigation": "Use ML-KEM encapsulation within a PQC-authenticated channel; "
                          "or use a classical TLS + PQC hybrid for registration",
            "severity": "Low (future quantum threat, not classical)",
        },
        {
            "id": "FM-CD-4",
            "name": "ZKML-PQC Size Budget Overflow",
            "description": (
                "At high TPS (10,000+), the combined per-block payload is: "
                "n_validators × (proof_size + sig_size) = 100 × (200KB + 2.4KB) = ~20.2MB/block. "
                "This exceeds practical block size limits of most L1 networks (~1-5MB). "
                "This failure mode is UNIQUE to co-design and does not appear in single-layer analysis."
            ),
            "root_cause": "Multiplicative overhead: ZKML proof size × validator count × PQC signature size",
            "mitigation": "M1 (Aggregate signatures) + proof compression (Plonky2/FRI) + off-chain proof storage",
            "severity": "High at 10,000+ TPS",
        },
    ],

    "combined_overhead_model": {
        "description": "Per-block combined overhead at N=100 validators",
        "components": {
            "zkml_proof_bytes": 200_000,      # 200KB per validator proof
            "mldsa44_sig_bytes": 2_420,       # ML-DSA-44 signature
            "mldsa44_pk_bytes": 1_312,        # Public key (stored in registry, not per-block)
            "mlkem768_ct_bytes": 1_088,       # KEM ciphertext (epoch registration only)
        },
        "per_block_bytes_naive": 100 * (200_000 + 2_420),    # 20.24 MB
        "per_block_bytes_with_M1": 200_000 + 2_420,           # Single aggregate: ~202 KB
        "per_block_bytes_with_M3": 200_000 + (7 * 2_420),     # log2(100) ≈ 7 Merkle paths
    },
}


# =============================================================================
# MAIN
# =============================================================================

def run_codesign_analysis():
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    print("\n" + "="*65)
    print("  ARCHITECTURAL CO-DESIGN ANALYSIS — RQ4 & RQ5")
    print("="*65)

    print(f"\n[RQ4] Interface Contracts: {len(CONTRACTS)} defined")
    for c in CONTRACTS:
        print(f"\n  [{c.contract_id}] {c.caller_layer} → {c.callee_layer}: {c.operation}")
        print(f"    Preconditions : {len(c.preconditions)}")
        print(f"    Postconditions: {len(c.postconditions)}")
        print(f"    Failure modes : {len(c.failure_modes)}")
        print(f"    Max latency   : {c.max_latency_ms}ms")

    print(f"\n[RQ5] Emergent Security Properties: "
          f"{len(CODESIGN_INTERACTIONS['emergent_security_properties'])}")
    for esp in CODESIGN_INTERACTIONS["emergent_security_properties"]:
        print(f"\n  [{esp['id']}] {esp['name']}")
        print(f"    Present without co-design: {esp['present_without_codesign']}")
        print(f"    Benefit: {esp['security_benefit']}")

    print(f"\n[RQ5] Co-Design Failure Modes: "
          f"{len(CODESIGN_INTERACTIONS['failure_modes'])}")
    for fm in CODESIGN_INTERACTIONS["failure_modes"]:
        print(f"\n  [{fm['id']}] {fm['name']} [Severity: {fm['severity']}]")
        print(f"    Root cause  : {fm['root_cause'][:80]}...")
        print(f"    Mitigation  : {fm['mitigation'][:80]}...")

    # Combined overhead
    co = CODESIGN_INTERACTIONS["combined_overhead_model"]
    print(f"\n[Combined Overhead — N=100 validators per block]")
    print(f"  Naive (no mitigation) : {co['per_block_bytes_naive']/1e6:.2f} MB/block ⚠️")
    print(f"  With M1 (aggregate)   : {co['per_block_bytes_with_M1']/1e3:.1f} KB/block ✓")
    print(f"  With M3 (Merkle)      : {co['per_block_bytes_with_M3']/1e3:.1f} KB/block ✓")

    results = {
        "rq4_contracts": [asdict(c) for c in CONTRACTS],
        "rq5_analysis": CODESIGN_INTERACTIONS,
        "rq4_answer": (
            "4 formal interface contracts defined governing PoUI↔ZKML↔PQC integration. "
            "Contracts specify pre/postconditions, failure modes, data types, and "
            "performance budgets for each inter-layer operation."
        ),
        "rq5_answer": (
            "3 emergent security properties identified that arise ONLY from co-design: "
            "Proof-of-Identity Chain, Quantum-Safe AI Governance, and Layered Slash Amplification. "
            "4 co-design-specific failure modes identified: Proving-Slot Race Condition, "
            "Key Rotation Desynchronization, Quantum-Safe Bootstrap Paradox, and "
            "ZKML-PQC Size Budget Overflow (critical at 10,000+ TPS)."
        ),
    }

    out_path = out_dir / "codesign_analysis.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved: {out_path}")
    print("\n  → Next: Phase 6 — PRISMA Literature Review")
    return results


if __name__ == "__main__":
    run_codesign_analysis()
