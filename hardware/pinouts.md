# Hardware Pinouts and Connections

## NVIDIA Jetson Orin Nano GPIO

### Camera Connection (CSI)
- Use CSI camera connector on Jetson Orin Nano
- Arducam IMX477 connects via MIPI CSI-2 interface

### I2C Connections (IMU BNO055)
| BNO055 Pin | Jetson GPIO Pin | Function |
|------------|-----------------|----------|
| VIN | 3.3V or 5V | Power |
| GND | GND | Ground |
| SCL | GPIO3_I2C_SDA (Pin 3) | I2C Clock |
| SDA | GPIO3_I2C_SCL (Pin 5) | I2C Data |
| INT | GPIO available | Interrupt (optional) |

**I2C Bus:** Default address 0x28 or 0x29 (check jumper setting on BNO055)

## Motor Driver Connections (Pololu G2 24V21)

### Motor Driver 1 (Left Motor)
| Pololu G2 Pin | Connection | Description |
|---------------|------------|-------------|
| VIN | Battery + (via fuse) | Motor power input |
| GND | Battery - | Ground |
| OUT1 | Motor 1 Terminal A | Motor connection |
| OUT2 | Motor 1 Terminal B | Motor connection |
| PWM | Jetson GPIO PWM0 | Speed control |
| DIR | Jetson GPIO | Direction control |
| EN | Jetson GPIO | Enable pin |
| FAULT | Jetson GPIO (input) | Fault indicator |

### Motor Driver 2 (Right Motor)
| Pololu G2 Pin | Connection | Description |
|---------------|------------|-------------|
| VIN | Battery + (via fuse) | Motor power input |
| GND | Battery - | Ground |
| OUT1 | Motor 2 Terminal A | Motor connection |
| OUT2 | Motor 2 Terminal B | Motor connection |
| PWM | Jetson GPIO PWM1 | Speed control |
| DIR | Jetson GPIO | Direction control |
| EN | Jetson GPIO | Enable pin |
| FAULT | Jetson GPIO (input) | Fault indicator |

### Motor Driver 3 (Rear Motor)
| Pololu G2 Pin | Connection | Description |
|---------------|------------|-------------|
| VIN | Battery + (via fuse) | Motor power input |
| GND | Battery - | Ground |
| OUT1 | Motor 3 Terminal A | Motor connection |
| OUT2 | Motor 3 Terminal B | Motor connection |
| PWM | Jetson GPIO PWM2 | Speed control |
| DIR | Jetson GPIO | Direction control |
| EN | Jetson GPIO | Enable pin |
| FAULT | Jetson GPIO (input) | Fault indicator |

## Kicker Solenoid Control (TIP120)

### TIP120 Transistor Circuit
| TIP120 Pin | Connection | Description |
|------------|------------|-------------|
| Base | Jetson GPIO (via 1k resistor) | Control signal |
| Collector | Solenoid negative terminal | Load connection |
| Emitter | GND | Ground |

### Solenoid Connections
| Component | Connection | Description |
|-----------|------------|-------------|
| Solenoid + | 12V (from buck converter) | Power |
| Solenoid - | TIP120 Collector | Switched ground |
| Flyback Diode | Across solenoid terminals | Protection (cathode to +, anode to -) |

## Power Distribution

### Main Power Path
```
LiPo Battery (22.2V) → Power Switch → 20A Fuse → Distribution
                                              ↓
                    ┌─────────────────────┬───────────┬────────────┐
                    ↓                     ↓           ↓            ↓
              Motor Drivers          Buck       Other loads   (future)
              (24V max)           Converter
                                  (5V 9A)
                                    ↓
                              Jetson, Camera,
                              Sensors, Logic
```

### Buck Converter Output (5V 9A)
- Powers: Jetson Orin Nano, Camera, IMU, Logic circuits
- Connection: XT30 or appropriate connector to 5V rail

## GPIO Pin Assignment Summary

| Function | Jetson GPIO | Pin Type | Notes |
|----------|-------------|----------|-------|
| Motor 1 PWM | TBD | PWM | Configure in device tree |
| Motor 1 DIR | TBD | GPIO | Digital output |
| Motor 1 EN | TBD | GPIO | Digital output |
| Motor 2 PWM | TBD | PWM | Configure in device tree |
| Motor 2 DIR | TBD | GPIO | Digital output |
| Motor 2 EN | TBD | GPIO | Digital output |
| Motor 3 PWM | TBD | PWM | Configure in device tree |
| Motor 3 DIR | TBD | GPIO | Digital output |
| Motor 3 EN | TBD | GPIO | Digital output |
| Kicker Control | TBD | GPIO | Digital output |
| I2C SCL | GPIO3_I2C_SCL | I2C | Hardware I2C |
| I2C SDA | GPIO3_I2C_SDA | I2C | Hardware I2C |

**Note:** Specific GPIO pin numbers need to be configured based on Jetson Orin Nano carrier board and device tree customization.

## Safety Features

1. **Fuses:** 20A slow-blow fuses on main power distribution
2. **Flyback Diodes:** 1N4007 diodes across all inductive loads (motors, solenoid)
3. **Power Switch:** Main disconnect for battery
4. **Motor Driver Fault:** Fault pins monitored for overcurrent/overtemperature

## Wiring Guidelines

- Use appropriate wire gauge for current (16-18 AWG for motor power, 22-24 AWG for signals)
- Keep high-current paths short and direct
- Separate power and signal wires to reduce noise
- Use heat shrink tubing on all connections
- Secure all connections with zip ties or cable management
