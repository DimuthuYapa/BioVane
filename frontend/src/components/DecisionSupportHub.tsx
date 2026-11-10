import React, { useState } from 'react';
import { ClipboardList, CheckCircle2, ShieldCheck, HardHat, Sparkles, Building2, UserCheck, AlertOctagon } from 'lucide-react';
import { DecisionDirective } from '../types';

interface DecisionSupportHubProps {
  directives: DecisionDirective[];
  onUpdateStatus: (directiveId: string, status: "ACKNOWLEDGED" | "COMPLETED") => void;
}

export const DecisionSupportHub: React.FC<DecisionSupportHubProps> = ({
  directives,
  onUpdateStatus
}) => {
  const [roleFilter, setRoleFilter] = useState<string>("ALL");

  const filtered = directives.filter((d) => {
    if (roleFilter === "ALL") return true;
    return d.target_role.toLowerCase().includes(roleFilter.toLowerCase());
  });

  const getPriorityStyle = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-950/60 text-red-300 border-red-700 font-bold';
      case 'HIGH':
        return 'bg-orange-950/60 text-orange-300 border-orange-700 font-semibold';
      case 'MEDIUM':
        return 'bg-amber-950/60 text-amber-300 border-amber-700';
      default:
        return 'bg-blue-950/60 text-blue-300 border-blue-700';
    }
  };

  const getRoleIcon = (role: string) => {
    if (role.includes("Safety")) return <HardHat className="h-4 w-4 text-amber-400" />;
    if (role.includes("Environmental")) return <Sparkles className="h-4 w-4 text-purple-400" />;
    return <Building2 className="h-4 w-4 text-cyan-400" />;
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header and Filter Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800/80 gap-3">
        <div className="flex items-center gap-2">
          <ClipboardList className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-semibold tracking-wide uppercase text-slate-300">
            Actionable Decision Support Center
          </h3>
          <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
            {filtered.length} active
          </span>
        </div>

        {/* Role Filters */}
        <div className="flex flex-wrap gap-1.5 text-xs">
          {[
            { id: "ALL", label: "All Directives" },
            { id: "Safety", label: "Safety Supervisor" },
            { id: "Environmental", label: "Health Officer (EHO)" },
            { id: "Operations", label: "Operations Manager" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setRoleFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                roleFilter === tab.id
                  ? 'bg-cyan-500 text-black font-semibold shadow'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700/80 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Directives List */}
      {filtered.length === 0 ? (
        <div className="p-8 text-center bg-slate-950/40 border border-slate-800 rounded-xl text-slate-400 text-sm">
          <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
          No urgent interventions required for this sector role. All baseline health metrics are nominal.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {filtered.map((directive) => {
            const isCompleted = directive.status === "COMPLETED";
            const isAck = directive.status === "ACKNOWLEDGED";

            return (
              <div
                key={directive.id}
                className={`p-4 rounded-xl border flex flex-col justify-between transition-all ${
                  isCompleted
                    ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                    : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 shadow-md'
                }`}
              >
                <div>
                  {/* Priority & Target Role */}
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-1.5 text-xs text-slate-300 font-medium">
                      {getRoleIcon(directive.target_role)}
                      <span>{directive.target_role}</span>
                    </div>
                    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${getPriorityStyle(directive.priority)}`}>
                      {directive.priority}
                    </span>
                  </div>

                  {/* Title & Action Protocol */}
                  <h4 className="text-sm font-bold text-white mb-1.5">
                    {directive.action_title}
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                    {directive.action_protocol}
                  </p>
                </div>

                {/* Footer: Regulatory Ref + 1-Click Action Dispatch */}
                <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  <div className="text-[10px] font-mono text-cyan-400 truncate">
                    Ref: {directive.regulatory_reference}
                  </div>

                  <div className="flex items-center gap-1.5">
                    {!isCompleted && !isAck && (
                      <button
                        onClick={() => onUpdateStatus(directive.id, "ACKNOWLEDGED")}
                        className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 transition"
                      >
                        Acknowledge
                      </button>
                    )}
                    {!isCompleted && (
                      <button
                        onClick={() => onUpdateStatus(directive.id, "COMPLETED")}
                        className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 transition flex items-center gap-1"
                      >
                        <CheckCircle2 className="h-3 w-3" />
                        Execute
                      </button>
                    )}
                    {isCompleted && (
                      <span className="text-[11px] font-mono text-emerald-400 font-medium flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        Executed
                      </span>
                    )}
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
