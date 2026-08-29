"""
main.py – GreenLogix Demo
===========================
Demonstrates both the evaluation engine and the simple optimizer.

Part 1 – Manual evaluation:
    Evaluate two hand-crafted routes and compare their scores.

Part 2 – Optimizer:
    Let run_optimizer() generate and improve candidate routes automatically,
    then compare the best result against the manual routes.

Sample network  (5 nodes: depot + 4 customers)
-----------------------------------------------
    Node 0: Depot  (start / end)
    Node 1: Customer A  – 80 kg,  no time window
    Node 2: Customer B  – 50 kg,  must arrive before 45 min  (tight!)
    Node 3: Customer C  – 60 kg,  no time window
    Node 4: Customer D  – 70 kg,  no time window

Total demand: 260 kg  <  vehicle capacity 500 kg  (always feasible)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from model import Customer, Vehicle, Problem
from solver import evaluate_route
from optimizer import run_optimizer


# ---------------------------------------------------------------------------
# Problem definition
# ---------------------------------------------------------------------------

customers = {
    1: Customer(id=1, demand=80,  time_window=None,     service_time=5),
    2: Customer(id=2, demand=50,  time_window=(0, 45),  service_time=8),
    3: Customer(id=3, demand=60,  time_window=None,     service_time=5),
    4: Customer(id=4, demand=70,  time_window=None,     service_time=5),
}

vehicle = Vehicle(
    capacity=500,
    fuel_capacity=60,
    base_fuel_per_km=0.2,
    load_factor=0.01,
    average_speed_kmph=40.0,
    max_drive_minutes=240,
    break_duration=45,
    emission_factor=2.68,
)

#              0     1     2     3     4
distance_matrix = [
    [  0.0, 10.0, 15.0, 20.0, 25.0],
    [ 10.0,  0.0,  9.0, 14.0, 18.0],
    [ 15.0,  9.0,  0.0,  8.0, 12.0],
    [ 20.0, 14.0,  8.0,  0.0,  7.0],
    [ 25.0, 18.0, 12.0,  7.0,  0.0],
]

#              0     1     2     3     4
traffic_matrix = [
    [  1.0,  1.2,  1.0,  1.0,  1.0],
    [  1.2,  1.0,  1.1,  1.0,  1.0],
    [  1.0,  1.1,  1.0,  1.3,  1.0],
    [  1.0,  1.0,  1.3,  1.0,  1.0],
    [  1.0,  1.0,  1.0,  1.0,  1.0],
]

problem = Problem(
    customers=customers,
    vehicle=vehicle,
    distance_matrix=distance_matrix,
    traffic_matrix=traffic_matrix,
)


# ---------------------------------------------------------------------------
# Helper: pretty-print an EvaluationResult
# ---------------------------------------------------------------------------

def print_result(label: str, result) -> None:
    print(f"\n{'─'*58}")
    print(f"  {label}")
    if result.route:
        print(f"  Route : {result.route}")
    print(f"{'─'*58}")
    print(f"  Distance  : {result.total_distance:>8.2f}  km")
    print(f"  Fuel      : {result.total_fuel:>8.2f}  litres")
    print(f"  Emission  : {result.total_emission:>8.2f}  kg CO₂")
    print(f"  Time      : {result.total_time:>8.2f}  min")
    print(f"  Penalty   : {result.penalty:>8.2f}")
    print(f"  Score (↓) : {result.score:>8.4f}")
    print(f"  Feasible  : {'✓ Yes' if result.feasible else '✗ No'}")
    if result.violations:
        for v in result.violations:
            print(f"    ✗ {v}")


# ---------------------------------------------------------------------------
# Part 1 – Manual route evaluation
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "="*58)
    print("  GreenLogix  –  Part 1: Manual Evaluation")
    print("="*58)

    manual_routes = {
        "Route A  [0→1→2→3→4→0]": [0, 1, 2, 3, 4, 0],
        "Route B  [0→4→3→2→1→0]": [0, 4, 3, 2, 1, 0],
    }

    manual_results = {}
    for label, route in manual_routes.items():
        manual_results[label] = evaluate_route(route, problem)
        print_result(label, manual_results[label])

    best_manual = min(manual_results, key=lambda l: manual_results[l].score)

    # ---------------------------------------------------------------------------
    # Part 2 – Optimizer
    # ---------------------------------------------------------------------------

    print("\n\n" + "="*58)
    print("  GreenLogix  –  Part 2: Optimizer (random + 2-opt)")
    print("="*58)
    print("  Generating 30 random routes and improving with 2-opt…")

    optimizer_result = run_optimizer(
        problem,
        num_candidates=30,
        use_2opt=True,
        seed=42,           # fixed seed → reproducible results
    )

    print_result("Optimizer best route", optimizer_result)

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------

    print("\n" + "="*58)
    print("  Summary")
    print("="*58)
    print(f"  Best manual route : {best_manual}")
    print(f"    Score = {manual_results[best_manual].score:.4f}")
    print(f"  Optimizer result  : {optimizer_result.route}")
    print(f"    Score = {optimizer_result.score:.4f}")

    if optimizer_result.score < manual_results[best_manual].score:
        improvement = manual_results[best_manual].score - optimizer_result.score
        print(f"  → Optimizer improved score by {improvement:.4f}")
    else:
        print("  → Manual route matches or beats optimizer on this small problem.")
    print("="*58)
