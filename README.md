# Open Jr RoboCup Soccer Robot

An open-source robotics platform for Jr RoboCup soccer competitions, built around the NVIDIA Jetson Orin Nano with custom motor control, vision systems, and kicking mechanisms.

## Project Overview

This robot is designed for autonomous soccer play in the Jr RoboCup competition category. It features:
- **Vision System**: Arducam 12MP IMX477 camera for ball and field detection
- **Motion Control**: 3x omnidirectional drive system with brushed DC motors
- **Processing**: NVIDIA Jetson Orin Nano for AI/ML inference and high-level control
- **Sensing**: BNO055 9-DOF IMU for orientation and acceleration
- **Actuation**: Electromagnetic solenoid kicker mechanism

## Hardware Bill of Materials

### Drive System
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| Metal Gearmotor | 3 | 10:1 ratio, 37Dx50L mm, 24V with helical pinion | [Core Electronics](https://core-electronics.com.au/10-1-metal-gearmotor-37dx50l-mm-24v-helical-pinion-47214.html) |
| Omni Wheels | 3 | 3604 series, 14mm bore, 72mm diameter | [Core Electronics](https://core-electronics.com.au/3604-series-omni-wheel-14mm-bore-72mm-diameter.html) |
| Motor Brackets | 2 pairs | Pololu stamped aluminum L-bracket for 37D mm gearmotors | [Core Electronics](https://core-electronics.com.au/pololu-stamped-aluminum-l-bracket-pair-for-37d-mm-metal-gearmotors.html) |
| Shaft Adapters | 2 packs | Pololu universal aluminum mounting hub for 6mm shaft (4-40 holes) | [Core Electronics](https://core-electronics.com.au/pololu-universal-aluminum-mounting-hub-for-6mm-shaft-4-40-holes-2-pack.html) |

### Motor Control
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| Motor Drivers | 3 | Pololu G2 High Power Motor Driver 24V21 | [Core Electronics](https://core-electronics.com.au/pololu-g2-high-power-motor-driver-24v21.html) |
| Flyback Diodes | 25 | 1N4007 general purpose diodes | [Core Electronics](https://core-electronics.com.au/general-purpose-diode-1n4007.html) |
| Fuses | 2 | 20A 6.35x32mm 3AG slow blow ceramic fuse | [Aus Electronics Direct](https://www.auselectronicsdirect.com.au/20a-6.35x32mm-3ag-slow-blow-ceramic-fuse-10-pack) |

### Computing & Vision
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| Main Computer | 1 | NVIDIA Jetson Orin Nano Developer Kit | [Amazon AU](https://www.amazon.com.au/NVIDIA-Jetson-Orin-Nano-Developer/dp/B0BZJTQ5YP) |
| Camera | 1 | Arducam 12MP IMX477 for Raspberry Pi/Jetson | [IoT Store](https://iot-store.com.au/products/b0272-arducam-12mp-imx477-camera-raspberry-pi) |

### Sensors
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| IMU | 1 | Adafruit BNO055 9-DOF Absolute Orientation IMU Fusion Breakout | [Core Electronics](https://core-electronics.com.au/adafruit-9-dof-absolute-orientation-imu-fusion-breakout-bno055.html) |

### Power System
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| Battery | 1 | Gens Ace 22.2V 2200mAh 45C 6S LiPo Soft Case | [Hobbies Direct](https://hobbiesdirect.com.au/products/gens-ace-222v-2200mah-45c-soft-case-lipo-battery-gea6s220045e3-56305) |
| Buck Converter | 1 | Pololu 5V 9A Step-Down Voltage Regulator D24V90F5 | [Core Electronics](https://core-electronics.com.au/pololu-5v-9a-step-down-voltage-regulator-d24v90f5.html) |
| Power Switch | 1 | Screw switch | [Wildman Rocketry](https://wildmanrocketry.com/products/screw-switch) |

### Kicking Mechanism
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| Solenoid | 1 | Abletop DC 12V solenoid electromagnet | [Amazon AU](https://www.amazon.com.au/Abletop-Solenoid-Electromagnetic-Electric-Automobiles/dp/B07G15X91N) |
| Solenoid Controller | 1 | TIP120 Power Darlington Transistors (3-pack, use 1) | [Core Electronics](https://core-electronics.com.au/tip120-power-darlington-transistors-3-pack.html) |

### Mechanical Parts
| Component | Quantity | Description | Supplier Link |
|-----------|----------|-------------|---------------|
| 3D Printing Filament | 1 | TPU 85A/90A flexible filament | [Bambu Lab AU](https://au.store.bambulab.com/products/tpu-85a-tpu-90a?id=573760925208563742) |

## Repository Structure

```
open-jr-robocup-soccer/
├── README.md                 # This file
├── docs/                     # Documentation
│   ├── assembly_guide.md     # Assembly instructions
│   ├── wiring_diagram.md     # Electrical wiring diagrams
│   └── calibration.md        # Sensor and motor calibration guides
├── hardware/                 # Hardware specifications
│   ├── bom.csv               # Bill of Materials (CSV format)
│   └── pinouts.md            # GPIO and connection pinouts
├── firmware/                 # Embedded firmware
│   ├── motor_control/        # Motor driver firmware
│   ├── sensor_readings/      # IMU and sensor interfaces
│   └── kicker_control/       # Solenoid kicking control
├── mechanical/               # CAD files and 3D print models
│   ├── chassis/              # Main chassis designs
│   ├── motor_mounts/         # Motor mounting brackets
│   └── kicker_assembly/      # Kicking mechanism parts
├── electrical/               # Electrical schematics
│   ├── schematics/           # Circuit diagrams
│   └── pcb/                  # PCB design files (if applicable)
└── config/                   # Configuration files
    ├── jetson_config.yaml    # Jetson Orin Nano configuration
    ├── camera_params.yaml    # Camera calibration parameters
    └── robot_params.yaml     # Robot-specific parameters
```

## Getting Started

### Prerequisites
- NVIDIA Jetson Orin Nano with JetPack SDK installed
- Python 3.8+ with required libraries
- 3D printer with TPU filament capability
- Basic electronics tools (soldering iron, multimeter, etc.)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd open-jr-robocup-soccer
   ```

2. **Hardware Assembly**
   - See `docs/assembly_guide.md` for detailed instructions
   - 3D print chassis and mounting parts using TPU filament
   - Mount motors, wheels, and electronics

3. **Electrical Wiring**
   - Refer to `docs/wiring_diagram.md`
   - Connect motor drivers to motors and Jetson
   - Wire power distribution system with fuses and buck converter
   - Install camera and IMU sensors

4. **Software Setup**
   ```bash
   # Install dependencies on Jetson
   pip3 install -r requirements.txt
   
   # Configure Jetson parameters
   cp config/jetson_config.yaml.example config/jetson_config.yaml
   ```

5. **Calibration**
   - Follow `docs/calibration.md` for motor, camera, and IMU calibration

## Safety Considerations

⚠️ **Important Safety Notes:**
- LiPo batteries can be dangerous if mishandled. Always use proper charging equipment and storage bags
- The 24V motor system can deliver high current. Ensure all connections are secure and properly fused
- The solenoid kicker generates significant force. Never activate when people are in front of the robot
- Always disconnect battery before working on electrical connections

## License

This project is open-source. Please see the LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Acknowledgments

- RoboCup Junior Australia for competition rules and support
- Core Electronics and local suppliers for components
- Open-source robotics community
