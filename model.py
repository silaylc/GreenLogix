"""
model.py – GreenLogix Data Models
==================================
Defines the data structures used throughout the evaluation engine.

Route representation
--------------------
A route is a plain Python list of node IDs, starting and ending at 0:
    [0, 3, 5, 2, 0]
Node 0 is always the depot.  Customer nodes are integers ≥ 1.

Input structure
---------------
All problem data (customers, vehicle, matrices) lives in a single Problem
object so every function only needs to receive one argument.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------

@dataclass
class Customer:
    """
    One delivery stop.  Node IDs must match the row/column indices of the
    distance and traffic matrices defined in Problem.

    Fields
    ------
    id           : unique integer ≥ 1 (0 is reserved for the depot)
    demand       : cargo weight to deliver at this stop (kg)
    time_window  : (earliest, latest) arrival in minutes from route start,
                   or None if there is no time constraint
    service_time : minutes needed to unload at this stop
    """
    id: int
    demand: float
    lat: float = 0.0  # Harita çizimi için eklendi
    lon: float = 0.0  # Harita çizimi için eklendi
    time_window: Optional[Tuple[float, float]] = None
    service_time: float = 5.0


# ---------------------------------------------------------------------------
# Vehicle
# ---------------------------------------------------------------------------

@dataclass
class Vehicle:
    """
    Vehicle specification (homogeneous fleet → every vehicle is identical).

    Default values follow the project parameter sheet:
        base_fuel_per_km  = 0.2   litres / km  (empty vehicle)
        emission_factor   = 2.68  kg CO₂ / litre  (diesel)
        break threshold   = 240   minutes  (~4 h)

    Fields
    ------
    capacity          : max cargo weight (kg)
    fuel_capacity     : tank size (litres)
    fuel_consumption  : base fuel rate, litres/km at zero load
    max_drive_minutes : continuous-drive limit before a mandatory break
    break_duration    : required break length (minutes)
    emission_factor   : kg of CO₂ emitted per litre of fuel
    """
    capacity: float           = 500.0
    fuel_capacity: float      = 60.0
    base_fuel_per_km: float   = 0.2    # litres / km  (base, empty vehicle)
    load_factor: float        = 0.01   # extra litres per km per kg of cargo
    average_speed_kmph: float = 40.0   # km/h – used to convert distance → time
    max_drive_minutes: float  = 240.0  # minutes before mandatory break
    break_duration: float     = 45.0   # minutes
    emission_factor: float    = 2.68   # kg CO₂ per litre of diesel


# ---------------------------------------------------------------------------
# Problem  –  the single input container
# ---------------------------------------------------------------------------

@dataclass
class Problem:
    """
    Everything the evaluator needs, in one place.

    Fields
    ------
    customers       : dict mapping node_id → Customer  (IDs start at 1;
                      node 0 is the depot and needs no Customer entry)
    vehicle         : Vehicle specification (one vehicle, homogeneous fleet)
    distance_matrix : distance_matrix[i][j] = km from node i to node j.
                      Size: (n+1) × (n+1) where n = number of customers.
                      Index 0 = depot, indices 1..n = customer nodes.
    traffic_matrix  : traffic_matrix[i][j] = fuel multiplier for leg i→j.
                      1.0 = free flow.  1.3 = 30 % extra fuel (congestion).
                      Same shape as distance_matrix.
    """
    customers: Dict[int, "Customer"]
    vehicle: "Vehicle"
    distance_matrix: List[List[float]]
    traffic_matrix: List[List[float]]


# ---------------------------------------------------------------------------
# EvaluationResult  –  returned by evaluate_route() in solver.py
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    """
    Structured output of the route evaluator.

    Fields
    ------
    total_distance : total km driven on the route
    total_fuel     : total litres consumed
    total_emission : total kg of CO₂ emitted
    total_time     : total elapsed time (driving + service + any break) in minutes
    penalty        : accumulated penalty score (hard violations + late delivery)
    score          : weighted objective  =  0.4·d + 0.3·f + 0.2·e + 0.1·p
                     Lower is better.
    feasible       : True only when no hard constraint is violated
    violations     : human-readable list of every constraint breach found
    """
    total_distance: float = 0.0
    total_fuel: float     = 0.0
    total_emission: float = 0.0
    total_time: float     = 0.0
    penalty: float        = 0.0
    score: float          = 0.0
    feasible: bool        = True
    violations: List[str] = field(default_factory=list)
    route: List[int]      = field(default_factory=list)  # the evaluated route (for debugging)
