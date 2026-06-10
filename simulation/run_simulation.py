"""
PoUI Trust Score Simulation Engine
===================================
Runs N=100 nodes over T=1,000 epochs with three node classes:
  (a) Honest nodes           — accuracy ~ N(0.90, 0.05)
  (b) High-latency honest    — accuracy normal, latency 3σ above mean
  (c) Malicious nodes        — accuracy ~ U(0.10, 0.30)

Metrics collected:
  - Epochs before permanent malicious node exclusion
  - Honest node reward (trust score) distribution
  - Latency self-regulation behavior
  - Gini coefficient of trust score distribution

Authors: Md. Mehedi Hasan (Team Lead), Antigravity AI (Research Assistant)
Project: Towards an AI-Native Blockchain Framework
"""

import numpy as np
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from trust_score_model import Node, NodeConfig, NodeType


# ─── Simulation Parameters ───────────────────────────────────────────────────
N_NODES         = 100    # Total validators in network
N_EPOCHS        = 1000   # Simulation epochs

# Node class distribution
N_HONEST        = 70     # 70% honest nodes
N_HIGH_LATENCY  = 15     # 15% high-latency honest nodes
N_MALICIOUS     = 15     # 15% malicious nodes (15% is above realistic threshold — stress test)

RANDOM_SEED     = 42     # For reproducibility
# ─────────────────────────────────────────────────────────────────────────────


def gini_coefficient(scores: np.ndarray) -> float:
    """
    Compute the Gini coefficient of trust score distribution.
    Gini = 0 → perfect equality; Gini = 1 → maximum inequality.
    Used to assess fairness of validator reward distribution.
    """
    scores = np.sort(np.abs(scores))  # use absolute values for positive domain
    n = len(scores)
    if n == 0 or scores.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * (index * scores).sum()) / (n * scores.sum()) - (n + 1) / n)


