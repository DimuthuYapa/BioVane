import pytest
from datetime import datetime, timezone
from app.models import ClimateReading, WorkforceOperationalProxies
from app.engine.anomaly_detector import BioVaneAnomalyDetector

def test_anomaly_detector_nominal_conditions():
    detector = BioVaneAnomalyDetector()

    nominal_climate = ClimateReading(
        timestamp=datetime.now(timezone.utc),
        zone_id="zone_a",
        zone_name="Sector A",
        ambient_temp_c=31.0,
        relative_humidity_pct=45.0,
        apparent_temp_c=34.0,
        wet_bulb_temp_c=23.0,
        wbgt_c=25.8,
        wbgt_flag="NORMAL",
        solar_radiation_wm2=400.0,
        wind_speed_kmh=14.0,
        pm2_5_ugm3=28.0,
        pm10_ugm3=60.0,
        aqi=80,
        aqi_category="Moderate"
    )

    nominal_workforce = WorkforceOperationalProxies(
        timestamp=datetime.now(timezone.utc),
        zone_id="zone_a",
        zone_name="Sector A",
        cohort_size=35,
        task_cycle_delay_pct=2.5,
        break_compliance_rate_pct=95.0,
        break_deficit_minutes=1.5,
        equipment_idle_time_pct=12.0,
        clinic_triage_count=0.1,
        is_suppressed=False,
        privacy_noise_applied=True
    )

    report = detector.evaluate_zone(nominal_climate, nominal_workforce)
    assert report.threat_level in ["NORMAL", "ELEVATED"]
    assert report.anomaly_score < 60.0
    assert len(report.explainability_vectors) == 7

def test_anomaly_detector_acute_heat_and_fatigue():
    detector = BioVaneAnomalyDetector()

    acute_climate = ClimateReading(
        timestamp=datetime.now(timezone.utc),
        zone_id="zone_b",
        zone_name="Sector B",
        ambient_temp_c=45.0,
        relative_humidity_pct=65.0,
        apparent_temp_c=52.0,
        wet_bulb_temp_c=33.5,
        wbgt_c=34.2,
        wbgt_flag="BLACK",
        solar_radiation_wm2=980.0,
        wind_speed_kmh=6.0,
        pm2_5_ugm3=65.0,
        pm10_ugm3=180.0,
        aqi=210,
        aqi_category="Very Unhealthy"
    )

    stressed_workforce = WorkforceOperationalProxies(
        timestamp=datetime.now(timezone.utc),
        zone_id="zone_b",
        zone_name="Sector B",
        cohort_size=35,
        task_cycle_delay_pct=28.5,
        break_compliance_rate_pct=60.0,
        break_deficit_minutes=18.0,
        equipment_idle_time_pct=34.0,
        clinic_triage_count=3.2,
        is_suppressed=False,
        privacy_noise_applied=True
    )

    report = detector.evaluate_zone(acute_climate, stressed_workforce)
    assert report.is_anomaly is True
    assert report.threat_level in ["HIGH", "CRITICAL"]
    assert report.anomaly_score >= 70.0
    
    # Verify explainability vector has WBGT and/or task delay as top contributors
    top_feature = report.explainability_vectors[0]
    assert top_feature.status in ["elevated", "critical"]
    assert top_feature.contribution_pct > 15.0
