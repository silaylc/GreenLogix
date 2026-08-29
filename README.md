# 🌍 GreenLogix: Sustainable Vehicle Routing & Decision Support System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Optimization](https://img.shields.io/badge/Optimization-Simulated_Annealing-0052CC?style=for-the-badge)

## 📌 Project Overview
GreenLogix is an engineering solution and decision support dashboard designed to optimize delivery routes by balancing operational efficiency, economic cost, environmental sustainability, and legal constraints[cite: 2]. Developed as a technical product, it addresses the Vehicle Routing Problem (VRP) under modern urban logistics conditions[cite: 2].

**Authors:** Satı Sıla Yolcu, Gökberk Kaan Tapan, Merve Kızılırmak[cite: 2].

## 🎯 Core Objectives & SDG Alignment
The project bridges the gap between advanced optimization methods and real-world delivery constraints[cite: 2]. It is directly aligned with the United Nations Sustainable Development Goals:
* **SDG 11 (Sustainable Cities and Communities):** Reduces unnecessary vehicle mileage and urban air pollution to support more planned movement of delivery fleets[cite: 2].
* **SDG 13 (Climate Action):** Integrates climate change measures by treating fuel consumption and estimated CO2 emissions as primary components of the route-determining stages[cite: 2].

## 🏗️ System Architecture & Technologies
GreenLogix features a modular, microservice-ready architecture separating data representation, fuel modeling, constraint validation, and optimization[cite: 2].
* **Core Implementation:** Python is utilized for rapid prototyping and mathematical implementation[cite: 2].
* **Dashboard Interface:** Streamlit provides an interactive logistics command center for route input and KPI visualization[cite: 2].
* **Mapping & Visualization:** Folium is used for interactive route, depot, and stop visualization on the map[cite: 2].
* **External APIs:** The system relies on Nominatim/OpenStreetMap for geocoding and OSRM for realistic route geometry and travel estimation[cite: 2].
* **Database Layer:** PostgreSQL is designed to handle the data model layer within the architecture[cite: 2].

## ⚙️ Optimization & Mathematical Model
Rather than treating routing as a pure shortest-path problem, GreenLogix evaluates candidate routes as a multi-factor engineering decision problem[cite: 2].
* **Algorithm:** The optimization engine utilizes Simulated Annealing, supplemented by 2-opt refinement and randomized search[cite: 2].
* **Load-Sensitive Fuel Model:** Fuel consumption is dynamically calculated based on the vehicle's baseline fuel rate, distance traveled, a load sensitivity coefficient (remaining cargo), and traffic factors[cite: 2].
* **Scoring Function:** The final route score is a weighted combination of total distance, total fuel consumption, CO2 emissions, and operational penalties[cite: 2].
* **Constraint Management:** The system rigorously evaluates routes against vehicle capacity, fuel availability, and continuous driving duration limits to ensure operational feasibility[cite: 2].

## 📊 Experimental Validation & Business Impact
Experimental results demonstrate that the GreenLogix optimization logic provides meaningful improvements over standard baseline delivery routes[cite: 2].
* **Distance Reduction:** Total travel distance was reduced by 1.69% in the simulated test scenario[cite: 2].
* **Sustainability Impact:** The optimized route reduced fuel consumption by 1.56% and carbon emissions by 1.53%[cite: 2].
* **Efficiency:** Overall travel time was improved by 1.35% while maintaining full operational feasibility with zero penalty costs[cite: 2].

## 🚀 How to Run the Project
1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/greenlogix-routing.git](https://github.com/YOUR_USERNAME/greenlogix-routing.git)
