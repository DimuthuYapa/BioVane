# Walkthrough: BioVane - Micro-Climate & Shift Fatigue Anomaly Grid

We have designed, implemented, and verified **BioVane: Micro-Climate & Shift Fatigue Anomaly Grid**, an early warning system designed to protect outdoor, industrial, and logistics workforces from heat stress, acute environmental hazards, and occupational fatigue before injury or downtime occurs.

---

## 1. System Overview & Architecture

BioVane fuses two signal streams into an explainable anomaly engine while preserving worker privacy:

```mermaid
flowchart TD
    subgraph Stream1 ["1. Micro-Climate Telemetry"]
        API["Open-Meteo Live API\n(GCC Presets: Dubai, SPARK, Mesaieed, KEZAD)"] --> ClimateEngine["Liljegren / Stull WBGT Calculation\nFlag Categories: Green / Yellow / Red / Black"]
        Sensors["Micro-Climate Zone Variations\n(Sectors A, B, C, D)"] --> ClimateEngine
    end

    subgraph Stream2 ["2. Operational Proxies & Privacy Shield"]
        Workforce["Passive Shift Proxies\n(Pacing Lag, Break Deficit, Machine Idle)"] --> PrivacyGuard["k-Anonymity Guard (k >= 5)\nSmall-Cell Suppression"]
        Triage["Clinic Health Logs"] --> PrivacyGuard
        PrivacyGuard --> DP["Differential Privacy Filter\nLaplace(0, Δf/ε) Noise"]
    end

    subgraph FusionEngine ["3. Anomaly Fusion & Explainability"]
        ClimateEngine --> IF["Isolation Forest Core"]
        DP --> IF
        IF --> Explain["Explainability Decomposition\nFeature Waterfall (% Contributions)"]
    end

    subgraph SupportHub ["4. Actionable Decision Support"]
        Explain --> Protocols["Occupational Standards Engine\n(ISO 7243 / OSHA / UAE MoHRE)"]
        Protocols --> Supervisor["Site Safety Supervisor Directives"]
        Protocols --> EHO["Environmental Health Officer Directives"]
        Protocols --> OpsMgr["Operations Manager Directives"]
    end

    subgraph UI ["5. Real-Time Command Center"]
        Supervisor --> Dashboard["React 18 + Tailwind Command UI"]
        EHO --> Dashboard
        OpsMgr --> Dashboard
        Explain --> Dashboard
    end
```

---

## 2. Changes Made & Files Created

The complete system was built in `C:\Users\3C Tech\biovane`:

