import React from 'react';
import { SlidersHorizontal, Flame, Wind, BatteryWarning, RotateCcw, Play } from 'lucide-react';
import { SimulationConfig } from '../types';

interface SimulationControllerProps {
  simulationConfig: SimulationConfig;
  onApplySimulation: (config: SimulationConfig) => void;
}

export const SimulationController: React.FC<SimulationControllerProps> = ({
  simulationConfig,
  onApplySimulation
}) => {
  const handlePreset = (scenario: "NORMAL" | "HEATWAVE" | "SHAMAL_DUST" | "ACUTE_FATIGUE") => {
    onApplySimulation({
      ...simulationConfig,
      active_scenario: scenario
    });
  };

  const handleSliderChange = (key: keyof SimulationConfig, val: number) => {
    onApplySimulation({
      ...simulationConfig,
      [key]: val,
      active_scenario: "NORMAL" // Custom tweak
    });
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-semibold tracking-wide uppercase text-slate-300">
            Real-Time Stress Simulation & Scenario Injector
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-400">
          Interactive Early Warning Validation
        </span>
      </div>

      {/* Preset Action Scenarios */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
        <button
          onClick={() => handlePreset("NORMAL")}
          className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
            simulationConfig.active_scenario === "NORMAL" && simulationConfig.heat_spike_delta_c === 0
              ? 'bg-emerald-950/40 border-emerald-500/80 text-emerald-300 shadow-lg shadow-emerald-950/40'
              : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold">1. Nominal Baseline</span>
            <RotateCcw className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <span className="text-[11px] text-slate-400">Standard operational conditions without stress spikes</span>
        </button>

        <button
          onClick={() => handlePreset("HEATWAVE")}
          className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
            simulationConfig.active_scenario === "HEATWAVE"
              ? 'bg-red-950/40 border-red-500/80 text-red-300 shadow-lg shadow-red-950/40'
              : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold">2. Acute Heatwave</span>
            <Flame className="h-3.5 w-3.5 text-red-400" />
          </div>
          <span className="text-[11px] text-slate-400">+4.8°C thermal spike, WBGT Black Flag, pacing degradation</span>
        </button>

        <button
          onClick={() => handlePreset("SHAMAL_DUST")}
          className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
            simulationConfig.active_scenario === "SHAMAL_DUST"
              ? 'bg-purple-950/40 border-purple-500/80 text-purple-300 shadow-lg shadow-purple-950/40'
              : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold">3. Shamal Dust Storm</span>
            <Wind className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <span className="text-[11px] text-slate-400">+180 µg/m³ PM10 particulate surge, AQI hazard alert</span>
        </button>

        <button
          onClick={() => handlePreset("ACUTE_FATIGUE")}
          className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
            simulationConfig.active_scenario === "ACUTE_FATIGUE"
              ? 'bg-amber-950/40 border-amber-500/80 text-amber-300 shadow-lg shadow-amber-950/40'
              : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold">4. Shift Fatigue Surge</span>
            <BatteryWarning className="h-3.5 w-3.5 text-amber-400" />
          </div>
          <span className="text-[11px] text-slate-400">+26% task cycle delay, 32% break compliance deficit</span>
        </button>
      </div>

      {/* Manual Fine-Tuning Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
        
        {/* Heat Delta */}
        <div>
          <div className="flex justify-between text-slate-300 mb-1">
            <span>Heat Spike Offset:</span>
            <span className="font-mono text-cyan-400 font-bold">
              +{simulationConfig.heat_spike_delta_c.toFixed(1)}°C
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="8"
            step="0.5"
            value={simulationConfig.heat_spike_delta_c}
            onChange={(e) => handleSliderChange("heat_spike_delta_c", parseFloat(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
        </div>

        {/* Dust Surge */}
        <div>
          <div className="flex justify-between text-slate-300 mb-1">
            <span>Particulate / Dust Surge:</span>
            <span className="font-mono text-purple-400 font-bold">
              +{simulationConfig.dust_surge_ugm3} µg/m³
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="250"
            step="10"
            value={simulationConfig.dust_surge_ugm3}
            onChange={(e) => handleSliderChange("dust_surge_ugm3", parseFloat(e.target.value))}
            className="w-full accent-purple-400 cursor-pointer"
          />
        </div>

        {/* Task Delay Delta */}
        <div>
          <div className="flex justify-between text-slate-300 mb-1">
            <span>Task Delay Variance:</span>
            <span className="font-mono text-amber-400 font-bold">
              +{simulationConfig.fatigue_delay_delta_pct.toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="40"
            step="2"
            value={simulationConfig.fatigue_delay_delta_pct}
            onChange={(e) => handleSliderChange("fatigue_delay_delta_pct", parseFloat(e.target.value))}
            className="w-full accent-amber-400 cursor-pointer"
          />
        </div>

        {/* Break Compliance Drop */}
        <div>
          <div className="flex justify-between text-slate-300 mb-1">
            <span>Break Deficit Drop:</span>
            <span className="font-mono text-rose-400 font-bold">
              -{simulationConfig.break_compliance_drop_pct.toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="50"
            step="5"
            value={simulationConfig.break_compliance_drop_pct}
            onChange={(e) => handleSliderChange("break_compliance_drop_pct", parseFloat(e.target.value))}
            className="w-full accent-rose-400 cursor-pointer"
          />
        </div>

      </div>
    </div>
  );
};
