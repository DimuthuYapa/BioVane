import React from 'react';
import { Thermometer, Droplets, Sun, Wind, CloudFog, AlertTriangle } from 'lucide-react';
import { ZoneSnapshot } from '../types';

interface MicroClimateGridProps {
  snapshots: ZoneSnapshot[];
  selectedZoneId: string;
  onSelectZone: (zoneId: string) => void;
}

export const MicroClimateGrid: React.FC<MicroClimateGridProps> = ({
  snapshots,
  selectedZoneId,
  onSelectZone
}) => {
  const getFlagColor = (flag: string) => {
    switch (flag) {
      case 'BLACK':
        return {
          bg: 'bg-zinc-900 border-zinc-700 text-red-400',
          badge: 'bg-red-950 text-red-400 border-red-700 font-bold',
          bar: 'bg-red-600'
        };
      case 'RED':
        return {
          bg: 'bg-red-950/20 border-red-800/40 text-red-300',
          badge: 'bg-red-900/60 text-red-300 border-red-600 font-bold',
          bar: 'bg-red-500'
        };
      case 'YELLOW':
        return {
          bg: 'bg-amber-950/20 border-amber-800/40 text-amber-300',
          badge: 'bg-amber-900/60 text-amber-300 border-amber-600 font-semibold',
          bar: 'bg-amber-500'
        };
      case 'GREEN':
        return {
          bg: 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300',
          badge: 'bg-emerald-900/60 text-emerald-300 border-emerald-600 font-semibold',
          bar: 'bg-emerald-500'
        };
      default:
        return {
          bg: 'bg-slate-900/60 border-slate-800 text-slate-300',
          badge: 'bg-slate-800 text-slate-300 border-slate-700',
          bar: 'bg-cyan-500'
        };
    }
  };

  const activeSnapshot = snapshots.find((s) => s.zone_id === selectedZoneId) || snapshots[0];

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Thermometer className="h-4 w-4 text-cyan-400" />
          <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300">
            Hyper-Local Micro-Climate Telemetry
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Live Met Stream & IoT Sensoring
        </span>
      </div>

      {/* Zone Selector Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {snapshots.map((s) => {
          const isSelected = s.zone_id === selectedZoneId;
          const flagStyle = getFlagColor(s.climate.wbgt_flag);
          return (
            <button
              key={s.zone_id}
              onClick={() => onSelectZone(s.zone_id)}
              className={`text-left p-3.5 rounded-xl border transition-all ${
                isSelected
                  ? 'bg-slate-800/90 border-cyan-500 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-500/50'
                  : 'bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/40 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between gap-1 mb-2">
                <span className="text-xs font-semibold text-slate-200 line-clamp-1">
                  {s.zone_name.split(' - ')[0]}
                </span>
                <span className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded border ${flagStyle.badge}`}>
                  {s.climate.wbgt_flag} FLAG
                </span>
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <div>
                  <div className="text-2xl font-bold font-mono tracking-tight text-white">
                    {s.climate.wbgt_c}°C
                  </div>
                  <div className="text-[11px] text-slate-400">WBGT Heat Index</div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono font-medium text-slate-300">
                    {s.climate.ambient_temp_c}°C
                  </div>
                  <div className="text-[10px] text-slate-400">Ambient</div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Detailed Telemetry Card for Selected Zone */}
      {activeSnapshot && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">
                  {activeSnapshot.zone_name}
                </h3>
                <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${getFlagColor(activeSnapshot.climate.wbgt_flag).badge}`}>
                  {activeSnapshot.climate.wbgt_flag} FLAG
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Thermal radiation & atmospheric loading under continuous baseline evaluation
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
                <span className="text-slate-400">Apparent Temp: </span>
                <span className="text-cyan-300 font-bold">{activeSnapshot.climate.apparent_temp_c}°C</span>
              </div>
              <div className="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
                <span className="text-slate-400">Wet-Bulb (Tw): </span>
                <span className="text-cyan-300 font-bold">{activeSnapshot.climate.wet_bulb_temp_c}°C</span>
              </div>
            </div>
          </div>

          {/* Grid of Micro-Climate Gauges */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
            
            {/* Ambient & WBGT Heat Card */}
            <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span className="flex items-center gap-1.5">
                  <Thermometer className="h-3.5 w-3.5 text-red-400" />
                  Thermal Load
                </span>
                <span className="font-mono text-[10px] text-slate-400">ISO 7243</span>
              </div>
              <div className="my-2">
                <div className="text-3xl font-extrabold font-mono text-white tracking-tight">
                  {activeSnapshot.climate.wbgt_c}°C
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Wet-Bulb Globe ({activeSnapshot.climate.ambient_temp_c}°C Dry)
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className={`h-full ${getFlagColor(activeSnapshot.climate.wbgt_flag).bar}`}
                  style={{ width: `${Math.min(100, Math.max(10, ((activeSnapshot.climate.wbgt_c - 20) / 16) * 100))}%` }}
                />
              </div>
            </div>

            {/* Humidity & Atmospheric Moisture */}
            <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span className="flex items-center gap-1.5">
                  <Droplets className="h-3.5 w-3.5 text-cyan-400" />
                  Relative Humidity
                </span>
                <span className="font-mono text-[10px] text-slate-400">Sling Hygrometer</span>
              </div>
              <div className="my-2">
                <div className="text-3xl font-extrabold font-mono text-white tracking-tight">
                  {activeSnapshot.climate.relative_humidity_pct}%
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Evaporative Cooling Headroom: {Math.max(0, 100 - activeSnapshot.climate.relative_humidity_pct)}%
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-cyan-500"
                  style={{ width: `${activeSnapshot.climate.relative_humidity_pct}%` }}
                />
              </div>
            </div>

            {/* Solar Radiation & Wind Cooling */}
            <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span className="flex items-center gap-1.5">
                  <Sun className="h-3.5 w-3.5 text-amber-400" />
                  Solar & Wind
                </span>
                <span className="font-mono text-[10px] text-slate-400">Pyranometer</span>
              </div>
              <div className="my-2">
                <div className="text-2xl font-bold font-mono text-white tracking-tight">
                  {activeSnapshot.climate.solar_radiation_wm2} <span className="text-xs font-normal text-slate-400">W/m²</span>
                </div>
                <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                  <Wind className="h-3 w-3 text-cyan-400" />
                  Wind: {activeSnapshot.climate.wind_speed_kmh} km/h
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-amber-400"
                  style={{ width: `${Math.min(100, (activeSnapshot.climate.solar_radiation_wm2 / 1000) * 100)}%` }}
                />
              </div>
            </div>

            {/* Particulate Matter & AQI */}
            <div className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span className="flex items-center gap-1.5">
                  <CloudFog className="h-3.5 w-3.5 text-purple-400" />
                  Air Quality & Dust
                </span>
                <span className="font-mono text-[10px] text-slate-400">US-AQI</span>
              </div>
              <div className="my-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                    {activeSnapshot.climate.aqi}
                  </span>
                  <span className="text-xs font-semibold text-purple-300">
                    {activeSnapshot.climate.aqi_category}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  PM2.5: {activeSnapshot.climate.pm2_5_ugm3} | PM10: {activeSnapshot.climate.pm10_ugm3} µg/m³
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className={`h-full ${activeSnapshot.climate.aqi > 150 ? 'bg-red-500' : activeSnapshot.climate.aqi > 100 ? 'bg-amber-400' : 'bg-purple-500'}`}
                  style={{ width: `${Math.min(100, (activeSnapshot.climate.aqi / 300) * 100)}%` }}
                />
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};
