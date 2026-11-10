import pytest
from datetime import datetime, timezone
from app.models import WorkforceOperationalProxies
from app.privacy.guard import PrivacyGuard

def test_k_anonymity_small_cell_suppression():
    guard = PrivacyGuard(k_threshold=5, epsilon=1.0)

    # Cell with only 3 workers (< k=5)
    small_cell = WorkforceOperationalProxies(
        timestamp=datetime.now(timezone.utc),
        zone_id="test_small",
        zone_name="Small Isolated Cell",
        cohort_size=3,
        task_cycle_delay_pct=15.0,
        break_compliance_rate_pct=70.0,
        break_deficit_minutes=12.0,
        equipment_idle_time_pct=25.0,
        clinic_triage_count=1.0,
        is_suppressed=False,
        privacy_noise_applied=False
    )

    shielded = guard.apply_privacy_shield([small_cell])[0]
    assert shielded.is_suppressed is True
    assert shielded.clinic_triage_count is None
    assert shielded.task_cycle_delay_pct == 0.0

def test_differential_privacy_noise_bounds():
    guard = PrivacyGuard(k_threshold=5, epsilon=1.0)

    large_cohort = WorkforceOperationalProxies(
        timestamp=datetime.now(timezone.utc),
        zone_id="test_large",
        zone_name="Large Fabrication Bay",
        cohort_size=40,
        task_cycle_delay_pct=10.0,
        break_compliance_rate_pct=85.0,
        break_deficit_minutes=5.0,
        equipment_idle_time_pct=15.0,
        clinic_triage_count=0.5,
        is_suppressed=False,
        privacy_noise_applied=False
    )

    shielded_runs = [guard.apply_privacy_shield([large_cohort])[0] for _ in range(20)]
    
    # Check that privacy noise is applied and values vary stochastically
    delays = [s.task_cycle_delay_pct for s in shielded_runs]
    assert len(set(delays)) > 1  # Not identical constants
    for s in shielded_runs:
        assert s.is_suppressed is False
        assert 0.0 <= s.break_compliance_rate_pct <= 100.0
        assert s.clinic_triage_count is not None
        assert s.clinic_triage_count >= 0.0

def test_audit_comparison_generation():
    guard = PrivacyGuard(k_threshold=5, epsilon=1.0)
    raw = [
        WorkforceOperationalProxies(
            timestamp=datetime.now(timezone.utc),
            zone_id="zone_a",
            zone_name="Zone A",
            cohort_size=30,
            task_cycle_delay_pct=8.0,
            break_compliance_rate_pct=90.0,
            break_deficit_minutes=4.0,
            equipment_idle_time_pct=12.0,
            clinic_triage_count=0.3,
            is_suppressed=False,
            privacy_noise_applied=False
        )
    ]
    shielded = guard.apply_privacy_shield(raw)
    audit = guard.generate_audit_comparison(raw, shielded)
    
    assert len(audit) == 1
    assert "k_threshold" in audit[0]
    assert "epsilon" in audit[0]
    assert "delay_noise_delta" in audit[0]
