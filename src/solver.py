"""
solver.py – GreenLogix Route Evaluator
========================================
Core function: evaluate_route(route, problem)

This module simulates driving a single route step-by-step and computes all
metrics.  There is NO optimisation here — that will come later (e.g. a
genetic algorithm).  The evaluator simply takes a given route and scores it.

Route format
------------
A route is a plain list of node IDs that starts and ends at node 0 (depot):
    [0, 3, 5, 2, 0]
Every intermediate node is a customer to visit.

Scoring formula  (weighted single-objective, lower is better)
-------------------------------------------------------------
    score = 0.4 * total_distance
          + 0.3 * total_fuel
          + 0.2 * total_emission
          + 0.1 * total_penalty

Because hard-constraint penalties are large (10 000 or 3 000), infeasible
routes naturally score far above feasible ones — the optimiser will avoid them.

Simulation loop
---------------
For each leg  route[k] → route[k+1]:
  1. Read distance  d  from distance_matrix[i][j].
  2. Read traffic multiplier  t  from traffic_matrix[i][j].
  3. Compute fuel burned on this leg; subtract from remaining_fuel.
  4. Compute CO₂ emitted from that fuel.
  5. Compute driving time  =  distance / speed.
   6. Accumulate drive time; if the break threshold is crossed,
      record a penalty and reset the continuous-drive counter.
  7. If the destination is a customer: check late-delivery penalty,
     add service time, and reduce the carried load by customer demand.

Before the loop:
  - Validate route structure, node existence, and no duplicate customers.
  - Check capacity immediately and add penalty if violated.

After the loop:
  8. Compute weighted score.
  9. Return EvaluationResult.
"""

"""
solver.py – GreenLogix Route Evaluator (Simulation Engine)
========================================================
CORE LOGIC: Step-by-Step Logistics Simulation
MÜHENDİSLİK GÖREVİ: Bir rotanın fiziksel ve yasal uygunluğunu (feasibility) denetlemek 
ve çevresel/maliyet skorunu hesaplamak.
"""

from typing import List
from model import EvaluationResult, Problem
from fuel import fuel_for_segment, emission_for_segment
from constraints import (
    check_capacity,
    check_break,
    late_delivery_penalty,
    FUEL_PENALTY,
)

# [TPM STRATEJİSİ: Ağırlıklı Karar Verme]
# Bu ağırlıklar, projenin "Sürdürülebilirlik" vizyonuna göre ayarlanmıştır.
# Yakıt ve Emisyon toplamda %50 ağırlığa sahiptir (Green Logistics Focus).
WEIGHT_DISTANCE = 0.4
WEIGHT_FUEL     = 0.3
WEIGHT_EMISSION = 0.2
WEIGHT_PENALTY  = 0.1

