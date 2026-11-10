from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ClimateReading(BaseModel):
    timestamp: datetime
    zone_id: str
    zone_name: str
    ambient_temp_c: float
    relative_humidity_pct: float
    apparent_temp_c: float
    wet_bulb_temp_c: float
    wbgt_c: float
    wbgt_flag: str  # "NORMAL", "GREEN", "YELLOW", "ORANGE", "RED", "BLACK"
    solar_radiation_wm2: float
    wind_speed_kmh: float
    pm2_5_ugm3: float
    pm10_ugm3: float
    aqi: int
    aqi_category: str

class WorkforceOperationalProxies(BaseModel):
    timestamp: datetime
    zone_id: str
    zone_name: str
    cohort_size: int
    task_cycle_delay_pct: float
    break_compliance_rate_pct: float
    break_deficit_minutes: float
    equipment_idle_time_pct: float
    clinic_triage_count: Optional[float] = None
    is_suppressed: bool = False
    privacy_noise_applied: bool = True
    epsilon_budget: float = 1.0
    k_anonymity_threshold: int = 5

class ExplainabilityFeature(BaseModel):
    feature_name: str
    display_name: str
    contribution_pct: float
    measured_value: float
    baseline_value: float
    unit: str
    status: str  # "normal", "elevated", "critical"
    direction: str  # "higher", "lower"

class AnomalyReport(BaseModel):
    timestamp: datetime
    zone_id: str
    zone_name: str
    threat_level: str  # "NORMAL", "ELEVATED", "HIGH", "CRITICAL"
    anomaly_score: float  # 0 to 100
    is_anomaly: bool
    summary_headline: str
    explainability_vectors: List[ExplainabilityFeature]

class DecisionDirective(BaseModel):
    id: str
    timestamp: datetime
    zone_id: str
    zone_name: str
    target_role: str  # "Site Safety Supervisor", "Environmental Health Officer", "Operations Manager"
    priority: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    action_title: str
    action_protocol: str
    regulatory_reference: str
    status: str = "DISPATCHED"  # "DISPATCHED", "ACKNOWLEDGED", "COMPLETED"

class ZoneSnapshot(BaseModel):
    zone_id: str
    zone_name: str
    climate: ClimateReading
    workforce: WorkforceOperationalProxies
    anomaly: AnomalyReport
    directives: List[DecisionDirective]

class SimulationConfig(BaseModel):
    heat_spike_delta_c: float = 0.0
    dust_surge_ugm3: float = 0.0
    fatigue_delay_delta_pct: float = 0.0
    break_compliance_drop_pct: float = 0.0
    clinic_triage_surge: int = 0
    active_scenario: Optional[str] = "NORMAL"  # "NORMAL", "HEATWAVE", "SHAMAL_DUST", "ACUTE_FATIGUE"

class LocationPreset(BaseModel):
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    description: str
