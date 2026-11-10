import React, { useState, useEffect } from 'react';
import { Shield, Eye, Lock, Sliders, CheckCircle, RefreshCw } from 'lucide-react';
import { PrivacyAuditItem } from '../types';

interface PrivacyPreservingAuditProps {
  kThreshold: number;
  epsilonBudget: number;
  onUpdatePrivacyParams: (k: number, eps: number) => void;
}

export const PrivacyPreservingAudit: React.FC<PrivacyPreservingAuditProps> = ({
  kThreshold,
  epsilonBudget,
  onUpdatePrivacyParams
}) => {
  const [localK, setLocalK] = useState<number>(kThreshold);
  const [localEps, setLocalEps] = useState<number>(epsilonBudget);
  const [auditData, setAuditData] = useState<PrivacyAuditItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const fetchAuditData = async () => {
    setIsLoading(true);
    try {
      const resp = await fetch('/api/privacy/audit');
      if (resp.ok) {
        const data = await resp.json();
        setAuditData(data.audit_table || []);
      }
    } catch (e) {
      console.error('Failed to fetch privacy audit data', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchAuditData();
    }
  }, [isOpen]);

  const handleSaveParams = () => {
    onUpdatePrivacyParams(localK, localEps);
    setTimeout(fetchAuditData, 300);
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 flex items-center justify-between text-left hover:bg-slate-800/40 transition"
      >
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-indigo-950/60 border border-indigo-700/50 flex items-center justify-center text-indigo-400">
            <Lock className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold tracking-wide uppercase text-slate-200">
                Privacy Preservation & Regulatory Compliance Inspector
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/50">
                k-Anonymity & Differential Privacy
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Audit side-by-side noise injection & verify zero individual worker re-identification
            </p>
          </div>
        </div>

        <div className="text-xs font-mono text-cyan-400 flex items-center gap-2">
          <span>{isOpen ? 'Collapse Panel ▲' : 'Inspect Audit Table ▼'}</span>
        </div>
      </button>

      {/* Expanded Content */}
      {isOpen && (
        <div className="p-5 pt-0 border-t border-slate-800/80 space-y-5">
          
          {/* Controls Bar: Sliders for k and epsilon */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-950/70 border border-slate-800">
            {/* k-Anonymity Slider */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span className="font-semibold">k-Anonymity Threshold:</span>
                <span className="font-mono text-cyan-400 font-bold">k = {localK}</span>
              </div>
              <input
                type="range"
                min="2"
                max="10"
                step="1"
                value={localK}
                onChange={(e) => setLocalK(parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
              <span className="text-[10px] text-slate-400">Cohorts &lt; k will be fully suppressed</span>
            </div>

            {/* Differential Privacy Epsilon Slider */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span className="font-semibold">Privacy Loss Budget (ε):</span>
                <span className="font-mono text-indigo-400 font-bold">ε = {localEps.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.2"
                max="3.0"
                step="0.1"
                value={localEps}
                onChange={(e) => setLocalEps(parseFloat(e.target.value))}
                className="w-full accent-indigo-400 cursor-pointer"
              />
              <span className="text-[10px] text-slate-400">Lower ε = stronger privacy (more Laplace noise)</span>
            </div>

            {/* Save & Re-audit button */}
            <div className="flex items-end gap-2">
              <button
                onClick={handleSaveParams}
                className="w-full py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition flex items-center justify-center gap-1.5 shadow-md"
              >
                <CheckCircle className="h-3.5 w-3.5" />
                Apply Privacy Parameters
              </button>
              <button
                onClick={fetchAuditData}
                disabled={isLoading}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                title="Refresh audit table"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Audit Verification Table */}
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="p-3">Sector</th>
                  <th className="p-3">Cohort Size</th>
                  <th className="p-3">Small-Cell Status</th>
                  <th className="p-3">Raw Pacing Lag</th>
                  <th className="p-3">Shielded Pacing Lag</th>
                  <th className="p-3">Laplace Δ</th>
                  <th className="p-3">Clinic Triage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 bg-slate-900/40">
                {auditData.map((row) => (
                  <tr key={row.zone_id} className="hover:bg-slate-800/30">
                    <td className="p-3 font-medium text-slate-200">
                      {row.zone_name.split(' - ')[0]}
                    </td>
                    <td className="p-3 text-slate-300">
                      {row.cohort_size} workers
                    </td>
                    <td className="p-3">
                      {row.is_suppressed ? (
                        <span className="px-2 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-700 font-bold">
                          SUPPRESSED (&lt; k)
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-700">
                          CLEAR (≥ k)
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-slate-400">
                      +{row.raw_task_delay_pct}%
                    </td>
                    <td className="p-3 text-cyan-300 font-bold">
                      {row.is_suppressed ? '--' : `+${row.shielded_task_delay_pct}%`}
                    </td>
                    <td className="p-3 text-indigo-300">
                      {row.is_suppressed ? '--' : `${row.delay_noise_delta > 0 ? '+' : ''}${row.delay_noise_delta}%`}
                    </td>
                    <td className="p-3">
                      {row.is_suppressed ? (
                        <span className="text-amber-400 font-semibold">[MASKED]</span>
                      ) : (
                        <span className="text-white font-semibold">
                          {row.shielded_clinic_triage} / 100
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Privacy Guarantee Footer */}
          <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-900/40 text-[11px] text-indigo-200 flex items-center gap-2">
            <Shield className="h-4 w-4 text-indigo-400 shrink-0" />
            <span>
              <strong>Regulatory Proof:</strong> BioVane mathematical transforms prevent reconstruction attacks. 
              Small cells (&lt; k={kThreshold}) are suppressed, and differential privacy noise ensures individual worker 
              speed, breaks, or clinic records can never be isolated or used for performance disciplinary reviews.
            </span>
          </div>

        </div>
      )}
    </div>
  );
};
