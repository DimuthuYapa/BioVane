export interface ClimateReading {
  timestamp: string;
  zone_id: string;
  zone_name: string;
  ambient_temp_c: number;
  relative_humidity_pct: number;
  apparent_temp_c: number;
  wet_bulb_temp_c: number;
  wbgt_c: number;
  wbgt_flag: "NORMAL" | "GREEN" | "YELLOW" | "RED" | "BLACK";
  solar_radiation_wm2: number;
  wind_speed_kmh: number;
  pm2_5_ugm3: number;
  pm10_ugm3: number;
  aqi: number;
  aqi_category: string;
}

export interface WorkforceOperationalProxies {
  timestamp: string;
  zone_id: string;
  zone_name: string;
  cohort_size: number;
  task_cycle_delay_pct: number;
  break_compliance_rate_pct: number;
  break_deficit_minutes: number;
  equipment_idle_time_pct: number;
  clinic_triage_count: number | null;
  is_suppressed: boolean;
  privacy_noise_applied: boolean;
  epsilon_budget: number;
  k_anonymity_threshold: number;
}

export interface ExplainabilityFeature {
  feature_name: string;
  display_name: string;
  contribution_pct: number;
  measured_value: number;
  baseline_value: number;
  unit: string;
  status: "normal" | "elevated" | "critical";
  direction: "higher" | "lower";
}

export interface AnomalyReport {
  timestamp: string;
  zone_id: string;
  zone_name: string;
  threat_level: "NORMAL" | "ELEVATED" | "HIGH" | "CRITICAL";
  anomaly_score: number;
  is_anomaly: boolean;
  summary_headline: string;
  explainability_vectors: ExplainabilityFeature[];
}

export interface DecisionDirective {
  id: string;
  timestamp: string;
  zone_id: string;
  zone_name: string;
  target_role: "Site Safety Supervisor" | "Environmental Health Officer" | "Operations Manager" | string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  action_title: string;
  action_protocol: string;
  regulatory_reference: string;
  status: "DISPATCHED" | "ACKNOWLEDGED" | "COMPLETED";
}

export interface ZoneSnapshot {
  zone_id: string;
  zone_name: string;
  climate: ClimateReading;
  workforce: WorkforceOperationalProxies;
  anomaly: AnomalyReport;
  directives: DecisionDirective[];
}

export interface LocationPreset {
  id: string;
  name: string;
  country: string;
  latitude: number;
  longitude: number;
  description: string;
}

export interface SimulationConfig {
  heat_spike_delta_c: number;
  dust_surge_ugm3: number;
  fatigue_delay_delta_pct: number;
  break_compliance_drop_pct: number;
  clinic_triage_surge: number;
  active_scenario: "NORMAL" | "HEATWAVE" | "SHAMAL_DUST" | "ACUTE_FATIGUE";
}

export interface PrivacyAuditItem {
  zone_id: string;
  zone_name: string;
  cohort_size: number;
  k_threshold: number;
  epsilon: number;
  is_suppressed: boolean;
  raw_task_delay_pct: number;
  shielded_task_delay_pct: number;
  delay_noise_delta: number;
  raw_break_compliance: number;
  shielded_break_compliance: number;
  raw_clinic_triage: number | null;
  shielded_clinic_triage: number | null;
}