def evaluate_route(route: List[int], problem: Problem) -> EvaluationResult:
    """
    KOMUT: Rotayı Adım Adım Simüle Et.
    Bu fonksiyon bir rotayı sadece 'çizmez', o rotada sürüş yapılıyormuş gibi 
    yakıt tüketimini ve sürücü yorgunluğunu anlık takip eder.
    """

    vehicle = problem.vehicle
    speed_km_per_min = vehicle.average_speed_kmph / 60.0

    # ------------------------------------------------------------------
    # 1. ROTA DOĞRULAMA (Input Validation)
    # ------------------------------------------------------------------
    if len(route) < 2 or route[0] != 0 or route[-1] != 0:
        raise ValueError("Route must start and end at Depot (0).")

    customer_nodes = [n for n in route if n != 0]

    # ------------------------------------------------------------------
    # 2. BAŞLANGIÇ DURUMU (Initial State & Payload)
    # ------------------------------------------------------------------
    # [MÜHENDİSLİK DETAYI: Toplam Yük Hesaplama]
    # Araç depodan çıkarken tüm müşteri taleplerini yükleyerek yola çıkar.
    current_load: float = sum(problem.customers[cid].demand for cid in customer_nodes)

    # KAPASİTE DENETİMİ: Sürüş başlamadan önce aracın aşırı yüklenip yüklenmediği kontrol edilir.
    total_penalty: float = 0.0
    violations: List[str] = []
    feasible: bool = True

    cap_penalty, cap_msg = check_capacity(current_load, vehicle)
    if cap_penalty > 0:
        total_penalty += cap_penalty
        violations.append(cap_msg)
        feasible = False

    # Değişkenler: Mesafe, Yakıt, Zaman ve Sürücü Molası Takibi
    total_distance, total_fuel, total_emission, total_time = 0.0, 0.0, 0.0, 0.0
    remaining_fuel = vehicle.fuel_capacity
    drive_since_break = 0.0

    # ------------------------------------------------------------------
    # 3. SİMÜLASYON DÖNGÜSÜ (Leg-by-Leg Simulation)
    # ------------------------------------------------------------------
    # Her bir durak arası mesafe (leg) tek tek incelenir.
    for k in range(len(route) - 1):
        i, j = route[k], route[k+1]

        # MESAFE VE TRAFİK: Veri matrisinden o yola ait gerçek değerler okunur.
        distance = problem.distance_matrix[i][j]
        traffic = problem.traffic_matrix[i][j]
        total_distance += distance

        # [DİNAMİK YAKIT MODELİ: Yük Duyarlı Tüketim]
        # Araç her durakta hafiflediği için her bacakta yakıt tüketimi yeniden hesaplanır.
        # Bu, projenin en güçlü 'Gerçekçi Modelleme' özelliğidir.
        fuel = fuel_for_segment(distance, current_load, vehicle, traffic)
        total_fuel += fuel
        remaining_fuel -= fuel

        # YAKIT DENETİMİ: Deponun yolda bitip bitmediği kontrol edilir.
        if remaining_fuel < 0:
            total_penalty += FUEL_PENALTY
            violations.append(f"FUEL ALERT: Tank empty at leg {i}→{j}")
            feasible = False
            remaining_fuel = 0.0

        # EMİSYON HESABI: Tüketilen yakıtın anlık CO2 karşılığı.
        total_emission += emission_for_segment(fuel, vehicle)

        # ZAMAN TAKİBİ: Sürüş süresi = Mesafe / Ortalama Hız
        drive_time = distance / speed_km_per_min
        total_time += drive_time
        drive_since_break += drive_time

        # [HUKUKİ KISIT: Sürücü Mola Kuralı]
        # Sürekli sürüş süresi (max_drive_minutes) aşılırsa mola cezası uygulanır.
        if drive_since_break > vehicle.max_drive_minutes:
            brk_p, brk_m = check_break(drive_since_break, vehicle)
            total_penalty += brk_p
            violations.append(brk_m)
            feasible = False
            drive_since_break = 0.0 # Sürücü zorunlu mola verdi varsayılır

        # DURAK İŞLEMLERİ (Customer Arrival)
        if j != 0:
            customer = problem.customers[j]

            # GECİKME CEZASI (Soft Constraint): Zaman pencerelerine uyum kontrolü.
            penalty = late_delivery_penalty(total_time, customer)
            if penalty > 0:
                total_penalty += penalty
                violations.append(f"LATE DELIVERY at {j}: {penalty/50:.1f} min late")

            # SERVİS SÜRESİ: Boşaltma işlemi için geçen süre toplam zamana eklenir.
            total_time += customer.service_time

            # [DİNAMİK YÜK GÜNCELLEME]: Müşteriye teslimat yapıldı, araç hafifledi.
            current_load -= customer.demand

    # ------------------------------------------------------------------
    # 4. SKORLAMA VE ÇIKTI (Multi-Objective Scoring)
    # ------------------------------------------------------------------
    # Tüm kriterler ağırlıklandırılarak tek bir başarı puanı (Score) üretilir.
    score = (
        WEIGHT_DISTANCE  * total_distance
        + WEIGHT_FUEL    * total_fuel
        + WEIGHT_EMISSION * total_emission
        + WEIGHT_PENALTY  * total_penalty
    )

    return EvaluationResult(
        total_distance=round(total_distance, 2),
        total_fuel=round(total_fuel, 2),
        total_emission=round(total_emission, 2),
        total_time=round(total_time, 1),
        penalty=total_penalty,
        score=round(score, 2),
        feasible=feasible,
        violations=violations,
        route=route
    )