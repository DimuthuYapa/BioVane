import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from fastapi import Depends
from app.security.users import authenticate_user
from app.security.tokens import create_access_token, verify_access_token



from app.models import (
    ZoneSnapshot,
    SimulationConfig,
    LocationPreset
)
from app.telemetry.climate import ClimateCollector, GCC_PRESETS
from app.telemetry.workforce import WorkforceProxyCollector
from app.privacy.guard import PrivacyGuard
from app.engine.anomaly_detector import BioVaneAnomalyDetector
from app.decision.rules import DecisionSupportEngine
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )

    return {
       "username": username,
      "role": payload.get("role")
}




def require_role(allowed_roles: list):
    def role_checker(current_user: dict = Depends(get_current_user)):

        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this resource"
            )
        return current_user

    return role_checker

app = FastAPI(
    title="BioVane: Micro-Climate & Shift Fatigue Anomaly Grid API",
    description="Privacy-preserving occupational health & micro-climate fusion engine.",
    version="1.0.0"
)

# Enable CORS for local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State initialization
climate_collector = ClimateCollector(preset_key="dubai_industrial")
workforce_collector = WorkforceProxyCollector()
privacy_guard = PrivacyGuard(k_threshold=5, epsilon=1.0)
anomaly_detector = BioVaneAnomalyDetector()
decision_engine = DecisionSupportEngine()

simulation_state = SimulationConfig(active_scenario="NORMAL")
directive_status_registry: Dict[str, str] = {}
class LoginPayload(BaseModel):
    username: str
    password: str

class PrivacyConfigPayload(BaseModel):
    k_threshold: int
    epsilon: float

class DirectiveUpdatePayload(BaseModel):
    status: str  # "ACKNOWLEDGED", "COMPLETED"

class PresetSelectPayload(BaseModel):
    preset_id: str
@app.post("/api/login")
def login(payload: LoginPayload):
    user = authenticate_user(
        payload.username,
        payload.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
    {
        "sub": user["username"],
        "role": user["role"]
    }
)


    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "BioVane Fusion Grid",
        "location": climate_collector.preset.name,
        "active_scenario": simulation_state.active_scenario,
        "k_anonymity": privacy_guard.k_threshold,
        "epsilon_budget": privacy_guard.epsilon
    }

@app.get("/api/presets", response_model=List[LocationPreset])
def get_location_presets():
    return list(GCC_PRESETS.values())

@app.post("/api/presets/select")
def select_location_preset(payload: PresetSelectPayload):
    if payload.preset_id not in GCC_PRESETS:
        raise HTTPException(status_code=400, detail="Invalid preset ID")
    climate_collector.set_location(payload.preset_id)
    return {"message": f"Active location switched to {climate_collector.preset.name}", "preset": climate_collector.preset}

@app.get("/api/snapshots", response_model=List[ZoneSnapshot])
def get_snapshots():
    # 1. Collect micro-climate telemetry with simulation offsets
    climate_readings = climate_collector.get_zone_readings(
        heat_spike_delta=simulation_state.heat_spike_delta_c,
        dust_surge=simulation_state.dust_surge_ugm3
    )

    wbgt_lookup = {r.zone_id: r.wbgt_c for r in climate_readings}

    # 2. Collect raw workforce operational proxies
    raw_workforce = workforce_collector.get_raw_proxies(
        heat_wbgt_impact=wbgt_lookup,
        fatigue_delay_delta=simulation_state.fatigue_delay_delta_pct,
        break_compliance_drop=simulation_state.break_compliance_drop_pct,
        clinic_surge=simulation_state.clinic_triage_surge
    )

    # 3. Apply privacy shield (k-anonymity & differential privacy)
    shielded_workforce = privacy_guard.apply_privacy_shield(raw_workforce)

    # 4. Run explainable anomaly detection and decision rules per zone
    snapshots: List[ZoneSnapshot] = []

    for climate, workforce in zip(climate_readings, shielded_workforce):
        anomaly = anomaly_detector.evaluate_zone(climate, workforce)
        directives = decision_engine.generate_directives(climate, workforce, anomaly)

        # Restore any overridden acknowledged/completed status from registry
        for d in directives:
            if d.id in directive_status_registry:
                d.status = directive_status_registry[d.id]

        snapshots.append(
            ZoneSnapshot(
                zone_id=climate.zone_id,
                zone_name=climate.zone_name,
                climate=climate,
                workforce=workforce,
                anomaly=anomaly,
                directives=directives
            )
        )

    return snapshots

