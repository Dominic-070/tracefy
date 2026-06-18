# Tracefy GPS Tracker – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Integrates your **Tracefy Pro GPS bicycle tracker** into Home Assistant. Shows your bike live on the map and provides sensors for speed, distance, battery status and more.

---

## Entities per bike

| Entity | Type | Description |
|--------|------|-------------|
| `device_tracker.<name>` | Device Tracker | Live GPS position on the HA map |
| `sensor.<name>_speed` | Sensor | Current speed (km/h) |
| `sensor.<name>_distance` | Sensor | Total distance ridden (km) |
| `sensor.<name>_last_seen` | Sensor | Timestamp of last GPS update |
| `sensor.<name>_direction` | Sensor | Heading in degrees |
| `sensor.<name>_gps_fix` | Sensor | Number of GPS satellites in view |
| `sensor.<name>_status` | Sensor | AVAILABLE / MISSING / IN_RECOVERY |
| `binary_sensor.<name>_moving` | Binary Sensor | Is the bike moving right now? |
| `binary_sensor.<name>_charging` | Binary Sensor | Is the battery connected? |
| `binary_sensor.<name>_reported_stolen` | Binary Sensor | Is a theft investigation active? |

Data is refreshed every **1 minute**.

---

## Installation via HACS

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/Dominic-070/tracefy` as type **Integration**
3. Install **Tracefy GPS Tracker**
4. Restart Home Assistant

## Manual installation

1. Copy the `custom_components/tracefy` folder to your HA `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Tracefy**
3. Enter your Tracefy app **email address** and **password**
4. Click **Submit** – your bike(s) will appear automatically

## Supported languages

English · Nederlands · Deutsch · Français

## Requirements

- A Tracefy Pro GPS tracker registered in the Tracefy app
- Home Assistant 2024.1 or newer
