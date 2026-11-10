import React from 'react';
import { Users, Clock, Coffee, ShieldAlert, Cpu, HeartPulse } from 'lucide-react';
import { WorkforceOperationalProxies } from '../types';

interface WorkforceProxyMonitorProps {
  workforce: WorkforceOperationalProxies;
}

export const WorkforceProxyMonitor: React.FC<WorkforceProxyMonitorProps> = ({ workforce }) => {
  const getPacingSeverity = (delay: number) => {
    if (delay > 20) return { text: 'text-red-400', badge: 'bg-red-950/60 text-red-300 border-red-700' };
    if (delay > 10) return { text: 'text-amber-400', badge: 'bg-amber-950/60 text-amber-300 border-amber-700' };
    return { text: 'text-emerald-400', badge: 'bg-emerald-950/60 text-emerald-300 border-emerald-700' };
  };

  const pacingStyle = getPacingSeverity(workforce.task_cycle_delay_pct);

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Title & Privacy Guarantee Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-indigo-400" />
          <h3 className="text-sm font-semibold tracking-wide uppercase text-slate-300">
            Passive Workforce Operational Proxies
          </h3>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-indigo-950/40 border border-indigo-800/40 text-[11px] text-indigo-300">
          <ShieldAlert className="h-3 w-3 text-indigo-400" />
          <span>Anonymous Aggregation Only • No Individual Tracking</span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        {/* Task Cycle Pacing Variance */}
        <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 text-blue-400" />
              Cycle Delay Lag
            </span>
            <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${pacingStyle.badge}`}>
              +{workforce.task_cycle_delay_pct}%
            </span>
          </div>
          <div className="my-2">
            <div className={`text-2xl font-extrabold font-mono tracking-tight ${pacingStyle.text}`}>
              +{workforce.task_cycle_delay_pct}%
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Shift Cycle Variance (Nominal: 0-3%)
            </div>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
            <div
              className={`h-full ${workforce.task_cycle_delay_pct > 20 ? 'bg-red-500' : workforce.task_cycle_delay_pct > 10 ? 'bg-amber-400' : 'bg-emerald-500'}`}
              style={{ width: `${Math.min(100, (workforce.task_cycle_delay_pct / 30) * 100)}%` }}
            />
          </div>
        </div>

        {/* Break Compliance & Rest Deficit */}
        <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="flex items-center gap-1.5">
              <Coffee className="h-3.5 w-3.5 text-amber-400" />
              Break Compliance
            </span>
            <span className="font-mono text-[10px] text-slate-400">
              Deficit: {workforce.break_deficit_minutes}m
            </span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-extrabold font-mono text-white tracking-tight">
              {workforce.break_compliance_rate_pct}%
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Scheduled Rest Utilization
            </div>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
            <div
              className={`h-full ${workforce.break_compliance_rate_pct < 75 ? 'bg-red-500' : workforce.break_compliance_rate_pct < 88 ? 'bg-amber-400' : 'bg-cyan-500'}`}
              style={{ width: `${workforce.break_compliance_rate_pct}%` }}
            />
          </div>
        </div>

        {/* Equipment Idle Time */}
        <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-cyan-400" />
              Machine Idle Pacing
            </span>
            <span className="font-mono text-[10px] text-slate-400">Forklifts/Cranes</span>
          </div>
          <div className="my-2">
            <div className="text-2xl font-extrabold font-mono text-white tracking-tight">
              {workforce.equipment_idle_time_pct}%
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Thermal Micro-Pauses (Baseline: 14%)
            </div>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
            <div
              className="h-full bg-blue-500"
              style={{ width: `${Math.min(100, (workforce.equipment_idle_time_pct / 50) * 100)}%` }}
            />
          </div>
        </div>

        {/* Clinic Triage Logs (with Privacy Guard / Small-Cell Suppression) */}
        <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="flex items-center gap-1.5">
              <HeartPulse className="h-3.5 w-3.5 text-rose-400" />
              Clinic Triage Rate
            </span>
            <span className="font-mono text-[10px] text-indigo-300">
              k={workforce.k_anonymity_threshold}
            </span>
          </div>
          <div className="my-2">
            {workforce.is_suppressed ? (
              <div>
                <div className="text-sm font-bold font-mono text-amber-400">
                  [SUPPRESSED]
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Cohort &lt; {workforce.k_anonymity_threshold} (Small Cell Protection)
                </div>
              </div>
            ) : (
              <div>
                <div className="text-2xl font-extrabold font-mono text-white tracking-tight">
                  {workforce.clinic_triage_count} <span className="text-xs font-normal text-slate-400">/ 100 workers</span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Heat/Fatigue Chief Complaints
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
            <span>Cohort size: {workforce.cohort_size} workers</span>
          </div>
        </div>

      </div>
    </div>
  );
};
