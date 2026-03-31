# Wiring Diagram - Open Jr RoboCup Soccer Robot

## Overview

This document provides detailed wiring instructions for connecting all electrical components.

## Power Distribution System

### Main Power Path

```
┌─────────────┐     ┌──────────┐     ┌─────────┐     ┌──────────────────┐
│  LiPo       │────▶│  Power   │────▶│  20A    │────▶│ Power            │
│  Battery    │     │  Switch  │     │  Fuse   │     │ Distribution     │
│  22.2V 6S   │     │          │     │         │     │ Point            │
└─────────────┘     └──────────┘     └─────────┘     └──────────────────┘
                                                          │
        ┌─────────────────────────────────────────────────┼──────────────────────────────────────┐
        │                                                 │                                      │
        ▼                                                 ▼                                      ▼
┌───────────────┐                              ┌──────────────────┐                    ┌─────────────────┐
│ Motor Driver 1│                              │ Buck Converter   │                    │ Future Loads    │
│ (Front Motor) │                              │ 22.2V → 5V 9A    │                    │ (reserved)      │
└───────────────┘                              └──────────────────┘                    └─────────────────┘
        │                                               │
        ▼                                               ▼
┌───────────────┐                              ┌──────────────────┐
│ Motor Driver 2│                              │ Jetson Orin Nano │
│ (Rear Left)   │                              │ Camera           │
└───────────────┘                              │ IMU BNO055       │
        │                                      │ Logic Circuits   │
        ▼                                      └──────────────────┘
┌───────────────┐
│ Motor Driver 3│
│ (Rear Right)  │
└───────────────┘
```

### Wire Gauge Recommendations

| Circuit | Current (Max) | Wire Gauge | Length (Max) |
|---------|---------------|------------|--------------|
| Battery to Switch | 20A | 16 AWG | 150mm |
| Switch to Fuse | 20A | 16 AWG | 100mm |
| Fuse to Distribution | 20A | 16 AWG | 100mm |
| Distribution to Motor Drivers | 5A each | 18 AWG | 200mm |
| Distribution to Buck Converter | 10A | 18 AWG | 150mm |
| Motor Driver to Motors | 5A | 18 AWG | 150mm |
| 5V to Jetson | 5A | 20 AWG | 200mm |
| Signal Wires | <100mA | 24 AWG | 300mm |

## Motor Driver Connections (Pololu G2 24V21)

### Motor Driver 1 - Front Motor

```
Pololu G2 Pin          Connection              Wire Color
─────────────────────────────────────────────────────────
VIN (Large Pad)   ────▶ Battery + (via fuse)   Red
GND (Large Pad)   ────▶ Battery -              Black
OUT1              ────▶ Motor Terminal A       Blue
OUT2              ────▶ Motor Terminal B       Green
PWM               ────▶ Jetson GPIO 12         Yellow
DIR               ────▶ Jetson GPIO 16         Orange
EN                ────▶ Jetson GPIO 20         Brown
FAULT             ────▶ Jetson GPIO 21         Gray
```

### Motor Driver 2 - Rear Left Motor

```
Pololu G2 Pin          Connection              Wire Color
─────────────────────────────────────────────────────────
VIN (Large Pad)   ────▶ Battery + (via fuse)   Red
GND (Large Pad)   ────▶ Battery -              Black
OUT1              ────▶ Motor Terminal A       Blue
OUT2              ────▶ Motor Terminal B       Green
PWM               ────▶ Jetson GPIO 13         Yellow
DIR               ────▶ Jetson GPIO 19         Orange
EN                ────▶ Jetson GPIO 26         Brown
FAULT             ────▶ Jetson GPIO 20         Gray
```

### Motor Driver 3 - Rear Right Motor

```
Pololu G2 Pin          Connection              Wire Color
─────────────────────────────────────────────────────────
VIN (Large Pad)   ────▶ Battery + (via fuse)   Red
GND (Large Pad)   ────▶ Battery -              Black
OUT1              ────▶ Motor Terminal A       Blue
OUT2              ────▶ Motor Terminal B       Green
PWM               ────▶ Jetson GPIO 22         Yellow
DIR               ────▶ Jetson GPIO 23         Orange
EN                ────▶ Jetson GPIO 24         Brown
FAULT             ────▶ Jetson GPIO 25         Gray
```

### Motor Terminal Connections

Each motor connects to its driver:

```
Motor Terminal A ────▶ OUT1 on Pololu G2
Motor Terminal B ────▶ OUT2 on Pololu G2

Flyback Diode (1N4007):
Cathode (striped end) ────▶ OUT1
Anode ────▶ OUT2
```

**Note:** Pololu G2 drivers have built-in flyback diodes, so external diodes are optional but recommended for extra protection.

## Kicker Solenoid Circuit

### TIP120 Transistor Wiring

