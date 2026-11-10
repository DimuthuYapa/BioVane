import pytest
from app.telemetry.climate import (
    calculate_wet_bulb_temperature,
    calculate_wbgt,
    get_wbgt_flag,
    get_aqi_category,
    ClimateCollector
)

def test_wet_bulb_temperature_calculation():
    # Ambient 35C, RH 50% -> Stull formula yields approx 26.2 C
    tw = calculate_wet_bulb_temperature(35.0, 50.0)
    assert 25.0 <= tw <= 27.5

    # Ambient 42C, RH 25% (dry desert heat)
    tw_dry = calculate_wet_bulb_temperature(42.0, 25.0)
    assert 23.0 <= tw_dry <= 26.5

def test_wbgt_calculation_and_flags():
    # Normal / Green conditions
    wbgt_normal = calculate_wbgt(t_ambient=25.0, tw=19.0, solar_rad=200.0, wind_kmh=15.0)
    assert wbgt_normal < 26.7
    assert get_wbgt_flag(wbgt_normal) == "NORMAL"

    # Extreme heat conditions (Black Flag)
    wbgt_extreme = calculate_wbgt(t_ambient=44.0, tw=32.0, solar_rad=950.0, wind_kmh=8.0)
    assert wbgt_extreme >= 32.2
    assert get_wbgt_flag(wbgt_extreme) == "BLACK"

def test_aqi_category_mapping():
    assert get_aqi_category(35) == "Good"
    assert get_aqi_category(75) == "Moderate"
    assert get_aqi_category(125) == "Unhealthy for Sensitive Groups"
    assert get_aqi_category(165) == "Unhealthy"
    assert get_aqi_category(220) == "Very Unhealthy"
    assert get_aqi_category(350) == "Hazardous"

def test_climate_collector_zones():
    collector = ClimateCollector(preset_key="dubai_industrial")
    readings = collector.get_zone_readings()
    assert len(readings) == 4
    zone_ids = [r.zone_id for r in readings]
    assert "zone_a" in zone_ids
    assert "zone_b" in zone_ids
    assert "zone_c" in zone_ids
    assert "zone_d" in zone_ids

    for r in readings:
        assert r.wbgt_c > 0
        assert r.wbgt_flag in ["NORMAL", "GREEN", "YELLOW", "RED", "BLACK"]
        assert r.aqi > 0
