import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from sklearn.ensemble import IsolationForest

from app.models import (
    ClimateReading,
    WorkforceOperationalProxies,
    AnomalyReport,
    ExplainabilityFeature
)

# Rolling baseline values (means and standard deviations under normal safe operations)
FEATURE_BASELINES = {
    "wbgt_c": {"name": "Wet-Bulb Globe Temp (WBGT)", "mean": 26.5, "std": 1.8, "unit": "°C"},
    "apparent_temp_c": {"name": "Heat Index / Apparent Temp", "mean": 35.0, "std": 3.0, "unit": "°C"},
    "pm2_5_ugm3": {"name": "Particulate Matter PM2.5", "mean": 30.0, "std": 8.0, "unit": "µg/m³"},
    "task_delay_pct": {"name": "Task Cycle Pacing Delay", "mean": 3.0, "std": 2.5, "unit": "%"},
    "break_deficit_min": {"name": "Shift Break Deficit", "mean": 2.5, "std": 2.0, "unit": "min"},
    "equipment_idle_pct": {"name": "Equipment Idle Pacing", "mean": 14.0, "std": 3.5, "unit": "%"},
    "clinic_triage_count": {"name": "Anonymized Clinic Triage", "mean": 0.2, "std": 0.3, "unit": "visits"}
}

class BioVaneAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.08,
            random_state=42
        )
        self._train_baseline_model()

    def _train_baseline_model(self):
        """
        Trains Isolation Forest on simulated nominal operational conditions.
        """
        np.random.seed(42)
        n_samples = 1200
        
        # Nominal operational conditions
        wbgt = np.random.normal(26.5, 1.6, n_samples)
        apparent = np.random.normal(35.0, 2.8, n_samples)
        pm2_5 = np.random.normal(30.0, 7.5, n_samples)
        task_delay = np.maximum(0.0, np.random.normal(3.0, 2.2, n_samples))
        break_deficit = np.maximum(0.0, np.random.normal(2.5, 1.8, n_samples))
        idle = np.maximum(5.0, np.random.normal(14.0, 3.0, n_samples))
        triage = np.maximum(0.0, np.random.normal(0.2, 0.25, n_samples))

        x_train = np.column_stack([
            wbgt, apparent, pm2_5, task_delay, break_deficit, idle, triage
        ])
        self.model.fit(x_train)

    def extract_feature_vector(
        self,
        climate: ClimateReading,
        workforce: WorkforceOperationalProxies
    ) -> np.ndarray:
        triage_val = workforce.clinic_triage_count if workforce.clinic_triage_count is not None else 0.0
        return np.array([
            climate.wbgt_c,
            climate.apparent_temp_c,
            climate.pm2_5_ugm3,
            workforce.task_cycle_delay_pct,
            workforce.break_deficit_minutes,
            workforce.equipment_idle_time_pct,
            triage_val
        ]).reshape(1, -1)

    def compute_explainability(
        self,
        climate: ClimateReading,
        workforce: WorkforceOperationalProxies
    ) -> List[ExplainabilityFeature]:
        """
        Computes standardized deviations against rolling baseline and apportions
        normalized anomaly contribution percentages across environmental and operational vectors.
        """
        triage_val = workforce.clinic_triage_count if workforce.clinic_triage_count is not None else 0.0
        
        measurements = {
            "wbgt_c": climate.wbgt_c,
            "apparent_temp_c": climate.apparent_temp_c,
            "pm2_5_ugm3": climate.pm2_5_ugm3,
            "task_delay_pct": workforce.task_cycle_delay_pct,
            "break_deficit_min": workforce.break_deficit_minutes,
            "equipment_idle_pct": workforce.equipment_idle_time_pct,
            "clinic_triage_count": triage_val
        }

        z_scores = {}
        for key, val in measurements.items():
            meta = FEATURE_BASELINES[key]
            z = (val - meta["mean"]) / meta["std"]
            # We focus primarily on positive stress deviations
            z_scores[key] = max(0.0, z)

        total_stress = sum(z_scores.values())
        if total_stress <= 0.001:
            total_stress = 1.0  # Avoid division by zero when perfectly baseline

        features: List[ExplainabilityFeature] = []
        for key, z in z_scores.items():
            meta = FEATURE_BASELINES[key]
            measured = measurements[key]
            baseline = meta["mean"]
            pct = round((z / total_stress) * 100.0, 1)

            # Determine feature status
            if z > 2.8:
                status = "critical"
            elif z > 1.5:
                status = "elevated"
            else:
                status = "normal"

            direction = "higher" if measured >= baseline else "lower"

            features.append(
                ExplainabilityFeature(
                    feature_name=key,
                    display_name=meta["name"],
                    contribution_pct=pct,
                    measured_value=round(measured, 2),
                    baseline_value=meta["mean"],
                    unit=meta["unit"],
                    status=status,
                    direction=direction
                )
            )

        # Sort features by contribution descending
        features.sort(key=lambda f: f.contribution_pct, reverse=True)
        return features

    def evaluate_zone(
        self,
        climate: ClimateReading,
        workforce: WorkforceOperationalProxies
    ) -> AnomalyReport:
        features = self.compute_explainability(climate, workforce)
        x_vec = self.extract_feature_vector(climate, workforce)
        
        # Decision function: lower values mean more anomalous
        score_raw = self.model.decision_function(x_vec)[0]
        is_if_anomaly = self.model.predict(x_vec)[0] == -1

        # Transform raw score [-0.3, 0.3] into standard 0 - 100 threat index
        # When score_raw < 0, it's anomalous
        threat_index = max(0.0, min(100.0, (0.22 - score_raw) * 190.0))
        
        # If WBGT flag is RED or BLACK, or task delay is over 20%, force elevated threat
        if climate.wbgt_flag in ["RED", "BLACK"] or workforce.task_cycle_delay_pct > 22.0:
            threat_index = max(threat_index, 72.0)
        elif climate.wbgt_flag == "YELLOW" or workforce.task_cycle_delay_pct > 12.0:
            threat_index = max(threat_index, 50.0)

        threat_index = round(threat_index, 1)

        # Classify threat level
        if threat_index >= 75.0:
            threat_level = "CRITICAL"
            is_anomaly = True
        elif threat_index >= 55.0:
            threat_level = "HIGH"
            is_anomaly = True
        elif threat_index >= 35.0:
            threat_level = "ELEVATED"
            is_anomaly = True if is_if_anomaly else False
        else:
            threat_level = "NORMAL"
            is_anomaly = False

        # Build natural language explainability headline
        top_factors = [f for f in features if f.status in ["elevated", "critical"]]
        if not top_factors:
            top_factors = features[:2]

        top_names = [
            f"{f.display_name} ({f.measured_value}{f.unit}, {f.contribution_pct}% contribution)"
            for f in top_factors[:2]
        ]
        
        if is_anomaly:
            headline = f"Anomaly triggered in {climate.zone_name}: Driven by {top_names[0]}"
            if len(top_names) > 1:
                headline += f" coupled with {top_names[1]}"
        else:
            headline = f"{climate.zone_name} is operating within nominal micro-climate & shift fatigue tolerance boundaries."

        return AnomalyReport(
            timestamp=datetime.now(timezone.utc),
            zone_id=climate.zone_id,
            zone_name=climate.zone_name,
            threat_level=threat_level,
            anomaly_score=threat_index,
            is_anomaly=is_anomaly,
            summary_headline=headline,
            explainability_vectors=features
        )
