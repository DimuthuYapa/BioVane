import math
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx

from app.models import ClimateReading, LocationPreset

logger = logging.getLogger("biovane.climate")

GCC_PRESETS: Dict[str, LocationPreset] = {
    "dubai_industrial": LocationPreset(
        id="dubai_industrial",
        name="Dubai Industrial City (DIC)",
        country="United Arab Emirates",
        latitude=24.87,
        longitude=55.07,
        description="Major manufacturing, logistics, and heavy transport hub in Dubai"
    ),
    "king_salman_spark": LocationPreset(
        id="king_salman_spark",
        name="King Salman Energy Park (SPARK)",
        country="Kingdom of Saudi Arabia",
        latitude=26.04,
        longitude=49.88,
        description="Eastern Province high-temperature industrial & energy logistics cluster"
    ),
    "mesaieed_qatar": LocationPreset(
        id="mesaieed_qatar",
        name="Mesaieed Industrial City (MIC)",
        country="Qatar",
        latitude=24.99,
        longitude=51.55,
        description="Petrochemical, steel, and port workforce zone"
    ),
    "abu_dhabi_kezad": LocationPreset(
        id="abu_dhabi_kezad",
        name="KEZAD Industrial Zone",
        country="United Arab Emirates",
        latitude=24.80,
        longitude=54.72,
        description="Khalifa Economic Zones Abu Dhabi maritime & fabrication sector"
    )
}

ZONE_VARIATIONS = [
    {
        "zone_id": "zone_a",
        "zone_name": "Sector A - Open Logistics & Container Yard",
        "temp_offset": 1.2,
        "humidity_offset": -2.0,
        "solar_factor": 1.15,
        "pm_factor": 1.1,
    },
    {
        "zone_id": "zone_b",
        "zone_name": "Sector B - Heavy Fabrication & Equipment Bay",
        "temp_offset": 2.4,
        "humidity_offset": 1.5,
        "solar_factor": 0.85,
        "pm_factor": 1.45,
    },
    {
        "zone_id": "zone_c",
        "zone_name": "Sector C - Structural Assembly & Crane Field",
        "temp_offset": 0.6,
        "humidity_offset": -1.0,
        "solar_factor": 1.2,
        "pm_factor": 1.25,
    },
    {
        "zone_id": "zone_d",
        "zone_name": "Sector D - Shaded Assembly & Inbound Staging",
        "temp_offset": -1.5,
        "humidity_offset": 3.0,
        "solar_factor": 0.4,
        "pm_factor": 0.9,
    }
]

