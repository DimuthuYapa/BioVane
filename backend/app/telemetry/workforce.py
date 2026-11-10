import random
from datetime import datetime, timezone
from typing import Dict, List
from app.models import WorkforceOperationalProxies

# Base sector configurations for workforce cohorts
SECTOR_WORKFORCE_CONFIGS = [
    {
        "zone_id": "zone_a",
        "zone_name": "Sector A - Open Logistics & Container Yard",
        "base_cohort_size": 48,
        "base_delay_pct": 2.5,
        "base_break_compliance": 94.0,
        "base_idle_time_pct": 14.0,
        "base_triage_rate": 0.2,  # per 100 workers
    },
    {
        "zone_id": "zone_b",
        "zone_name": "Sector B - Heavy Fabrication & Equipment Bay",
        "base_cohort_size": 36,
        "base_delay_pct": 3.8,
        "base_break_compliance": 92.0,
        "base_idle_time_pct": 18.0,
        "base_triage_rate": 0.4,
    },
    {
        "zone_id": "zone_c",
        "zone_name": "Sector C - Structural Assembly & Crane Field",
        "base_cohort_size": 30,
        "base_delay_pct": 4.1,
        "base_break_compliance": 90.0,
        "base_idle_time_pct": 16.5,
        "base_triage_rate": 0.3,
    },
    {
        "zone_id": "zone_d",
        "zone_name": "Sector D - Shaded Assembly & Inbound Staging",
        "base_cohort_size": 18,
        "base_delay_pct": 1.2,
        "base_break_compliance": 97.0,
        "base_idle_time_pct": 10.0,
        "base_triage_rate": 0.1,
    }
]

class WorkforceProxyCollector:
    """
    Generates anonymized, cohort-aggregated operational indicators.
    Never tracks individuals. Only aggregates operational rhythm metrics:
    pacing variance, rest compliance, equipment micro-idling, and triage clinic logs.
    """
    def __init__(self):
        self.random_seed = 42

    def get_raw_proxies(
        self,
        heat_wbgt_impact: Dict[str, float],
        fatigue_delay_delta: float = 0.0,
        break_compliance_drop: float = 0.0,
        clinic_surge: int = 0
    ) -> List[WorkforceOperationalProxies]:
        """
        Produces operational proxies factoring in current WBGT heat load and simulation inputs.
        """
        proxies = []
        now = datetime.now(timezone.utc)

        for cfg in SECTOR_WORKFORCE_CONFIGS:
            zid = cfg["zone_id"]
            wbgt = heat_wbgt_impact.get(zid, 28.0)
            
            # Thermal strain response curve: as WBGT exceeds 29.5 C, task delays escalate non-linearly
            heat_strain_factor = 0.0
            if wbgt > 29.0:
                heat_strain_factor = (wbgt - 29.0) * 4.5  # each degree above 29 adds ~4.5% pacing delay
            if wbgt > 32.0:
                heat_strain_factor += (wbgt - 32.0) * 6.0

            # Compute operational indicators
            jitter = random.uniform(-0.8, 0.8)
            task_delay = max(0.0, cfg["base_delay_pct"] + heat_strain_factor + fatigue_delay_delta + jitter)
            
            break_compliance = max(
                40.0,
                min(100.0, cfg["base_break_compliance"] - (heat_strain_factor * 0.8) - break_compliance_drop + jitter)
            )

            # Break deficit: minutes of required rest missed based on compliance drop
            break_deficit = max(0.0, round((100.0 - break_compliance) * 0.45, 1))

            idle_time = max(
                5.0,
                min(60.0, cfg["base_idle_time_pct"] + (heat_strain_factor * 0.6) + (fatigue_delay_delta * 0.4))
            )

            # Raw triage incidents in cohort
            expected_triage = (cfg["base_cohort_size"] / 100.0) * cfg["base_triage_rate"]
            if wbgt > 31.0:
                expected_triage += (wbgt - 31.0) * 1.2
            expected_triage += clinic_surge * (cfg["base_cohort_size"] / 40.0)
            raw_triage = round(max(0.0, expected_triage + random.uniform(-0.2, 0.3)), 1)

            proxies.append(
                WorkforceOperationalProxies(
                    timestamp=now,
                    zone_id=zid,
                    zone_name=cfg["zone_name"],
                    cohort_size=cfg["base_cohort_size"],
                    task_cycle_delay_pct=round(task_delay, 1),
                    break_compliance_rate_pct=round(break_compliance, 1),
                    break_deficit_minutes=break_deficit,
                    equipment_idle_time_pct=round(idle_time, 1),
                    clinic_triage_count=raw_triage,
                    is_suppressed=False,
                    privacy_noise_applied=False,
                    epsilon_budget=1.0,
                    k_anonymity_threshold=5
                )
            )

        return proxies
