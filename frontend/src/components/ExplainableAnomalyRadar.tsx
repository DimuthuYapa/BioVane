import React from 'react';
import { Radar, ShieldCheck, AlertCircle, TrendingUp, Info } from 'lucide-react';
import { AnomalyReport } from '../types';

interface ExplainableAnomalyRadarProps {
  anomaly: AnomalyReport;
}

export const ExplainableAnomalyRadar: React.FC<ExplainableAnomalyRadarProps> = ({ anomaly }) => {
  const getThreatStyle = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-500/10 border-red-500/40 text-red-400',
          badge: 'bg-red-500/20 text-red-300 border-red-500/50',
          bar: 'bg-red-500',
          gaugeText: 'text-red-400'
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-500/10 border-orange-500/40 text-orange-400',
          badge: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
          bar: 'bg-orange-500',
          gaugeText: 'text-orange-400'
        };
      case 'ELEVATED':
        return {
          bg: 'bg-amber-500/10 border-amber-500/40 text-amber-400',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
          bar: 'bg-amber-400',
          gaugeText: 'text-amber-400'
        };
      default:
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          bar: 'bg-emerald-500',
          gaugeText: 'text-emerald-400'
        };
    }
  };

  const threatStyle = getThreatStyle(anomaly.threat_level);

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
        <div className="flex items-center gap-2">
          <Radar className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-semibold tracking-wide uppercase text-slate-300">
            Explainable Anomaly Detection Core
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Isolation Forest ML</span>
          <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${threatStyle.badge}`}>
            {anomaly.threat_level} THREAT
          </span>
        </div>
      </div>

      {/* Main Grid: Threat Meter + Natural Language Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-center">
        
        {/* Threat Gauge Score */}
        <div className={`p-4 rounded-xl border flex flex-col items-center justify-center text-center ${threatStyle.bg}`}>
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
            Fused Threat Index
          </div>
          <div className={`text-5xl font-black font-mono tracking-tighter ${threatStyle.gaugeText}`}>
            {anomaly.anomaly_score}
            <span className="text-lg font-normal text-slate-400">/100</span>
          </div>
          <div className="text-xs font-medium text-slate-300 mt-2">
            Status: <span className="font-bold">{anomaly.threat_level} RISK</span>
          </div>
          <div className="w-full bg-slate-900/80 h-2 rounded-full overflow-hidden mt-3 border border-slate-700/50">
            <div
              className={`h-full transition-all duration-500 ${threatStyle.bar}`}
              style={{ width: `${Math.min(100, anomaly.anomaly_score)}%` }}
            />
          </div>
        </div>

        {/* Explainability Narrative Headline */}
        <div className="lg:col-span-2 bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between h-full">
          <div>
            <div className="flex items-center gap-1.5 text-xs text-cyan-400 font-mono uppercase tracking-wide mb-1.5">
              <Info className="h-3.5 w-3.5" />
              Explainability Vector Breakdown
            </div>
            <p className="text-sm font-medium text-slate-200 leading-relaxed">
              {anomaly.summary_headline}
            </p>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Model Contamination: 8.0% • 100 Isolation Trees</span>
            <span className="font-mono text-cyan-400">Rolling Baseline: Nominals Active</span>
          </div>
        </div>

      </div>

      {/* Factor Contribution Waterfall */}
      <div className="space-y-2 pt-2">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold uppercase tracking-wider">Factor Contribution Decomposition</span>
          <span className="font-mono">Contribution % (Sums to 100%)</span>
        </div>

        <div className="space-y-2">
          {anomaly.explainability_vectors.map((f) => {
            const isCritical = f.status === 'critical';
            const isElevated = f.status === 'elevated';
            const barColor = isCritical
              ? 'bg-red-500'
              : isElevated
              ? 'bg-amber-400'
              : 'bg-slate-500';

            return (
              <div
                key={f.feature_name}
                className="bg-slate-950/50 border border-slate-800/70 rounded-lg p-2.5 hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-200">{f.display_name}</span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                      isCritical
                        ? 'bg-red-950 text-red-300 border border-red-800'
                        : isElevated
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {f.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-slate-400 text-[11px]">
                      Measured: <span className="text-white font-semibold">{f.measured_value}{f.unit}</span> (Base: {f.baseline_value}{f.unit})
                    </span>
                    <span className="text-cyan-300 font-bold w-12 text-right">
                      {f.contribution_pct}%
                    </span>
                  </div>
                </div>

                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${barColor}`}
                    style={{ width: `${Math.max(2, f.contribution_pct)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
