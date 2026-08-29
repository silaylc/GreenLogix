"""
fuel.py – GreenLogix Fuel & Emission Calculations
===================================================
Computes fuel consumption and CO₂ emissions for a single route leg.

Mathematical model
------------------
For each leg  i → j  the fuel consumed is:

    fuel(i,j) = base_fuel_per_km * d[i][j] * (1 + load_factor * current_load) * t[i][j]

where:
    base_fuel_per_km  = vehicle.base_fuel_per_km   (litres/km, default 0.2)
    d[i][j]           = distance_matrix[i][j]      (km)
    load_factor       = vehicle.load_factor         (0.01 per kg, set on Vehicle)
    current_load      = cargo weight on the truck when leaving node i  (kg)
    t[i][j]           = traffic_matrix[i][j]        (1.0 = free flow)

The term  (1 + vehicle.load_factor * current_load)  is the load multiplier:
    - At 0 kg load   →  multiplier = 1.0   (base consumption)
    - At 100 kg load →  multiplier = 2.0   (double the base)
    This means every extra kg of cargo adds 1 % more fuel per km.

CO₂ emissions for the same leg:

    emission(i,j) = fuel(i,j) * emission_factor

where:
    emission_factor = vehicle.emission_factor  (kg CO₂ per litre, default 2.68)
"""

from model import Vehicle


def fuel_for_segment(
    distance: float,
    current_load: float,
    vehicle: Vehicle,
    traffic: float = 1.0,
) -> float:
    """
    Compute fuel consumed (litres) for a single route leg.

    Formula
    -------
        fuel = base_fuel_per_km * distance * (1 + load_factor * current_load) * traffic

    Parameters
    ----------
    distance     : length of this leg from distance_matrix[i][j]  (km)
    current_load : cargo weight on the vehicle when leaving the origin node (kg)
    vehicle      : Vehicle definition (provides base_fuel_per_km and load_factor)
    traffic      : congestion multiplier from traffic_matrix[i][j]  (default 1.0)

    Returns
    -------
    Litres of fuel burned on this leg.
    """
    if distance < 0:
        raise ValueError(f"distance must be >= 0, got {distance}")
    if current_load < 0:
        raise ValueError(f"current_load must be >= 0, got {current_load}")
    if traffic <= 0:
        raise ValueError(f"traffic multiplier must be > 0, got {traffic}")

    load_multiplier = 1.0 + vehicle.load_factor * current_load
    return vehicle.base_fuel_per_km * distance * load_multiplier * traffic


def emission_for_segment(fuel_litres: float, vehicle: Vehicle) -> float:
    """
    Compute CO₂ emitted (kg) for a segment given the fuel consumed.

    Formula
    -------
        emission = fuel_litres * emission_factor

    Parameters
    ----------
    fuel_litres : litres of fuel burned on this segment
    vehicle     : Vehicle definition (provides emission_factor)

    Returns
    -------
    Kilograms of CO₂ emitted on this segment.
    """
    if fuel_litres < 0:
        raise ValueError(f"fuel_litres must be >= 0, got {fuel_litres}")

    return fuel_litres * vehicle.emission_factor
