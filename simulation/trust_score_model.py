"""
Trust Score Model for Proof of Useful Intelligence (PoUI) Consensus
====================================================================
Implements the core Trust Score formula:

    Tₜ = α · Aₜ² × e^(−λLₜ) + β · ln(Uₜ) − γ · Sₜ

Authors: Md. Mehedi Hasan (Team Lead), Antigravity AI (Research Assistant)
Project: Towards an AI-Native Blockchain Framework
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum


class NodeType(Enum):
    HONEST = "honest"
    HIGH_LATENCY = "high_latency"
    MALICIOUS = "malicious"


@dataclass
class NodeConfig:
    """Hyperparameters for the Trust Score network."""
    # Governance weight coefficients
    alpha: float = 0.5      # Weight for AI inference accuracy term
    beta: float = 0.3       # Weight for uptime logarithm term
    gamma: float = 1.5      # Weight for slash penalty term

    # Latency decay constant (higher = stricter latency penalty)
    lambda_decay: float = 0.01

    # Honest node accuracy distribution
    accuracy_mean: float = 0.90
    accuracy_std: float = 0.05

    # Latency baseline (ms)
    latency_mean: float = 50.0
    latency_std: float = 10.0

    # Malicious node accuracy range
    malicious_acc_min: float = 0.10
    malicious_acc_max: float = 0.30

    # High latency multiplier
    high_latency_multiplier: float = 3.0

    # Exclusion threshold: node excluded if Trust Score drops below this
    # Calibrated: honest nodes score ~0.20–0.38; malicious nodes score ~-0.05
    # after slash accumulation, they drop below threshold
    exclusion_threshold: float = -0.5

    # Uptime window (epochs to track)
    uptime_window: int = 50


@dataclass
class Node:
    """
    Represents a validator node in the PoUI consensus network.

    Each node maintains its own Trust Score history, accuracy history,
    latency history, and slash record.
    """
    node_id: int
    node_type: NodeType
    config: NodeConfig

    trust_score: float = 0.5         # Initial neutral trust score
    cumulative_uptime_ratio: float = 1.0
    is_excluded: bool = False
    epoch_excluded: int = -1

    # History tracking
    trust_history: List[float] = field(default_factory=list)
    accuracy_history: List[float] = field(default_factory=list)
    latency_history: List[float] = field(default_factory=list)
    slash_history: List[int] = field(default_factory=list)
    epochs_online: int = 0
    total_epochs: int = 0

    def sample_accuracy(self, rng: np.random.Generator) -> float:
        """Sample AI inference accuracy for this epoch."""
        if self.node_type == NodeType.MALICIOUS:
            return float(rng.uniform(
                self.config.malicious_acc_min,
                self.config.malicious_acc_max
            ))
        else:
            # Honest nodes: Gaussian with clipping to [0, 1]
            acc = rng.normal(self.config.accuracy_mean, self.config.accuracy_std)
            return float(np.clip(acc, 0.0, 1.0))

    def sample_latency(self, rng: np.random.Generator) -> float:
        """Sample network latency for this epoch (ms)."""
        base_latency = rng.normal(self.config.latency_mean, self.config.latency_std)
        base_latency = max(1.0, base_latency)  # latency ≥ 1ms

        if self.node_type == NodeType.HIGH_LATENCY:
            # High-latency nodes: 3x standard deviation above mean
            extra = self.config.high_latency_multiplier * self.config.latency_std
            return float(base_latency + extra)
        return float(base_latency)

    def detect_slash(self, accuracy: float, rng: np.random.Generator, threshold: float = 0.40) -> int:
        """
        Slash detection: probabilistic auditing model.
        - Malicious nodes are detected with p=0.35 per epoch when acc < threshold.
        - Honest nodes are never slashed (false-positive rate = 0).
        Returns 1 if slashed, 0 otherwise.
        Note: In a real system this uses cryptographic ZKP-based proofs.
        """
        if self.node_type == NodeType.MALICIOUS and accuracy < threshold:
            # Probabilistic detection — models real-world auditing pipeline delay
            detection_prob = 0.35
            return int(rng.random() < detection_prob)
        return 0

    def update_trust_score(self, epoch: int, rng: np.random.Generator) -> float:  # noqa: E501
        """
        Compute and update Trust Score using the PoUI formula:

            Tₜ = α · Aₜ² × e^(−λLₜ) + β · ln(Uₜ) − γ · Sₜ

        Returns the new Trust Score.
        """
        if self.is_excluded:
            return self.trust_score

        cfg = self.config
        self.total_epochs += 1
        self.epochs_online += 1

        # Sample observables
        A_t = self.sample_accuracy(rng)
        L_t = self.sample_latency(rng)
        S_t = self.detect_slash(A_t, rng)

        # Update uptime ratio over sliding window
        window = min(self.total_epochs, cfg.uptime_window)
        self.cumulative_uptime_ratio = self.epochs_online / self.total_epochs

        # Protect ln(0) — uptime ratio ∈ (0, 1]
        U_t = max(self.cumulative_uptime_ratio, 1e-9)

        # ===== TRUST SCORE FORMULA =====
        accuracy_term = cfg.alpha * (A_t ** 2) * np.exp(-cfg.lambda_decay * L_t)
        uptime_term   = cfg.beta  * np.log(U_t)
        slash_term    = cfg.gamma * S_t
        # ================================

        T_t = accuracy_term + uptime_term - slash_term

        # Record history
        self.trust_score = T_t
        self.trust_history.append(T_t)
        self.accuracy_history.append(A_t)
        self.latency_history.append(L_t)
        self.slash_history.append(S_t)

        # Check exclusion threshold
        if T_t < cfg.exclusion_threshold and not self.is_excluded:
            self.is_excluded = True
            self.epoch_excluded = epoch

        return T_t

    def stats(self) -> dict:
        """Return summary statistics for this node."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "final_trust_score": self.trust_score,
            "mean_trust_score": float(np.mean(self.trust_history)) if self.trust_history else 0.0,
            "std_trust_score": float(np.std(self.trust_history)) if self.trust_history else 0.0,
            "mean_accuracy": float(np.mean(self.accuracy_history)) if self.accuracy_history else 0.0,
            "mean_latency_ms": float(np.mean(self.latency_history)) if self.latency_history else 0.0,
            "total_slashes": int(sum(self.slash_history)),
            "is_excluded": self.is_excluded,
            "epoch_excluded": self.epoch_excluded,
        }