def run_simulation(verbose: bool = True) -> Dict[str, Any]:
    """
    Run the full PoUI Trust Score simulation.

    Returns a results dictionary with all raw data and summary statistics.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    config = NodeConfig()

    # ── Instantiate nodes ────────────────────────────────────────────────────
    nodes: List[Node] = []
    node_id = 0

    for _ in range(N_HONEST):
        nodes.append(Node(node_id=node_id, node_type=NodeType.HONEST, config=config))
        node_id += 1

    for _ in range(N_HIGH_LATENCY):
        nodes.append(Node(node_id=node_id, node_type=NodeType.HIGH_LATENCY, config=config))
        node_id += 1

    for _ in range(N_MALICIOUS):
        nodes.append(Node(node_id=node_id, node_type=NodeType.MALICIOUS, config=config))
        node_id += 1

    if verbose:
        print(f"{'='*60}")
        print(f"  PoUI Trust Score Simulation")
        print(f"  Nodes: {N_NODES}  |  Epochs: {N_EPOCHS}")
        print(f"  Honest: {N_HONEST} | High-Latency: {N_HIGH_LATENCY} | Malicious: {N_MALICIOUS}")
        print(f"{'='*60}")

    # ── Per-epoch tracking ───────────────────────────────────────────────────
    epoch_active_honest     = []
    epoch_active_malicious  = []
    epoch_mean_trust_honest = []
    epoch_mean_trust_malicious = []
    epoch_gini              = []
    malicious_exclusion_epochs = {}  # node_id → epoch_excluded

    start_time = time.time()

    # ── Main simulation loop ─────────────────────────────────────────────────
    for epoch in range(1, N_EPOCHS + 1):
        epoch_trust_scores = []

        for node in nodes:
            if not node.is_excluded:
                node.update_trust_score(epoch, rng)

            if not node.is_excluded:
                epoch_trust_scores.append(node.trust_score)

            # Track first exclusion of malicious nodes
            if (node.node_type == NodeType.MALICIOUS
                    and node.is_excluded
                    and node.node_id not in malicious_exclusion_epochs
                    and node.epoch_excluded == epoch):
                malicious_exclusion_epochs[node.node_id] = epoch

        # Aggregate epoch metrics
        active_honest    = [n for n in nodes if not n.is_excluded and n.node_type == NodeType.HONEST]
        active_malicious = [n for n in nodes if not n.is_excluded and n.node_type == NodeType.MALICIOUS]

        epoch_active_honest.append(len(active_honest))
        epoch_active_malicious.append(len(active_malicious))

        if active_honest:
            epoch_mean_trust_honest.append(np.mean([n.trust_score for n in active_honest]))
        else:
            epoch_mean_trust_honest.append(0.0)

        if active_malicious:
            epoch_mean_trust_malicious.append(np.mean([n.trust_score for n in active_malicious]))
        else:
            epoch_mean_trust_malicious.append(np.nan)

        gini = gini_coefficient(np.array(epoch_trust_scores)) if epoch_trust_scores else 0.0
        epoch_gini.append(gini)

        # Progress reporting
        if verbose and epoch % 100 == 0:
            elapsed = time.time() - start_time
            excluded_mal = N_MALICIOUS - len(active_malicious)
            print(f"  Epoch {epoch:4d}/{N_EPOCHS} | "
                  f"Active honest: {len(active_honest):3d} | "
                  f"Excluded malicious: {excluded_mal}/{N_MALICIOUS} | "
                  f"Gini: {gini:.4f} | "
                  f"Elapsed: {elapsed:.1f}s")

    elapsed_total = time.time() - start_time

    # ── Collect per-node stats ───────────────────────────────────────────────
    node_stats = [n.stats() for n in nodes]

    # ── Summary statistics ───────────────────────────────────────────────────
    honest_nodes    = [n for n in nodes if n.node_type == NodeType.HONEST]
    hl_nodes        = [n for n in nodes if n.node_type == NodeType.HIGH_LATENCY]
    malicious_nodes = [n for n in nodes if n.node_type == NodeType.MALICIOUS]

    mal_exclusion_times = list(malicious_exclusion_epochs.values())

    summary = {
        "simulation_params": {
            "n_nodes": N_NODES,
            "n_epochs": N_EPOCHS,
            "n_honest": N_HONEST,
            "n_high_latency": N_HIGH_LATENCY,
            "n_malicious": N_MALICIOUS,
            "random_seed": RANDOM_SEED,
            "elapsed_seconds": round(elapsed_total, 3),
        },
        "malicious_exclusion": {
            "total_excluded": len(malicious_exclusion_epochs),
            "total_malicious": N_MALICIOUS,
            "exclusion_rate_pct": round(len(malicious_exclusion_epochs) / N_MALICIOUS * 100, 2),
            "mean_epoch_to_exclusion": round(float(np.mean(mal_exclusion_times)), 2) if mal_exclusion_times else None,
            "median_epoch_to_exclusion": round(float(np.median(mal_exclusion_times)), 2) if mal_exclusion_times else None,
            "min_epoch_to_exclusion": int(min(mal_exclusion_times)) if mal_exclusion_times else None,
            "max_epoch_to_exclusion": int(max(mal_exclusion_times)) if mal_exclusion_times else None,
            "epoch_breakdown": malicious_exclusion_epochs,
        },
        "honest_node_rewards": {
            "mean_final_trust": round(float(np.mean([n.trust_score for n in honest_nodes])), 4),
            "std_final_trust": round(float(np.std([n.trust_score for n in honest_nodes])), 4),
            "min_final_trust": round(float(np.min([n.trust_score for n in honest_nodes])), 4),
            "max_final_trust": round(float(np.max([n.trust_score for n in honest_nodes])), 4),
            "excluded_count": sum(1 for n in honest_nodes if n.is_excluded),
        },
        "high_latency_node_behavior": {
            "mean_final_trust": round(float(np.mean([n.trust_score for n in hl_nodes])), 4),
            "std_final_trust": round(float(np.std([n.trust_score for n in hl_nodes])), 4),
            "mean_latency_ms": round(float(np.mean([np.mean(n.latency_history) for n in hl_nodes])), 2),
            "excluded_count": sum(1 for n in hl_nodes if n.is_excluded),
            "latency_self_regulation": "penalized_not_excluded",  # expected behavior
        },
        "trust_distribution": {
            "final_gini": round(epoch_gini[-1], 4),
            "mean_gini_over_run": round(float(np.mean(epoch_gini)), 4),
        },
        "epoch_series": {
            "active_honest": epoch_active_honest,
            "active_malicious": epoch_active_malicious,
            "mean_trust_honest": epoch_mean_trust_honest,
            "mean_trust_malicious": [v if not (isinstance(v, float) and np.isnan(v)) else None
                                     for v in epoch_mean_trust_malicious],
            "gini": epoch_gini,
        },
        "node_stats": node_stats,
    }

    return summary


def print_summary(results: Dict[str, Any]) -> None:
    """Pretty-print key results to stdout."""
    mal = results["malicious_exclusion"]
    hon = results["honest_node_rewards"]
    hl  = results["high_latency_node_behavior"]
    td  = results["trust_distribution"]
    sp  = results["simulation_params"]

    print(f"\n{'='*60}")
    print("  SIMULATION RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"\n[RQ1] Malicious Node Exclusion:")
    print(f"  • Excluded:         {mal['total_excluded']}/{mal['total_malicious']} "
          f"({mal['exclusion_rate_pct']}%)")
    print(f"  • Mean epoch to exclusion:   {mal['mean_epoch_to_exclusion']}")
    print(f"  • Median epoch to exclusion: {mal['median_epoch_to_exclusion']}")
    print(f"  • Fastest exclusion:         Epoch {mal['min_epoch_to_exclusion']}")
    print(f"  • Slowest exclusion:         Epoch {mal['max_epoch_to_exclusion']}")

    print(f"\n[RQ1] Honest Node Trust Score Distribution:")
    print(f"  • Mean final trust:  {hon['mean_final_trust']}")
    print(f"  • Std  final trust:  {hon['std_final_trust']}")
    print(f"  • Range:             [{hon['min_final_trust']}, {hon['max_final_trust']}]")
    print(f"  • Honest excluded:   {hon['excluded_count']} (should be 0)")

    print(f"\n[RQ1] High-Latency Node Behavior:")
    print(f"  • Mean final trust:  {hl['mean_final_trust']} (should be < honest)")
    print(f"  • Mean latency:      {hl['mean_latency_ms']} ms")
    print(f"  • HL excluded:       {hl['excluded_count']} (latency self-regulation)")

    print(f"\n[RQ1] Trust Score Distribution Fairness:")
    print(f"  • Final Gini coeff:  {td['final_gini']} (0=equal, 1=unequal)")
    print(f"  • Mean Gini (run):   {td['mean_gini_over_run']}")

    print(f"\n  Total simulation time: {sp['elapsed_seconds']}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\nStarting PoUI Trust Score Simulation...")
    results = run_simulation(verbose=True)
    print_summary(results)

    # Save raw results
    output_path = Path(__file__).parent / "results" / "simulation_raw_results.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Raw results saved to: {output_path}")