```
                    ┌─────────────┐
                    │   TIP120    │
                    │ Transistor  │
                    └─────────────┘
                         │
        Base ◀───────────┤
        (via 1kΩ         │
        resistor)        │
        from             │
        Jetson GPIO 5    │
                         │
                    Collector ◀───────▶ Solenoid (-)
                         │
                    Emitter ─────────▶ GND
```

### Complete Kicker Circuit

```
Buck Converter 12V Output
        │
        ├───────────────────────────▶ Solenoid (+)
        │
        │                           ┌──────────────┐
        │                           │  Solenoid    │
        │                           │  Coil        │
        │                           └──────────────┘
        │                                   │
        │                                   │
        │                            Collector │
        │                                   │
        │                          ┌────────┴────────┐
        │                          │                 │
        │                     ┌────▼────┐       ┌────▼────┐
        │                     │ TIP120  │       │ 1N4007  │
        │                     │Transistor│       │ Diode   │
        │                     │         │       │(Flyback)│
        │              Base ◀─┤         │       │         │
        │              │      │         │       │         │
        │         1kΩ  │      │         │       │         │
        │        Resistor    │         │       │         │
        │              │      │         │       │         │
        │              │      └────┬────┘       └────┬────┘
        │              │           │                │
        │              │           │                │
        │              │        Emitter             │
        │              │           │                │
        │              │           │                │
        └──────────────┴───────────┴────────────────┘
                                │
                               GND

Jetson GPIO 5 ────▶ 1kΩ Resistor ────▶ TIP120 Base
```

**Critical:** Install flyback diode across solenoid terminals:
- **Cathode** (striped end) to **+12V**
- **Anode** to **TIP120 Collector**

## IMU BNO055 Connections

### I2C Interface

```
BNO055 Pin          Jetson Orin Nano      Wire Color
─────────────────────────────────────────────────────
VIN            ────▶ 3.3V or 5V          Red
GND            ────▶ GND                 Black
SDA            ────▶ GPIO3 (Pin 3)       White
SCL            ────▶ GPIO5 (Pin 5)       Yellow
INT (optional) ────▶ Available GPIO      Blue
```

**I2C Pull-up Resistors:** 
- The BNO055 has onboard pull-ups (2.47kΩ)
- Additional 4.7kΩ pull-ups may be needed if bus is long

## Camera Connection

### Arducam IMX477 (CSI Interface)

```
Arducam IMX477          Jetson Orin Nano
────────────────────────────────────────
CSI Connector  ────────▶ CSI Port (J13)
```

**Installation Steps:**
1. Lift the latch on Jetson CSI connector
2. Insert cable with contacts facing the center of the board
3. Push down firmly and lock the latch
4. Secure cable with strain relief

## Power Switch Wiring

```
Battery XT60 (+) ────▶ Switch Terminal 1
Switch Terminal 2 ────▶ Fuse Holder Input
Fuse Holder Output ────▶ Power Distribution Point
Battery XT60 (-) ────────────────────────────────▶ Power Distribution Ground
```

## Fuse Placement

Install 20A slow-blow fuses at these locations:

1. **Main Power Fuse:** Between switch and power distribution
2. **Motor Bus Fuse (optional):** Individual 5A fuses for each motor driver

## Grounding Strategy

```
                    ┌─────────────────┐
                    │ Battery (-)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Star Ground     │
                    │ Point           │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Motor Driver  │   │ Buck Converter│   │ Signal Ground │
│ Grounds       │   │ Ground        │   │ (Jetson, IMU) │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Important:** Keep high-current grounds separate from signal grounds to reduce noise.

## Connector Types

| Connection | Connector Type |
|------------|----------------|
| Battery | XT60 |
| Motor Power | JST-XH 2-pin or screw terminal |
| Motor Signals | JST-GH 4-pin |
| Power Distribution | XT30 or screw terminal blocks |
| 5V Logic | JST-XH 3-pin |
| I2C | JST-GH 4-pin |
| Camera | CSI ribbon cable (15mm, 0.5mm pitch) |

## Testing Checklist

Before applying power:

- [ ] All connections match wiring diagram
- [ ] No exposed wire strands
- [ ] Flyback diodes installed correctly (cathode to +)
- [ ] TIP120 base has current-limiting resistor
- [ ] I2C pull-up resistors present
- [ ] Ground connections secure
- [ ] Power switch in OFF position
- [ ] Multimeter shows no shorts between V+ and GND

## Troubleshooting

### Motor Not Running
- Check EN pin is HIGH
- Verify PWM signal present
- Check FAULT pin status
- Measure voltage at VIN

### I2C Device Not Detected
- Check SDA/SCL not swapped
- Verify pull-up resistors
- Test with `i2cdetect -r -y 1`

### Kicker Not Firing
- Verify 12V at solenoid
- Check GPIO output
- Test TIP120 with multimeter
- Confirm flyback diode not shorted