def calculate_wet_bulb_temperature(t_c: float, rh_pct: float) -> float:
    """
    Computes Stull formula for wet-bulb temperature Tw given T in Celsius and RH in %.
    Accurate to within 1 deg C across a broad spectrum of ambient temperature and humidity.
    """
    t = float(t_c)
    rh = max(1.0, min(100.0, float(rh_pct)))
    
    tw = (
        t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(t + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
        - 4.686035
    )
    return round(tw, 2)

def calculate_wbgt(t_ambient: float, tw: float, solar_rad: float, wind_kmh: float) -> float:
    """
    Computes Wet-Bulb Globe Temperature (WBGT) approximation:
    WBGT = 0.7*Tw + 0.2*Tg + 0.1*Ta
    Where Tg (Globe Temp) is estimated from Ta, solar radiation (W/m2), and wind speed (m/s).
    """
    wind_ms = max(0.2, wind_kmh / 3.6)
    # Estimate Globe Temperature (empirical radiative equilibrium)
    tg = t_ambient + (0.015 * solar_rad) - (0.06 * wind_ms)
    wbgt = (0.7 * tw) + (0.2 * tg) + (0.1 * t_ambient)
    return round(wbgt, 2)

def get_wbgt_flag(wbgt_c: float) -> str:
    """
    Classifies WBGT according to OSHA / ISO 7243 / military heat stress flag tiers:
    - Normal: < 26.7 C (< 80 F)
    - Green: 26.7 to 29.3 C (80 - 84.9 F)
    - Yellow: 29.4 to 31.0 C (85 - 87.9 F)
    - Red: 31.1 to 32.1 C (88 - 89.9 F)
    - Black: >= 32.2 C (>= 90 F)
    """
    if wbgt_c < 26.7:
        return "NORMAL"
    elif wbgt_c < 29.4:
        return "GREEN"
    elif wbgt_c < 31.1:
        return "YELLOW"
    elif wbgt_c < 32.2:
        return "RED"
    else:
        return "BLACK"

def get_aqi_category(aqi: int) -> str:
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

class ClimateCollector:
    def __init__(self, preset_key: str = "dubai_industrial"):
        self.preset_key = preset_key
        self.preset = GCC_PRESETS.get(preset_key, GCC_PRESETS["dubai_industrial"])
        self.http_client = httpx.Client(timeout=8.0)

    def set_location(self, preset_key: str):
        if preset_key in GCC_PRESETS:
            self.preset_key = preset_key
            self.preset = GCC_PRESETS[preset_key]

    def fetch_live_or_fallback(self) -> Dict[str, float]:
        """
        Fetches current weather and air quality from Open-Meteo APIs.
        Falls back to realistic GCC diurnal profile if network is unavailable.
        """
        lat = self.preset.latitude
        lon = self.preset.longitude
        
        try:
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&current="
                f"temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,direct_radiation"
            )
            aq_url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?"
                f"latitude={lat}&longitude={lon}&current="
                f"pm10,pm2_5,us_aqi,dust"
            )

            w_resp = self.http_client.get(weather_url)
            w_data = w_resp.json().get("current", {})

            aq_resp = self.http_client.get(aq_url)
            aq_data = aq_resp.json().get("current", {})

            t = float(w_data.get("temperature_2m", 36.5))
            rh = float(w_data.get("relative_humidity_2m", 52.0))
            apparent_t = float(w_data.get("apparent_temperature", 42.0))
            wind = float(w_data.get("wind_speed_10m", 14.5))
            solar = float(w_data.get("direct_radiation", 620.0))

            pm2_5 = float(aq_data.get("pm2_5", 38.0))
            pm10 = float(aq_data.get("pm10", 85.0))
            aqi = int(aq_data.get("us_aqi", 108))

            return {
                "temp": t,
                "rh": rh,
                "apparent_temp": apparent_t,
                "wind": wind,
                "solar": solar,
                "pm2_5": pm2_5,
                "pm10": pm10,
                "aqi": aqi
            }

        except Exception as e:
            logger.warning(f"Live Open-Meteo request failed, using realistic diurnal fallback: {e}")
            # Diurnal calculation for GCC climate
            now = datetime.now(timezone.utc)
            hour = now.hour
            # Peak heat between 10:00 and 15:00 UTC
            solar_curve = max(0.0, math.sin((hour - 4) / 14 * math.pi))
            t = 31.0 + 9.5 * solar_curve
            rh = max(25.0, 68.0 - 32.0 * solar_curve)
            apparent_t = t + 5.5 * (rh / 50.0)
            solar = 820.0 * solar_curve
            wind = 12.0 + 6.0 * solar_curve
            pm2_5 = 35.0 + 15.0 * solar_curve
            pm10 = 75.0 + 35.0 * solar_curve
            aqi = int(90 + 30 * solar_curve)

            return {
                "temp": round(t, 1),
                "rh": round(rh, 1),
                "apparent_temp": round(apparent_t, 1),
                "wind": round(wind, 1),
                "solar": round(solar, 1),
                "pm2_5": round(pm2_5, 1),
                "pm10": round(pm10, 1),
                "aqi": aqi
            }

    def get_zone_readings(
        self,
        heat_spike_delta: float = 0.0,
        dust_surge: float = 0.0
    ) -> List[ClimateReading]:
        """
        Produces readings for all 4 micro-climate sectors with realistic local variations
        and applied simulation deltas.
        """
        base = self.fetch_live_or_fallback()
        readings = []
        now = datetime.now(timezone.utc)

        for z in ZONE_VARIATIONS:
            temp = round(base["temp"] + z["temp_offset"] + heat_spike_delta, 1)
            rh = round(max(10.0, min(98.0, base["rh"] + z["humidity_offset"])), 1)
            solar = round(max(0.0, base["solar"] * z["solar_factor"]), 1)
            wind = base["wind"]
            
            tw = calculate_wet_bulb_temperature(temp, rh)
            wbgt = calculate_wbgt(temp, tw, solar, wind)
            flag = get_wbgt_flag(wbgt)

            # Air quality variations
            pm2_5 = round(max(5.0, (base["pm2_5"] * z["pm_factor"]) + (dust_surge * 0.4)), 1)
            pm10 = round(max(10.0, (base["pm10"] * z["pm_factor"]) + dust_surge), 1)
            aqi = int(min(500, base["aqi"] * z["pm_factor"] + (dust_surge * 0.6)))
            aqi_cat = get_aqi_category(aqi)

            apparent_temp = round(base["apparent_temp"] + (z["temp_offset"] * 1.2) + (heat_spike_delta * 1.3), 1)

            readings.append(
                ClimateReading(
                    timestamp=now,
                    zone_id=z["zone_id"],
                    zone_name=z["zone_name"],
                    ambient_temp_c=temp,
                    relative_humidity_pct=rh,
                    apparent_temp_c=apparent_temp,
                    wet_bulb_temp_c=tw,
                    wbgt_c=wbgt,
                    wbgt_flag=flag,
                    solar_radiation_wm2=solar,
                    wind_speed_kmh=wind,
                    pm2_5_ugm3=pm2_5,
                    pm10_ugm3=pm10,
                    aqi=aqi,
                    aqi_category=aqi_cat
                )
            )

        return readings
