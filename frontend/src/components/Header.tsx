import React from 'react';
import { ShieldCheck, MapPin, Activity, Flame, Wind, Clock } from 'lucide-react';
import { LocationPreset } from '../types';

interface HeaderProps {
  presets: LocationPreset[];
  activePresetId: string;
  onSelectPreset: (presetId: string) => void;
  highestThreat: "NORMAL" | "ELEVATED" | "HIGH" | "CRITICAL";
  activeScenario: string;
}

export const Header: React.FC<HeaderProps> = ({
  presets,
  activePresetId,
  onSelectPreset,
  highestThreat,
  activeScenario
}) => {
  const getThreatBadge = () => {
    switch (highestThreat) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40 animate-pulse";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "ELEVATED":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  return (
    <header className="border-b border-slate-800/80 bg-[#0c121e]/90 backdrop-blur sticky top-0 z-40 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        
        {/* Brand & System Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/30">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                BioVane
              </h1>
              <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-700/50">
                Grid v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 font-normal">
              Micro-Climate & Shift Fatigue Anomaly Grid • GCC Telemetry Core
            </p>
          </div>
        </div>

        {/* Global Status Indicators & Controls */}
        <div className="flex flex-wrap items-center gap-2.5 sm:gap-4 w-full md:w-auto justify-between md:justify-end">
          
          {/* Active Preset Location Selector */}
          <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <MapPin className="h-3.5 w-3.5 text-cyan-400" />
            <select
              value={activePresetId}
              onChange={(e) => onSelectPreset(e.target.value)}
              className="bg-transparent text-slate-200 outline-none text-xs cursor-pointer font-medium pr-1"
            >
              {presets.map((p) => (
                <option key={p.id} value={p.id} className="bg-slate-900 text-slate-200">
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Privacy Preservation Guard Status */}
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-indigo-300 text-xs">
            <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
            <span className="hidden sm:inline font-mono font-medium">Privacy Guard:</span>
            <span className="font-mono text-[11px] text-indigo-200">k≥5 · ε=1.0</span>
          </div>

          {/* Threat Status Badge */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-semibold uppercase tracking-wider ${getThreatBadge()}`}>
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${highestThreat === 'CRITICAL' ? 'bg-red-400' : 'bg-emerald-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${highestThreat === 'CRITICAL' ? 'bg-red-500' : 'bg-emerald-500'}`}></span>
            </span>
            <span>Grid: {highestThreat}</span>
          </div>

          {/* Active Scenario Tag (if not normal) */}
          {activeScenario !== "NORMAL" && (
            <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-mono">
              <Flame className="h-3.5 w-3.5 text-amber-400" />
              <span>Sim: {activeScenario}</span>
            </div>
          )}

        </div>

      </div>
    </header>
  );
};
