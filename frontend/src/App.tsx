import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MicroClimateGrid } from './components/MicroClimateGrid';
import { WorkforceProxyMonitor } from './components/WorkforceProxyMonitor';
import { ExplainableAnomalyRadar } from './components/ExplainableAnomalyRadar';
import { DecisionSupportHub } from './components/DecisionSupportHub';
import { PrivacyPreservingAudit } from './components/PrivacyPreservingAudit';
import { SimulationController } from './components/SimulationController';
import { ZoneSnapshot, LocationPreset, SimulationConfig } from './types';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [snapshots, setSnapshots] = useState<ZoneSnapshot[]>([]);
  const [presets, setPresets] = useState<LocationPreset[]>([]);
  const [activePresetId, setActivePresetId] = useState<string>('dubai_industrial');
  const [selectedZoneId, setSelectedZoneId] = useState<string>('zone_a');
  const [simulationConfig, setSimulationConfig] = useState<SimulationConfig>({
    heat_spike_delta_c: 0,
    dust_surge_ugm3: 0,
    fatigue_delay_delta_pct: 0,
    break_compliance_drop_pct: 0,
    clinic_triage_surge: 0,
    active_scenario: 'NORMAL'
  });
  const [kThreshold, setKThreshold] = useState<number>(5);
  const [epsilonBudget, setEpsilonBudget] = useState<number>(1.0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial location presets
  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const res = await fetch('/api/presets');
        if (res.ok) {
          const data = await res.json();
          setPresets(data);
        }
      } catch (err) {
        console.error('Failed to load presets', err);
      }
    };
    fetchPresets();
  }, []);

  // Fetch snapshots periodically
  const fetchSnapshots = async () => {
    try {
      const res = await fetch('/api/snapshots');
      if (res.ok) {
        const data: ZoneSnapshot[] = await res.json();
        setSnapshots(data);
        setError(null);
      } else {
        setError(`Failed to fetch telemetry data (Status: ${res.status})`);
      }
    } catch (err) {
      setError('Cannot connect to BioVane Backend server. Verify backend is running on :8000.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSnapshots();
    const interval = setInterval(fetchSnapshots, 4000);
    return () => clearInterval(interval);
  }, [activePresetId]);

  // Preset location switcher
  const handleSelectPreset = async (presetId: string) => {
    setActivePresetId(presetId);
    try {
      await fetch('/api/presets/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset_id: presetId })
      });
      fetchSnapshots();
    } catch (err) {
      console.error('Failed to switch preset', err);
    }
  };

  // Simulation handler
  const handleApplySimulation = async (config: SimulationConfig) => {
    setSimulationConfig(config);
    try {
      const res = await fetch('/api/simulation/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (res.ok) {
        const updated = await res.json();
        setSimulationConfig(updated);
        fetchSnapshots();
      }
    } catch (err) {
      console.error('Failed to apply simulation', err);
    }
  };

  // Privacy parameters updater
  const handleUpdatePrivacyParams = async (k: number, eps: number) => {
    setKThreshold(k);
    setEpsilonBudget(eps);
    try {
      await fetch('/api/privacy/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ k_threshold: k, epsilon: eps })
      });
      fetchSnapshots();
    } catch (err) {
      console.error('Failed to configure privacy parameters', err);
    }
  };

  // Directive status updater (Acknowledge / Execute)
  const handleUpdateDirectiveStatus = async (directiveId: string, status: "ACKNOWLEDGED" | "COMPLETED") => {
    try {
      await fetch(`/api/directives/${directiveId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      // Optimistic update
      setSnapshots((prev) =>
        prev.map((s) => ({
          ...s,
          directives: s.directives.map((d) => (d.id === directiveId ? { ...d, status } : d))
        }))
      );
    } catch (err) {
      console.error('Failed to update directive status', err);
    }
  };

  // Determine highest threat among all zones
  const getHighestThreat = (): "NORMAL" | "ELEVATED" | "HIGH" | "CRITICAL" => {
    if (snapshots.some((s) => s.anomaly.threat_level === 'CRITICAL')) return 'CRITICAL';
    if (snapshots.some((s) => s.anomaly.threat_level === 'HIGH')) return 'HIGH';
    if (snapshots.some((s) => s.anomaly.threat_level === 'ELEVATED')) return 'ELEVATED';
    return 'NORMAL';
  };

  const activeSnapshot = snapshots.find((s) => s.zone_id === selectedZoneId) || snapshots[0];

  return (
    <div className="min-h-screen bg-[#080d16] text-slate-100 flex flex-col">
      {/* Top Header */}
      <Header
        presets={presets}
        activePresetId={activePresetId}
        onSelectPreset={handleSelectPreset}
        highestThreat={getHighestThreat()}
        activeScenario={simulationConfig.active_scenario}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-6 space-y-6">
        
        {/* Connection Error Banner if backend unreachable */}
        {error && (
          <div className="p-4 rounded-xl bg-red-950/60 border border-red-700/80 text-red-200 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-red-400 shrink-0" />
            <div className="text-xs">
              <strong>Connection Warning:</strong> {error}
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {isLoading && snapshots.length === 0 ? (
          <div className="p-16 text-center space-y-3">
            <RefreshCw className="h-8 w-8 text-cyan-400 animate-spin mx-auto" />
            <p className="text-sm text-slate-400 font-mono">
              Connecting to BioVane Micro-Climate & Fatigue Telemetry Grid...
            </p>
          </div>
        ) : (
          <>
            {/* 1. Real-Time Scenario Simulation Controller */}
            <SimulationController
              simulationConfig={simulationConfig}
              onApplySimulation={handleApplySimulation}
            />

            {/* 2. Hyper-Local Micro-Climate Telemetry Grid */}
            <MicroClimateGrid
              snapshots={snapshots}
              selectedZoneId={selectedZoneId}
              onSelectZone={(id) => setSelectedZoneId(id)}
            />

            {/* 3. Deep Dive into Selected Zone: Explainable Anomaly + Workforce Proxies + Decision Hub */}
            {activeSnapshot && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                {/* Left Column: Anomaly Radar + Workforce Proxies (7 cols) */}
                <div className="lg:col-span-7 space-y-6">
                  <ExplainableAnomalyRadar anomaly={activeSnapshot.anomaly} />
                  <WorkforceProxyMonitor workforce={activeSnapshot.workforce} />
                </div>

                {/* Right Column: Actionable Decision Support Hub (5 cols) */}
                <div className="lg:col-span-5">
                  <DecisionSupportHub
                    directives={activeSnapshot.directives}
                    onUpdateStatus={handleUpdateDirectiveStatus}
                  />
                </div>

              </div>
            )}

            {/* 4. Privacy Preservation & Regulatory Audit Inspector */}
            <PrivacyPreservingAudit
              kThreshold={kThreshold}
              epsilonBudget={epsilonBudget}
              onUpdatePrivacyParams={handleUpdatePrivacyParams}
            />
          </>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#060910] py-4 px-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>BioVane • Micro-Climate & Shift Fatigue Anomaly Grid</span>
          <span className="font-mono text-[11px] text-slate-400">
            Compliant with ISO 7243:2017 &middot; OSHA Heat Stress &middot; Differential Privacy Lap(0, Δf/ε)
          </span>
        </div>
      </footer>
    </div>
  );
};
