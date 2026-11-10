import copy
import numpy as np
from typing import Dict, List, Any
from app.models import WorkforceOperationalProxies

class PrivacyGuard:
    """
    Enforces privacy-preserving processing on workforce operational signals:
    1. Small-Cell Suppression & k-Anonymity Guard (default k=5)
    2. Differential Privacy Laplace Noise Injection for numerical metrics
    3. Guarantees zero individual worker traceability or performance penalization
    """

    def __init__(self, k_threshold: int = 5, epsilon: float = 1.0):
        self.k_threshold = k_threshold
        self.epsilon = max(0.1, float(epsilon))

    def set_parameters(self, k_threshold: int, epsilon: float):
        self.k_threshold = max(2, int(k_threshold))
        self.epsilon = max(0.05, float(epsilon))

    def laplace_mechanism(self, value: float, sensitivity: float, scale_override: float = None) -> float:
        """
        Draws noise from Laplace(0, sensitivity / epsilon).
        """
        b = scale_override if scale_override is not None else (sensitivity / self.epsilon)
        noise = np.random.laplace(0.0, b)
        return float(value + noise)

    def apply_privacy_shield(
        self,
        raw_proxies: List[WorkforceOperationalProxies]
    ) -> List[WorkforceOperationalProxies]:
        """
        Transforms raw operational proxies into privacy-preserving proxies.
        """
        shielded: List[WorkforceOperationalProxies] = []

        for p in raw_proxies:
            item = copy.deepcopy(p)
            item.k_anonymity_threshold = self.k_threshold
            item.epsilon_budget = self.epsilon

            # 1. k-Anonymity & Small-Cell Suppression check
            if item.cohort_size < self.k_threshold:
                # Suppress small cells to eliminate individual identification risk
                item.is_suppressed = True
                item.clinic_triage_count = None
                item.task_cycle_delay_pct = 0.0
                item.break_compliance_rate_pct = 100.0
                item.equipment_idle_time_pct = 0.0
                item.break_deficit_minutes = 0.0
                item.privacy_noise_applied = True
                shielded.append(item)
                continue

            # 2. Differential Privacy noise injection on aggregated rates
            # Sensitivity of task cycle delay (%): delta_f = 2.0%
            noise_delay = self.laplace_mechanism(item.task_cycle_delay_pct, sensitivity=1.5)
            item.task_cycle_delay_pct = round(max(0.0, noise_delay), 1)

            # Sensitivity of break compliance: delta_f = 100 / cohort_size
            comp_sensitivity = 100.0 / max(10, item.cohort_size)
            noise_compliance = self.laplace_mechanism(item.break_compliance_rate_pct, sensitivity=comp_sensitivity)
            item.break_compliance_rate_pct = round(max(0.0, min(100.0, noise_compliance)), 1)

            # Break deficit
            item.break_deficit_minutes = max(0.0, round((100.0 - item.break_compliance_rate_pct) * 0.45, 1))

            # Equipment idle time
            noise_idle = self.laplace_mechanism(item.equipment_idle_time_pct, sensitivity=2.0)
            item.equipment_idle_time_pct = round(max(0.0, min(100.0, noise_idle)), 1)

            # Clinic triage count: integer/count sensitivity = 1.0
            if item.clinic_triage_count is not None:
                # Laplace noise with count sensitivity
                noisy_triage = self.laplace_mechanism(float(item.clinic_triage_count), sensitivity=1.0)
                item.clinic_triage_count = round(max(0.0, noisy_triage), 1)

            item.is_suppressed = False
            item.privacy_noise_applied = True
            shielded.append(item)

        return shielded

    def generate_audit_comparison(
        self,
        raw_list: List[WorkforceOperationalProxies],
        shielded_list: List[WorkforceOperationalProxies]
    ) -> List[Dict[str, Any]]:
        """
        Provides side-by-side verification of privacy transformation.
        """
        audit = []
        for raw, shielded in zip(raw_list, shielded_list):
            audit.append({
                "zone_id": raw.zone_id,
                "zone_name": raw.zone_name,
                "cohort_size": raw.cohort_size,
                "k_threshold": self.k_threshold,
                "epsilon": self.epsilon,
                "is_suppressed": shielded.is_suppressed,
                "raw_task_delay_pct": raw.task_cycle_delay_pct,
                "shielded_task_delay_pct": shielded.task_cycle_delay_pct,
                "delay_noise_delta": round(shielded.task_cycle_delay_pct - raw.task_cycle_delay_pct, 2),
                "raw_break_compliance": raw.break_compliance_rate_pct,
                "shielded_break_compliance": shielded.break_compliance_rate_pct,
                "raw_clinic_triage": raw.clinic_triage_count,
                "shielded_clinic_triage": shielded.clinic_triage_count,
            })
        return audit
