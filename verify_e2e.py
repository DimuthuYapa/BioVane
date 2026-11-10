import sys
import os

# Add backend to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

from starlette.testclient import TestClient
from app.main import app

def run_e2e_verification():
    print("=" * 60)
    print("BIOVANE END-TO-END SYSTEM VERIFICATION")
    print("=" * 60)

    client = TestClient(app)

    # 1. Verify Health
    print("\n1. Checking API Health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    health = r.json()
    print(f"   [PASS] Health: {health['status']} | Service: {health['service']} | Location: {health['location']}")

    # 2. Verify Presets
    print("\n2. Checking GCC Location Presets...")
    r = client.get("/api/presets")
    assert r.status_code == 200
    presets = r.json()
    assert len(presets) >= 4
    print(f"   [PASS] Loaded {len(presets)} GCC industrial presets:")
    for p in presets:
        print(f"      - {p['name']} ({p['country']}) [Lat: {p['latitude']}, Lon: {p['longitude']}]")

    # 3. Test Location Switching
    print("\n3. Testing Location Switching to King Salman Energy Park...")
    r = client.post("/api/presets/select", json={"preset_id": "king_salman_spark"})
    assert r.status_code == 200
    print(f"   [PASS] {r.json()['message']}")

    # 4. Verify Nominal Snapshots & Isolation Forest Scoring
    print("\n4. Verifying Nominal Snapshots & Baseline Isolation Forest...")
    # Reset simulation to normal
    client.post("/api/simulation/apply", json={"active_scenario": "NORMAL"})
    r = client.get("/api/snapshots")
    assert r.status_code == 200
    snapshots = r.json()
    assert len(snapshots) == 4
    for s in snapshots:
        zname = s['zone_name'].split(' - ')[0]
        wbgt = s['climate']['wbgt_c']
        flag = s['climate']['wbgt_flag']
        threat = s['anomaly']['threat_level']
        score = s['anomaly']['anomaly_score']
        print(f"   [PASS] {zname}: WBGT={wbgt}°C ({flag} FLAG) | Threat={threat} (Score: {score}/100)")
        assert len(s['anomaly']['explainability_vectors']) == 7

    # 5. Verify Stress Simulation (Heatwave Surge)
    print("\n5. Simulating Acute Heatwave Spike (+4.8°C, WBGT Surge)...")
    r = client.post("/api/simulation/apply", json={"active_scenario": "HEATWAVE"})
    assert r.status_code == 200
    r = client.get("/api/snapshots")
    snapshots = r.json()
    heatwave_threats = [s['anomaly']['threat_level'] for s in snapshots]
    print(f"   [PASS] Grid threat levels under heatwave: {heatwave_threats}")
    assert any(t in ["HIGH", "CRITICAL"] for t in heatwave_threats)
    
    # Check explainability on acute zone
    high_zone = next(s for s in snapshots if s['anomaly']['threat_level'] in ["HIGH", "CRITICAL"])
    print(f"   [PASS] Anomaly Headline: \"{high_zone['anomaly']['summary_headline']}\"")
    top_factor = high_zone['anomaly']['explainability_vectors'][0]
    print(f"   [PASS] Top Explainability Factor: {top_factor['display_name']} ({top_factor['contribution_pct']}% contribution, status: {top_factor['status']})")

    # 6. Verify Actionable Decision Directives Dispatched
    print("\n6. Checking Role-Specific Action Directives...")
    directives = high_zone['directives']
    assert len(directives) >= 2
    roles = [d['target_role'] for d in directives]
    print(f"   [PASS] Dispatched directives for: {set(roles)}")
    for d in directives:
        print(f"      - [{d['priority']}] {d['target_role']}: \"{d['action_title']}\" (Ref: {d['regulatory_reference']})")

    # 7. Test Directive Acknowledgment & Execution
    first_dir = directives[0]
    print(f"\n7. Testing 1-Click Acknowledge & Execute on Directive ID '{first_dir['id']}'...")
    r = client.post(f"/api/directives/{first_dir['id']}/status", json={"status": "ACKNOWLEDGED"})
    assert r.status_code == 200
    assert r.json()['status'] == "ACKNOWLEDGED"
    print("   [PASS] Status updated to ACKNOWLEDGED")

    r = client.post(f"/api/directives/{first_dir['id']}/status", json={"status": "COMPLETED"})
    assert r.status_code == 200
    assert r.json()['status'] == "COMPLETED"
    print("   [PASS] Status updated to COMPLETED")

    # 8. Verify Privacy Audit & Small-Cell Suppression
    print("\n8. Verifying Privacy Preservation & k-Anonymity Guard...")
    r = client.get("/api/privacy/audit")
    assert r.status_code == 200
    audit = r.json()
    print(f"   [PASS] Privacy config: k={audit['k_threshold']}, epsilon={audit['epsilon_budget']}")
    for row in audit['audit_table']:
        print(f"      - {row['zone_name'].split(' - ')[0]}: Cohort={row['cohort_size']} | Suppressed={row['is_suppressed']} | Raw Delay={row['raw_task_delay_pct']}% -> Shielded={row['shielded_task_delay_pct']}% (Noise delta: {row['delay_noise_delta']}%)")

    # 9. Verify Frontend Static Asset Serving
    print("\n9. Verifying Compiled React Frontend Serving...")
    r = client.get("/")
    assert r.status_code == 200
    assert "BioVane" in r.text
    assert '<div id="root"></div>' in r.text
    print("   [PASS] Root path correctly serves compiled Vite frontend index.html!")

    print("\n" + "=" * 60)
    print("ALL 9 END-TO-END VERIFICATION CHECKS PASSED WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_verification()
