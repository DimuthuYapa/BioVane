# BioVane: Micro-Climate & Shift Fatigue Anomaly Grid

BioVane is an advanced, privacy-preserving early warning system designed to protect outdoor, industrial, and logistics workforces (specifically in extreme heat regions like the GCC) from environmental and occupational health crises before they result in injury, severe heat stress, or operational downtime.

---

## 1. Core Architecture & Key Pillars

1. **Hyper-Local Micro-Climate Telemetry:**
   - Real-time weather and air quality via Open-Meteo API (ambient temperature, relative humidity, direct solar radiation, wind speed, PM2.5, PM10, and US-AQI).
   - Dynamic Liljegren / Stull Wet-Bulb Globe Temperature (WBGT) calculation with OSHA / ISO 7243 flag tiers (Green, Yellow, Red, Black Flag).
   - Micro-climate sector variations for industrial yards (e.g. logistics open asphalt vs heavy fabrication bay).

2. **Passive Workforce Operational Proxies:**
   - Aggregates non-invasive operational indicators: task cycle completion delays, scheduled break compliance rate, break deficit minutes, equipment idle pacing, and anonymized triage clinic chief complaints.

3. **Strict Privacy-Preserving Views:**
   - **$k$-Anonymity & Small-Cell Suppression:** Any cohort $< k$ (default $k=5$) suppresses granular metrics and clinic records.
   - **Differential Privacy:** Calibrated Laplace noise injection $Lap(0, \Delta f / \epsilon)$ on aggregated rates and counts.
   - Eliminates worker re-identification and guarantees zero disciplinary or individual tracking misuse.

4. **Explainable Anomaly Detection (Isolation Forest):**
   - Unsupervised Isolation Forest trained on nominal climate & shift operational states.
   - Feature contribution decomposition waterfall: explains *why* an alert triggered (e.g., *62% WBGT heat spike + 28% task cycle delay + 10% break deficit*).

5. **Actionable Decision Support:**
   - Role-specific protocols automatically routed to:
     - **Site Safety Supervisors:** Enforce mandatory 15m/30m shaded recovery cycles, hydration audits, buddy checks.
     - **Environmental Health Officers (EHO):** Deploy misting cannons, inspect chilled welfare refuge pods, audit N95 particulate PPE.
     - **Operations Managers:** Throttle crane throughput quotas by 20-30%, balance operator rotations, clear bottlenecks.

6. **Interactive Stress Simulation:**
   - Test acute events in real time: Nominal baseline, Acute Heatwave (+4.8°C), Shamal Dust Storm (+180 µg/m³), and Acute Fatigue Surge (+26% delay).

---

## 2. Quick Start

### Start the BioVane Application
Run the launcher from the project directory:
```bash
python start_server.py
```
Then open your browser:
- **Interactive Command Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive REST API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run Automated Unit & E2E Tests
```bash
# Run backend unit tests
python backend/run_tests.py

# Run end-to-end integration verification
python verify_e2e.py
```

---

## 3. Directory Layout

```
biovane/
├── README.md                     # Documentation & operational guide
├── start_server.py               # Launcher serving FastAPI + React frontend
├── verify_e2e.py                 # Automated end-to-end integration test suite
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── run_tests.py              # Unit test runner
│   ├── pytest.ini                # Pytest configuration
│   ├── app/
│   │   ├── main.py               # FastAPI application, routing, and static mounting
│   │   ├── models.py             # Pydantic schemas (Climate, Workforce, Anomaly, Directives)
│   │   ├── telemetry/
│   │   │   ├── climate.py        # Open-Meteo client, WBGT formulas, GCC presets
│   │   │   └── workforce.py      # Passive operational proxies generator
│   │   ├── privacy/
│   │   │   └── guard.py          # k-Anonymity & Laplace differential privacy
│   │   ├── engine/
│   │   │   └── anomaly_detector.py # Isolation Forest & explainability decomposition
│   │   └── decision/
│   │       └── rules.py          # ISO 7243 & OSHA role-based decision directives
│   └── tests/
│       ├── test_climate.py       # Weather, WBGT, and air quality tests
│       ├── test_privacy.py       # k-Anonymity and differential privacy tests
│       └── test_anomaly.py       # Isolation Forest and stress anomaly tests
└── frontend/
    ├── package.json              # React 18, Vite, Tailwind CSS, Lucide dependencies
    ├── vite.config.ts            # Vite build configuration & API proxy
    ├── tailwind.config.js        # Industrial dark theme design system
    ├── src/
    │   ├── main.tsx              # React mounting root
    │   ├── App.tsx               # Main Command Center UI orchestration
    │   ├── types.ts              # TypeScript interfaces
    │   └── components/
    │       ├── Header.tsx        # System status, GCC presets, threat badges
    │       ├── MicroClimateGrid.tsx # Zone selector, WBGT flags, environmental telemetry
    │       ├── WorkforceProxyMonitor.tsx # Shift cycle pacing, break compliance, triage
    │       ├── ExplainableAnomalyRadar.tsx # Threat meter, narrative summary, feature waterfall
    │       ├── DecisionSupportHub.tsx # Role-filtered actionable directive cards
    │       ├── PrivacyPreservingAudit.tsx # Side-by-side privacy audit & sliders
    │       └── SimulationController.tsx # Real-time heatwave & fatigue injector
    └── dist/                     # Optimized production build served by FastAPI
```