### Backend Components (`biovane/backend`)
* [models.py](file:///C:/Users/3C%20Tech/biovane/backend/app/models.py): Pydantic schemas for micro-climate readings, workforce operational proxies, explainability vectors, anomaly reports, and decision directives.
* [climate.py](file:///C:/Users/3C%20Tech/biovane/backend/app/telemetry/climate.py): Live Open-Meteo weather and air quality API connector with Stull wet-bulb temperature, Liljegren WBGT calculation, flag categorizer (Normal, Green, Yellow, Red, Black Flag), and 4 GCC industrial zone presets (Dubai Industrial City, King Salman SPARK, Mesaieed MIC, KEZAD).
* [workforce.py](file:///C:/Users/3C%20Tech/biovane/backend/app/telemetry/workforce.py): Passive operational proxies engine generating shift pacing delays, break compliance rates, break deficit minutes, equipment idle time, and triage clinic logs.
* [guard.py](file:///C:/Users/3C%20Tech/biovane/backend/app/privacy/guard.py): Privacy guard enforcing $k$-anonymity ($k \ge 5$) with small-cell suppression and calibrated Laplace differential privacy noise ($Lap(0, \Delta f / \epsilon)$), guaranteeing zero individual worker identification.
* [anomaly_detector.py](file:///C:/Users/3C%20Tech/biovane/backend/app/engine/anomaly_detector.py): Isolation Forest anomaly detector with rolling baseline deviation tracking and explainability percentage decomposition.
* [rules.py](file:///C:/Users/3C%20Tech/biovane/backend/app/decision/rules.py): Actionable decision support engine generating role-targeted directives for Site Safety Supervisors, EHOs, and Operations Managers based on ISO 7243 and OSHA guidelines.
* [main.py](file:///C:/Users/3C%20Tech/biovane/backend/app/main.py): FastAPI application with REST endpoints (`/api/telemetry`, `/api/anomalies`, `/api/presets`, `/api/privacy/audit`, `/api/simulate`) and static mounting of the compiled React frontend.

### Frontend Command Center (`biovane/frontend`)
* [App.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/App.tsx): Real-time industrial command dashboard with live polling, zone selection, and active threat monitors.
* [Header.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/Header.tsx): Live grid status, active GCC preset switcher, privacy badge, and grid threat indicator.
* [MicroClimateGrid.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/MicroClimateGrid.tsx): Sector telemetry cards, WBGT gauges with flag tiers, ambient/apparent temperature, humidity, wind, solar radiation, and AQI/PM2.5.
* [WorkforceProxyMonitor.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/WorkforceProxyMonitor.tsx): Shift pacing variance, break compliance progress, break deficit minutes, and small-cell suppression status.
* [ExplainableAnomalyRadar.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/ExplainableAnomalyRadar.tsx): Isolation Forest score gauge (0 to 100), natural language headline, and factor contribution decomposition waterfall.
* [DecisionSupportHub.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/DecisionSupportHub.tsx): Role-filtered action cards (Supervisor / EHO / Operations) with 1-click Acknowledge and Execute actions.
* [PrivacyPreservingAudit.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/PrivacyPreservingAudit.tsx): Interactive inspector with $k$-anonymity and $\epsilon$-budget sliders, plus side-by-side verification table of raw vs privacy-shielded values.
* [SimulationController.tsx](file:///C:/Users/3C%20Tech/biovane/frontend/src/components/SimulationController.tsx): Interactive scenario injector (Nominal, Heatwave Spike, Shamal Dust Storm, Acute Fatigue Surge) and fine-tuning sliders.

### Project Utilities & Launchers
* [start_server.py](file:///C:/Users/3C%20Tech/biovane/start_server.py): Single-command launcher serving both API and UI on `http://127.0.0.1:8000`.
* [verify_e2e.py](file:///C:/Users/3C%20Tech/biovane/verify_e2e.py): End-to-end automated integration test suite.
* [README.md](file:///C:/Users/3C%20Tech/biovane/README.md): Comprehensive documentation and user manual.

---

## 3. Verification & Validation Results

### 1. Backend Unit Tests (`backend/run_tests.py`)
All 9 unit tests passed:
- `test_wet_bulb_temperature_calculation`: **PASSED** (Stull formula accuracy verified across 35°C-42°C ambient regimes).
- `test_wbgt_calculation_and_flags`: **PASSED** (Normal vs Black Flag threshold verified).
- `test_aqi_category_mapping`: **PASSED** (US-AQI categories from Good to Hazardous).
- `test_climate_collector_zones`: **PASSED** (Live Open-Meteo telemetry ingestion and sector interpolation verified).
- `test_k_anonymity_small_cell_suppression`: **PASSED** (Cohorts $< k=5$ have sensitive indicators suppressed).
- `test_differential_privacy_noise_bounds`: **PASSED** (Laplace noise distribution verified without value leaks).
- `test_audit_comparison_generation`: **PASSED** (Side-by-side audit generation verified).
- `test_anomaly_detector_nominal_conditions`: **PASSED** (Nominal conditions produce low anomaly scores).
- `test_anomaly_detector_acute_heat_and_fatigue`: **PASSED** (Heatwave and fatigue trigger high threat scores).

### 2. Frontend Production Build (`npm run build`)
- Vite production build succeeded in 27.6s with **0 errors**.
- Optimized bundles: `index.html` (1.15 kB), CSS (26.77 kB), JS (200.41 kB).

### 3. End-to-End System Integration (`verify_e2e.py`)
All 9 automated integration stages completed successfully:
1. API Health Check: **PASS**
2. GCC Presets (Dubai, SPARK, Mesaieed, KEZAD): **PASS**
3. Location Switching: **PASS**
4. Nominal Snapshots & Isolation Forest Scoring: **PASS**
5. Acute Heatwave Simulation (+4.8°C, WBGT surge): **PASS**
6. Explainable Narrative & Feature Waterfall Decomposition: **PASS** (e.g. 29.4% task delay contribution, 27.1% clinic triage contribution)
7. Role-Specific Action Directives Dispatch (Supervisor, EHO, Ops Manager): **PASS**
8. 1-Click Acknowledge and Execute State Transitions: **PASS**
9. Privacy Guard Audit & Small-Cell Suppression Verification: **PASS**
10. Compiled React Frontend UI Serving at `GET /`: **PASS**

---

## 4. How to Run

From `C:\Users\3C Tech\biovane`:
```bash
python start_server.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to interact with the full command-center grid.
