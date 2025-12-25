# 🌊 Project Tsunami: DDoS Simulation & Mitigation Lab

**Project Tsunami** is a "Purple Team" cybersecurity lab designed to simulate a High-Concurrency Denial of Service (DoS) attack and demonstrate how to defend against it using application-layer Rate Limiting.

It features a custom **Victim Server**, an asynchronous **Flood Generator**, and a **Live Streamlit War Room** to visualize the attack traffic and defense efficacy in real-time.

---

## ⚠️ Disclaimer
**EDUCATIONAL PURPOSES ONLY.**
This code is designed to be run on `localhost` (127.0.0.1) or isolated lab environments. Do not use the flood generator against public servers, IP addresses you do not own, or without explicit permission. Doing so is illegal.

---

## 🏗 Architecture

The project consists of three distinct components running simultaneously:

1.  **The Victim (`victim.py`):**
    * A Flask server exposing a CPU-intensive endpoint (`/heavy`).
    * **Vulnerability:** Without protection, calculating `factorial(5000)` freezes the CPU.
    * **Defense:** Implements a "Sliding Window" Rate Limiter to block IPs exceeding 50 requests/10s.

2.  **The Storm (`flood_db.py`):**
    * An asynchronous attack script using `aiohttp` and `asyncio`.
    * Generates 3,000+ requests per second without waiting for replies.
    * Logs real-time attack results (Success vs. Blocked) to a SQLite database.

3.  **The War Room (`dashboard.py`):**
    * A Streamlit dashboard that acts as a Security Operations Center (SOC).
    * Visualizes the "Tipping Point" where the Firewall kicks in and traffic shifts from Green (Success) to Yellow (Blocked).

---

## 🛠 Tech Stack

* **Language:** Python 3.9+
* **Web Framework:** Flask
* **Async Network:** `aiohttp` / `asyncio`
* **Visualization:** Streamlit / Altair
* **Database:** SQLite3

---

## 🚀 Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/Project-Tsunami-DDoS-Lab.git](https://github.com/your-username/Project-Tsunami-DDoS-Lab.git)
    cd Project-Tsunami-DDoS-Lab
    ```

2.  Install dependencies:
    ```bash
    pip install flask aiohttp streamlit pandas altair
    ```

---

## ⚔️ How to Run the Simulation

This simulation requires **3 separate terminal windows** running at the same time.

### Terminal 1: The Victim Server (Blue Team)
Start the server that contains the Rate Limiting defense logic.
```bash
python victim.py
```
### Terminal 1: The Victim Server (Blue Team)
```bash
streamlit run dashboard.py
