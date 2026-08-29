# 🌍 GreenLogix: Sustainable Vehicle Routing & Decision Support Syste

## 📌 Project Overview
GreenLogix is an engineering solution and decision support dashboard designed to optimize delivery routes by balancing operational efficiency, economic cost, environmental sustainability, and legal constraints. Developed as a technical product, it addresses the Vehicle Routing Problem (VRP) under modern urban logistics conditions.

**Authors:** Satı Sıla Yolcu, Gökberk Kaan Tapan, Merve Kızılırmak

## 🎯 Core Objectives & SDG Alignment
The project bridges the gap between advanced optimization methods and real-world delivery constraints[cite: 2]. It is directly aligned with the United Nations Sustainable Development Goals:
* **SDG 11 (Sustainable Cities and Communities):** Reduces unnecessary vehicle mileage and urban air pollution to support more planned movement of delivery fleets.
* **SDG 13 (Climate Action):** Integrates climate change measures by treating fuel consumption and estimated CO2 emissions as primary components of the route-determining stages.

## 🏗️ System Architecture & Technologies
GreenLogix features a modular, microservice-ready architecture separating data representation, fuel modeling, constraint validation, and optimization.
* **Core Implementation:** Python is utilized for rapid prototyping and mathematical implementation.
* **Dashboard Interface:** Streamlit provides an interactive logistics command center for route input and KPI visualization.
* **Mapping & Visualization:** Folium is used for interactive route, depot, and stop visualization on the map.
* **External APIs:** The system relies on Nominatim/OpenStreetMap for geocoding and OSRM for realistic route geometry and travel estimation.
* **Database Layer:** PostgreSQL is designed to handle the data model layer within the architecture[cite: 2].

## ⚙️ Optimization & Mathematical Model
Rather than treating routing as a pure shortest-path problem, GreenLogix evaluates candidate routes as a multi-factor engineering decision problem.
* **Algorithm:** The optimization engine utilizes Simulated Annealing, supplemented by 2-opt refinement and randomized search.
* **Load-Sensitive Fuel Model:** Fuel consumption is dynamically calculated based on the vehicle's baseline fuel rate, distance traveled, a load sensitivity coefficient (remaining cargo), and traffic factors.
* **Scoring Function:** The final route score is a weighted combination of total distance, total fuel consumption, CO2 emissions, and operational penalties.
* **Constraint Management:** The system rigorously evaluates routes against vehicle capacity, fuel availability, and continuous driving duration limits to ensure operational feasibility.

## 📊 Experimental Validation & Business Impact
Experimental results demonstrate that the GreenLogix optimization logic provides meaningful improvements over standard baseline delivery routes.
* **Distance Reduction:** Total travel distance was reduced by 1.69% in the simulated test scenario.
* **Sustainability Impact:** The optimized route reduced fuel consumption by 1.56% and carbon emissions by 1.53%.
* **Efficiency:** Overall travel time was improved by 1.35% while maintaining full operational feasibility with zero penalty costs.


