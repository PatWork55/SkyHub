# 🚁 SkyHub: AI-Driven eVTOL Vertiport Optimizer

**SkyHub** is a flexible systems engineering and Data Science framework designed to dimension the infrastructure of future drone taxi airports (eVTOL).

Using Monte Carlo simulations, it allows infrastructure planners to **input their specific market parameters** (traffic, costs, battery tech) and automatically identifies the configuration that maximizes profit while guaranteeing **zero accidents**.

---

## 🎯 Project Goal
The aviation industry faces a dilemma: building too small leads to lost revenue, while building too big kills profitability.
**SkyHub solves this optimization problem.** It is not a static model but a dynamic tool that adapts to:
* **Any Location:** From sleepy suburbs to busy metropolises.
* **Any Tech:** Current Li-Ion batteries or future solid-state tech.
* **Any Economy:** Adjust construction costs and ticket prices.

---

## 🚀 Key Feature: Realistic Pendular Traffic
Unlike standard simulations that use constant traffic rates, SkyHub simulates **Real-World Commuting Patterns**, revealing the critical logistical role of the infrastructure.

* **🌅 Morning Rush (07:00 - 09:00):** High Arrival / Low Departure.
    * *The Challenge:* The fleet accumulates at the hub. The algorithms test if the **Garage Capacity** acts as a sufficient buffer.
* **🌇 Evening Rush (17:00 - 19:00):** Low Arrival / High Departure.
    * *The Challenge:* The hub must rapidly deploy the stored fleet to meet the surge in outgoing taxi demand.

---

## 🛠️ Adapt to Your Reality (Configuration)
SkyHub is built to be a sandbox. All simulation parameters are centralized in `config.py` and can be modified to match your specific constraints.

**What you can customize:**
* **💸 Economics:** Update `COST_PAD_BUILD`, `REVENUE_PER_FLIGHT`, or `COST_CRASH_PENALTY` based on your local real estate market.
* **🔋 Physics:** Change `BATTERY_MAX`, `CONSUMPTION_PER_MIN`, or `CHARGE_RATE_PER_MIN` to simulate next-gen aircraft specifications.
* **📈 Traffic Profiles:** Modify `PROFILE_ARRIVAL` and `PROFILE_DEPARTURE` lists to simulate different cities (e.g., an airport shuttle service vs. a downtown commuting hub).

---

## 📊 Example Case Study: "Paris La Défense"
*Note: The results below are specific to the default parameters provided in the repository (High construction costs, intense asymmetric traffic).*

Running the optimizer on this specific scenario (28-day cycle) highlighted the importance of storage over charging capacity:

| Parameter | Optimized Result |
| :--- | :--- |
| **Charging Pads** | **8** |
| **Garage Spots** | **57** |
| **Net Monthly Profit** | **~326,700 €** |
| **Safety Score** | **100% (0 Crash)** |

**Insight:** For this specific scenario, the algorithm identified a high Garage-to-Pad ratio (7:1) as the most profitable structure to absorb the morning commuting wave. **Your results will vary based on your input parameters.**

---

## 🧠 System Architecture

### 1. Physical Layer (`evtol.py`)
Realistic physics simulation of electric drones (dynamic battery consumption, fast charging logic, mission priority).

### 2. Control Layer: Predictive ATC (`vertiport.py`)
An intelligent Air Traffic Controller that guarantees safety.
* **Predictive Access:** Calculates Estimated Time of Arrival (ETA) at a charger.
* **Safety Lock:** Denies entry if the estimated wait time exceeds the drone's safety buffer.

### 3. Optimization Layer: Smart Grid Search (`optimizer.py`)
* **Auto-Scaling:** The algorithm analyzes your traffic inputs to automatically deduce the relevant search space (using Little's Law).
* **Monte Carlo Engine:** Runs thousands of simulations to find the "Sweet Spot" between CAPEX and OPEX.

---

## 💻 Visualizer (Control Center)
The project includes a **Pygame-based Control Center** to visualize the simulation in real-time.
* **Real-time Metrics:** Monitors queue length, pad occupancy, and garage fill rates.
* **Dynamic Day/Night Cycle:** Displays current traffic load (IN/OUT percentages) changing over 24 hours.

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.x
* Pygame

### 1. Installation
```bash
pip install pygame 

### 2. Run the Optimizer
First, run the mathematical simulation to find the best configuration. This will generate a `best_params.json` file.
```bash
python3 optimizer.py

python3 simulation.py
