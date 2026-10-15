"""
constraints.py – GreenLogix Constraint Checks & Penalty Values
===============================================================
Each function checks one constraint and returns a (penalty, message) pair.

    penalty = 0      → constraint is satisfied, no issue
    penalty > 0      → constraint is violated, penalty is added to the score

Hard constraints (large fixed penalty → route becomes infeasible):
    1. Vehicle capacity       − total demand > vehicle capacity  →  +10 000
    2. Fuel / battery limit   − total fuel consumed > tank size  →  +10 000
    3. Mandatory driver break − continuous driving > 240 min     →  +3 000

Soft constraint (per-minute penalty → route stays feasible but scores worse):
    4. Late delivery          − arrival after time_window latest →  +50 per late minute

These constants are the "simple fixed penalties" from the project spec.
"""

from model import Customer, Vehicle

# ---------------------------------------------------------------------------
# Penalty constants  (matching the project specification)
# ---------------------------------------------------------------------------
CAPACITY_PENALTY        = 10_000   # added when load exceeds vehicle capacity
FUEL_PENALTY            = 10_000   # added when fuel consumed exceeds tank size
BREAK_PENALTY           = 3_000    # added when mandatory break is missed
LATE_PENALTY_PER_MINUTE = 50       # added per minute of late arrival


# ---------------------------------------------------------------------------
# Hard Constraint 1 – Vehicle Capacity
# ---------------------------------------------------------------------------

def check_capacity(total_demand: float, vehicle: Vehicle):
    """
    Check that total cargo weight does not exceed the vehicle's capacity.

    Parameters
    ----------
    total_demand : sum of all customer demands on the route (kg)
    vehicle      : Vehicle definition

    Returns
    -------
    (penalty: float, message: str)
    penalty = CAPACITY_PENALTY if violated, 0 otherwise.
    """
    if total_demand > vehicle.capacity:
        msg = (
            f"CAPACITY VIOLATION: total demand {total_demand:.1f} kg "
            f"> vehicle capacity {vehicle.capacity:.1f} kg"
        )
        return CAPACITY_PENALTY, msg
    return 0, ""


# ---------------------------------------------------------------------------
# Hard Constraint 2 – Fuel / Battery Limit
# ---------------------------------------------------------------------------

def check_fuel(total_fuel: float, vehicle: Vehicle):
    """
    Check that total fuel consumed does not exceed the tank's capacity.

    Parameters
    ----------
    total_fuel : total litres consumed on the entire route
    vehicle    : Vehicle definition

    Returns
    -------
    (penalty: float, message: str)
    penalty = FUEL_PENALTY if violated, 0 otherwise.
    """
    if total_fuel > vehicle.fuel_capacity:
        msg = (
            f"FUEL VIOLATION: consumed {total_fuel:.2f} L "
            f"> tank capacity {vehicle.fuel_capacity:.1f} L"
        )
        return FUEL_PENALTY, msg
    return 0, ""


# ---------------------------------------------------------------------------
# Hard Constraint 3 – Mandatory Driver Break
# ---------------------------------------------------------------------------

def check_break(cumulative_drive_min: float, vehicle: Vehicle):
    """
    Check that the driver's continuous driving time has not exceeded the
    mandatory break threshold (vehicle.max_drive_minutes).

    If cumulative_drive_min > max_drive_minutes, a break was missed and
    BREAK_PENALTY is returned.  The solver calls this function whenever it
    detects the threshold has been crossed.

    Parameters
    ----------
    cumulative_drive_min : minutes driven continuously since the last break
                           (or since the start of the route)
    vehicle              : Vehicle definition (provides max_drive_minutes)

    Returns
    -------
    (penalty: float, message: str)
    penalty = BREAK_PENALTY if violated, 0 otherwise.
    """
    if cumulative_drive_min > vehicle.max_drive_minutes:
        msg = (
            f"BREAK VIOLATION: {cumulative_drive_min:.1f} min of continuous "
            f"driving exceeds the {vehicle.max_drive_minutes:.0f}-min limit"
        )
        return BREAK_PENALTY, msg
    return 0, ""


# ---------------------------------------------------------------------------
# Soft Constraint 4 – Late Delivery
# ---------------------------------------------------------------------------

def late_delivery_penalty(arrival_time: float, customer: Customer) -> float:
    """
    Compute the penalty for arriving at a customer after their time window.

    Formula
    -------
        penalty = max(0, arrival_time - latest) * LATE_PENALTY_PER_MINUTE

    Parameters
    ----------
    arrival_time : simulated arrival time at the customer (minutes from departure)
    customer     : Customer definition (provides time_window)

    Returns
    -------
    Penalty value ≥ 0.  Returns 0 if the customer has no time window or if
    the vehicle arrives on time.
    """
    if customer.time_window is None:
        return 0.0
    _, latest = customer.time_window
    late_minutes = max(0.0, arrival_time - latest)
    return late_minutes * LATE_PENALTY_PER_MINUTE
