"""
optimizer.py – GreenLogix Strategic Optimizer
=============================================
STRATEGY: Multi-Start Local Search (2-opt)
MÜHENDİSLİK GÖREVİ: Binlerce olasılık arasından en düşük emisyonlu ve 
en yüksek verimliliğe sahip rotayı iteratif olarak keşfetmek.
"""

import random
from typing import List, Optional
from model import Problem, EvaluationResult
from solver import evaluate_route

# ---------------------------------------------------------------------------
# 1. ADIM: ROTA ÜRETİMİ (Random Initialization)
# ---------------------------------------------------------------------------

def generate_random_route(customer_ids: List[int], rng: random.Random) -> List[int]:
    """
    KOMUT: Rastgele Başlangıç Noktası Üret.
    Algoritmanın yerel minimumlara takılmaması için farklı başlangıç noktaları oluşturur.
    """
    order = customer_ids[:]
    rng.shuffle(order)
    return [0] + order + [0] # Depo ile başlar ve biter

# ---------------------------------------------------------------------------
# 2. ADIM: 2-OPT YEREL ARAMA (Iterative Improvement)
# ---------------------------------------------------------------------------

def two_opt_swap(route: List[int], i: int, j: int) -> List[int]:
    """
    KOMUT: 2-opt Değişimi.
    Rotadaki iki kenarı kesip aradaki segmenti ters çevirerek düğümleri yeniden bağlar.
    [0, 1, 2, 3, 4, 0] -> i=1, j=3 -> [0, 3, 2, 1, 4, 0]
    """
    return route[:i] + route[i:j + 1][::-1] + route[j + 1:]



def improve_with_2opt(route: List[int], problem: Problem) -> List[int]:
    """
    ALGORİTMİK MANTIK: Greedy Hill Climbing.
    Sürekli olarak mevcut rotadan daha iyi (düşük skorlu) bir komşu rota arar.
    Skor; mesafe, yakıt, emisyon ve cezaların ağırlıklı toplamıdır.
    """
    best_route = route
    # solver.py içindeki evaluate_route fonksiyonunu kullanarak rotayı puanlar
    best_score = evaluate_route(best_route, problem).score

    improved = True
    while improved:
        improved = False
        # Depo noktalarına (baş ve son) dokunmadan iç noktaları optimize eder
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                candidate = two_opt_swap(best_route, i, j)
                score = evaluate_route(candidate, problem).score
                
                # Eğer yeni skor daha iyiyse (düşükse), bu rotayı yeni standart yap
                if score < best_score:
                    best_route = candidate
                    best_score = score
                    improved = True 
    return best_route

# ---------------------------------------------------------------------------
# 3. ADIM: ANA OPTİMİZASYON DÖNGÜSÜ (Master Controller)
# ---------------------------------------------------------------------------

def run_optimizer(
    problem: Problem,
    num_candidates: int = 30,
    use_2opt: bool = True,
    seed: Optional[int] = None,
) -> EvaluationResult:
    """
    STRATEJİ: Global Optimizasyon.
    Belirlenen sayıda (num_candidates) rastgele rotayı üretir, her birini 
    yerel arama ile mükemmelleştirir ve aralarından 'En Yeşil' olanı seçer.
    """
    if not problem.customers:
        # Müşteri yoksa sadece depoda duran bir rota döndürür
        return evaluate_route([0, 0], problem)

    rng = random.Random(seed)
    customer_ids = list(problem.customers.keys())
    best_result: Optional[EvaluationResult] = None

    # [MÜHENDİSLİK KARARI: Multi-Start Search]
    # Tek bir deneme yerine çoklu aday üzerinden gitmek, en iyi sonuca ulaşma ihtimalini artırır.
    for _ in range(num_candidates):
        # 1. Başla
        route = generate_random_route(customer_ids, rng)

        # 2. İyileştir (2-opt yerel arama)
        if use_2opt:
            route = improve_with_2opt(route, problem)

        # 3. Değerlendir
        result = evaluate_route(route, problem)

        # 4. En iyiyi hafızada tut
        if best_result is None or result.score < best_result.score:
            best_result = result

    return best_result