@app.get("/api/privacy/audit")
def get_privacy_audit(
    current_user: dict = Depends(require_role(["admin"]))
):


    climate_readings = climate_collector.get_zone_readings(
        heat_spike_delta=simulation_state.heat_spike_delta_c,
        dust_surge=simulation_state.dust_surge_ugm3
    )
    wbgt_lookup = {r.zone_id: r.wbgt_c for r in climate_readings}
    raw_workforce = workforce_collector.get_raw_proxies(
        heat_wbgt_impact=wbgt_lookup,
        fatigue_delay_delta=simulation_state.fatigue_delay_delta_pct,
        break_compliance_drop=simulation_state.break_compliance_drop_pct,
        clinic_surge=simulation_state.clinic_triage_surge
    )
    shielded_workforce = privacy_guard.apply_privacy_shield(raw_workforce)

    return {
        "k_threshold": privacy_guard.k_threshold,
        "epsilon_budget": privacy_guard.epsilon,
        "explanation": (
            f"k-Anonymity ensures cohorts < {privacy_guard.k_threshold} have sensitive indicators suppressed. "
            f"Differential Privacy injects calibrated Laplace(0, Sensitivity / {privacy_guard.epsilon}) "
            "noise to aggregated percentages and counts to mathematically guarantee zero individual worker trace."
        ),
        "audit_table": privacy_guard.generate_audit_comparison(raw_workforce, shielded_workforce)
    }

@app.post("/api/privacy/configure")
def configure_privacy(payload: PrivacyConfigPayload):
    privacy_guard.set_parameters(payload.k_threshold, payload.epsilon)
    return {
        "message": "Privacy guard parameters updated",
        "k_threshold": privacy_guard.k_threshold,
        "epsilon": privacy_guard.epsilon
    }

@app.get("/api/simulation/current", response_model=SimulationConfig)
def get_simulation_state():
    return simulation_state

@app.post("/api/simulation/apply", response_model=SimulationConfig)
def apply_simulation(payload: SimulationConfig):
    global simulation_state

    # Preset scenario handler
    if payload.active_scenario == "HEATWAVE":
        payload.heat_spike_delta_c = 4.8
        payload.dust_surge_ugm3 = 35.0
        payload.fatigue_delay_delta_pct = 19.5
        payload.break_compliance_drop_pct = 22.0
        payload.clinic_triage_surge = 2
    elif payload.active_scenario == "SHAMAL_DUST":
        payload.heat_spike_delta_c = 1.2
        payload.dust_surge_ugm3 = 180.0
        payload.fatigue_delay_delta_pct = 12.0
        payload.break_compliance_drop_pct = 15.0
        payload.clinic_triage_surge = 1
    elif payload.active_scenario == "ACUTE_FATIGUE":
        payload.heat_spike_delta_c = 2.0
        payload.dust_surge_ugm3 = 20.0
        payload.fatigue_delay_delta_pct = 26.0
        payload.break_compliance_drop_pct = 32.0
        payload.clinic_triage_surge = 3
    elif payload.active_scenario == "NORMAL":
        payload.heat_spike_delta_c = 0.0
        payload.dust_surge_ugm3 = 0.0
        payload.fatigue_delay_delta_pct = 0.0
        payload.break_compliance_drop_pct = 0.0
        payload.clinic_triage_surge = 0

    simulation_state = payload
    return simulation_state

@app.post("/api/directives/{directive_id}/status")
def update_directive_status(directive_id: str, payload: DirectiveUpdatePayload):
    directive_status_registry[directive_id] = payload.status
    return {"id": directive_id, "status": payload.status}

# Mount frontend build static directory if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
