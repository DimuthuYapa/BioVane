import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("Testing climate module...")
from tests.test_climate import (
    test_wet_bulb_temperature_calculation,
    test_wbgt_calculation_and_flags,
    test_aqi_category_mapping,
    test_climate_collector_zones
)
test_wet_bulb_temperature_calculation()
print("  test_wet_bulb_temperature_calculation: PASSED")
test_wbgt_calculation_and_flags()
print("  test_wbgt_calculation_and_flags: PASSED")
test_aqi_category_mapping()
print("  test_aqi_category_mapping: PASSED")
test_climate_collector_zones()
print("  test_climate_collector_zones: PASSED")

print("Testing privacy guard...")
from tests.test_privacy import (
    test_k_anonymity_small_cell_suppression,
    test_differential_privacy_noise_bounds,
    test_audit_comparison_generation
)
test_k_anonymity_small_cell_suppression()
print("  test_k_anonymity_small_cell_suppression: PASSED")
test_differential_privacy_noise_bounds()
print("  test_differential_privacy_noise_bounds: PASSED")
test_audit_comparison_generation()
print("  test_audit_comparison_generation: PASSED")

print("Testing anomaly detector...")
from tests.test_anomaly import (
    test_anomaly_detector_nominal_conditions,
    test_anomaly_detector_acute_heat_and_fatigue
)
test_anomaly_detector_nominal_conditions()
print("  test_anomaly_detector_nominal_conditions: PASSED")
test_anomaly_detector_acute_heat_and_fatigue()
print("  test_anomaly_detector_acute_heat_and_fatigue: PASSED")

print("\nALL 9 TESTS PASSED SUCCESSFULLY!")
