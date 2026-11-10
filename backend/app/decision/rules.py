import uuid
from datetime import datetime, timezone
from typing import List

from app.models import (
    ClimateReading,
    WorkforceOperationalProxies,
    AnomalyReport,
    DecisionDirective
)

class DecisionSupportEngine:
    """
    Evaluates joint climate and workforce operational stress against established
    international occupational health standards (ISO 7243 WBGT, OSHA Heat Stress,
    UAE MoHRE Midday Working Directives, and ACGIH TLVs).
    Generates role-specific, actionable interventions.
    """

    def generate_directives(
        self,
        climate: ClimateReading,
        workforce: WorkforceOperationalProxies,
        anomaly: AnomalyReport
    ) -> List[DecisionDirective]:
        directives: List[DecisionDirective] = []
        now = datetime.now(timezone.utc)
        zid = climate.zone_id
        zname = climate.zone_name

        # --- 1. Site Safety Supervisor Directives ---
        if climate.wbgt_flag == "BLACK" or anomaly.threat_level == "CRITICAL":
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Site Safety Supervisor",
                    priority="CRITICAL",
                    action_title="Mandate Immediate Strenuous Work Halt & Chaded Rest",
                    action_protocol=(
                        f"WBGT has reached {climate.wbgt_c}°C (Black Flag Tier). Immediately suspend all direct "
                        "sun-exposed heavy manual labor. Move cohort into cooled shelters for a minimum 45-minute "
                        "recovery cycle. Administer chilled electrolyte fluids and conduct buddy-system heat strain checks."
                    ),
                    regulatory_reference="ISO 7243:2017 & UAE MoHRE Heat Directives",
                    status="DISPATCHED"
                )
            )
        elif climate.wbgt_flag == "RED" or anomaly.threat_level == "HIGH":
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Site Safety Supervisor",
                    priority="HIGH",
                    action_title="Enforce 30m Work / 30m Shaded Rest Cycle",
                    action_protocol=(
                        f"WBGT is {climate.wbgt_c}°C with task pacing delay at +{workforce.task_cycle_delay_pct}%. "
                        "Switch to a 30m work / 30m rest rhythm. Verify minimum 1 liter per hour water intake per operative. "
                        "Perform visual checks for flushed skin, lethargy, or coordination lag."
                    ),
                    regulatory_reference="OSHA Heat Stress Technical Manual (Table 1)",
                    status="DISPATCHED"
                )
            )
        elif climate.wbgt_flag == "YELLOW" or workforce.task_cycle_delay_pct > 12.0:
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Site Safety Supervisor",
                    priority="MEDIUM",
                    action_title="Mandate 15-Minute Rest & Hydration Round",
                    action_protocol=(
                        f"Operational delay (+{workforce.task_cycle_delay_pct}%) indicates onset of thermal fatigue. "
                        "Mandate an immediate 15-minute shaded rest break. Ensure water dispensers in sector are refilled."
                    ),
                    regulatory_reference="ACGIH Heat Stress TLV Baseline",
                    status="DISPATCHED"
                )
            )

        # --- 2. Environmental Health Officer (EHO) Directives ---
        if climate.pm10_ugm3 > 140.0 or climate.aqi > 150:
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Environmental Health Officer",
                    priority="HIGH" if climate.aqi > 180 else "MEDIUM",
                    action_title="Deploy Mist Cannons & Enforce N95 Particulate PPE",
                    action_protocol=(
                        f"Particulate surge detected: PM10 at {climate.pm10_ugm3} µg/m³ (AQI: {climate.aqi} - {climate.aqi_category}). "
                        "Activate perimeter dust suppression water atomizers. Issue N95/FFP2 respirators to all exposed operatives."
                    ),
                    regulatory_reference="WHO Air Quality & Industrial Hygiene Standards",
                    status="DISPATCHED"
                )
            )

        if climate.ambient_temp_c >= 40.0 or climate.wbgt_c >= 30.5:
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Environmental Health Officer",
                    priority="HIGH",
                    action_title="Audit Sector Evaporative Misting & Chilled Refuge Pods",
                    action_protocol=(
                        f"Ambient thermal reading {climate.ambient_temp_c}°C with direct solar load {climate.solar_radiation_wm2} W/m². "
                        "Verify refrigerant pressure in mobile welfare trailers and test water misting nozzle throughput."
                    ),
                    regulatory_reference="Regional OHS Code of Practice for Thermal Comfort",
                    status="DISPATCHED"
                )
            )

        # --- 3. Operations & Dispatch Manager Directives ---
        if anomaly.threat_level in ["CRITICAL", "HIGH"] or workforce.task_cycle_delay_pct > 18.0:
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Operations Manager",
                    priority="HIGH",
                    action_title="Throttle Zone Throughput Targets & Rotate Heavy Crane Operators",
                    action_protocol=(
                        f"Combined stress index {anomaly.anomaly_score}/100. Pacing lag is +{workforce.task_cycle_delay_pct}%. "
                        "Temporarily adjust hourly quota targets downward by 20-30% without shift penalties. "
                        "Stagger inbound flatbed truck arrivals to prevent outdoor bottlenecking."
                    ),
                    regulatory_reference="Operational Safety & Fatigue Risk Management Systems (FRMS)",
                    status="DISPATCHED"
                )
            )
        elif workforce.break_compliance_rate_pct < 85.0:
            directives.append(
                DecisionDirective(
                    id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    zone_id=zid,
                    zone_name=zname,
                    target_role="Operations Manager",
                    priority="MEDIUM",
                    action_title="Clear Production Bottlenecks Blocking Mandated Rest Cycles",
                    action_protocol=(
                        f"Break compliance has slipped to {workforce.break_compliance_rate_pct}%. "
                        "Instruct shift team leaders to relieve operatives in 10-minute relays to clear fatigue deficit."
                    ),
                    regulatory_reference="Workforce Health & Human Performance Governance",
                    status="DISPATCHED"
                )
            )

        return directives
