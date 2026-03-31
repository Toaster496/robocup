# Power Distribution Schematic

## System Overview

```
                         POWER DISTRIBUTION SYSTEM
                         =========================

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   BATTERY INPUT                                                             │
│   ┌──────────────┐                                                         │
│   │ LiPo 6S      │                                                         │
│   │ 22.2V 2200mAh│                                                         │
│   │ 45C          │                                                         │
│   │ XT60         │                                                         │
│   └──────┬───────┘                                                         │
│          │                                                                  │
│          │ Red (Positive)                                                   │
│          │ Black (Negative)                                                 │
│          ▼                                                                  │
│   ┌──────────────┐                                                         │
│   │ MAIN SWITCH  │ Screw Switch                                            │
│   │              │                                                         │
│   └──────┬───────┘                                                         │
│          │                                                                  │
│          ▼                                                                  │
│   ┌──────────────┐                                                         │
│   │ 20A FUSE     │ Slow Blow Ceramic                                       │
│   │ Holder       │ 6.35x32mm 3AG                                           │
│   └──────┬───────┘                                                         │
│          │                                                                  │
│          ▼                                                                  │
│   ════════════════  POWER DISTRIBUTION POINT  ════════════════              │
│          │                                                                  │
│          ├──────────────────────────────────────────────────────┐           │
│          │                          │                           │           │
│          ▼                          ▼                           ▼           │
│   ┌─────────────┐           ┌─────────────┐            ┌─────────────┐     │
│   │ MOTOR BUS   │           │ 5V BUS      │            │ RESERVED    │     │
│   │ (22.2V)     │           │ (5V 9A)     │            │             │     │
│   └──────┬──────┘           └──────┬──────┘            └─────────────┘     │
│          │                          │                                       │
└──────────┼──────────────────────────┼───────────────────────────────────────┘
           │                          │
           │                          │
           ▼                          ▼
    ┌─────────────┐           ┌─────────────┐
    │ Motor       │           │ Buck        │
    │ Drivers x3  │           │ Converter   │
    │ Pololu G2   │           │ D24V90F5    │
    │ 24V21       │           │ 5V 9A       │
    └──────┬──────┘           └──────┬──────┘
           │                          │
           ▼                          ├─────────────────┐
    ┌─────────────┐                   │                 │
    │ Motors x3   │                   ▼                 ▼
    │ 24V 10:1    │           ┌─────────────┐   ┌─────────────┐
    │ Gearmotors  │           │ Jetson      │   │ IMU BNO055  │
    └─────────────┘           │ Orin Nano   │   │ 3.3V/5V     │
                              │             │   └─────────────┘
                              │ Camera      │
                              │ IMX477      │
                              └─────────────┘
```

## Voltage Levels

| Rail | Voltage | Max Current | Protected By | Loads |
|------|---------|-------------|--------------|-------|
| Battery | 22.2V (nominal) | 45C (99A burst) | None (direct) | Main input |
| Main Bus | 18-25.2V | 20A | 20A Fuse | All downstream |
| Motor Bus | 18-25.2V | 15A (5A per motor) | Motor driver limits | Motor drivers |
| 5V Bus | 5.0V | 9A | Buck converter | Jetson, sensors, logic |

## Current Estimates

| Component | Typical Current | Peak Current |
|-----------|-----------------|--------------|
| Jetson Orin Nano | 2-4A @ 5V | 5A @ 5V |
| Camera | 0.3A @ 5V | 0.5A @ 5V |
| IMU BNO055 | 0.015A @ 5V | 0.02A @ 5V |
| Each Motor (no load) | 0.3A @ 24V | 0.5A @ 24V |
| Each Motor (stall) | - | 5A @ 24V |
| Solenoid (active) | 0.5A @ 12V | 1A @ 12V |

**Total Estimated Draw:**
- Logic (5V): ~3A continuous, ~6A peak
- Motors (24V): ~1A continuous, ~15A peak (all stalled)
- Kicker (12V): Intermittent ~0.5A

## Protection Features

### 1. Main Fuse (20A Slow Blow)
- Protects against catastrophic failure
- Allows brief current spikes during motor startup
- Located immediately after power switch

### 2. Motor Driver Protection
- Pololu G2 has built-in:
  - Over-current protection
  - Over-temperature shutdown
  - Under-voltage lockout
  - Reverse voltage protection (with external diode)

### 3. Buck Converter Protection
- Output over-current protection
- Thermal shutdown
- Input under-voltage lockout

### 4. Flyback Diodes
- 1N4007 diodes across all inductive loads
- Prevents voltage spikes from damaging electronics
- Installed on:
  - Each motor (optional, driver has protection)
  - Solenoid (REQUIRED)

## PCB Layout Recommendations

If designing a custom power distribution board:

1. **Keep high-current paths short and wide**
   - Use 2oz copper for power traces
   - Minimum trace width: 10mm for 20A
   
2. **Star grounding**
   - Single point ground for power
   - Separate ground plane for signals
   
3. **Decoupling capacitors**
   - 100µF electrolytic near each motor driver
   - 0.1µF ceramic near each IC
   
4. **Connector placement**
   - Battery input at board edge
   - Fuse holder accessible
   - Test points for voltage measurement

## Testing Procedure

### Initial Power-Up (No Motors Connected)

1. **Visual Inspection**
   - [ ] No solder bridges
   - [ ] Correct component orientation
   - [ ] Secure connections

2. **Continuity Test (Power OFF)**
   - [ ] Battery + to fuse input: continuity
   - [ ] Fuse output to distribution: continuity
   - [ ] Battery - to all grounds: continuity
   - [ ] V+ to GND: NO continuity (no short)

3. **Voltage Test (Power ON)**
   - [ ] Connect battery
   - [ ] Turn on switch
   - [ ] Measure at distribution point: 22-25V
   - [ ] Measure buck converter output: 5.0V ±0.1V
   - [ ] Check for unusual heating

4. **Load Test**
   - [ ] Connect Jetson, verify boot
   - [ ] Connect each peripheral individually
   - [ ] Monitor 5V rail under load

### Motor Connection Test

1. **Individual Motor Test**
   - [ ] Connect one motor driver
   - [ ] Command low speed forward
   - [ ] Verify rotation direction
   - [ ] Check current draw (<0.5A no load)
   - [ ] Repeat for each motor

2. **All Motors Test**
   - [ ] Connect all three motors
   - [ ] Test coordinated movement
   - [ ] Monitor total current draw
   - [ ] Verify no brownouts

## Safety Warnings

⚠️ **HIGH CURRENT HAZARD**
- 20A can cause severe burns and fires
- Never work on live circuits
- Always disconnect battery before modifications

⚠️ **LIPO BATTERY SAFETY**
- Can explode if shorted or damaged
- Always use LiPo-safe charging bags
- Never charge unattended
- Store at storage voltage (3.8V/cell)

⚠️ **ROTATING PARTS**
- Motors can start unexpectedly
- Keep fingers clear of wheels
- Disable motors before handling

## Emergency Procedures

### If Smoke or Fire Occurs:
1. Immediately disconnect battery
2. Use Class D fire extinguisher for LiPo fires
3. Do NOT use water on electrical or LiPo fires
4. Move robot to safe location if possible

### If Short Circuit Detected:
1. Release power switch immediately
2. Disconnect battery
3. Locate and fix short before re-powering
4. Replace blown fuse with identical rating
