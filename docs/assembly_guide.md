# Assembly Guide - Open Jr RoboCup Soccer Robot

## Overview

This guide walks you through the complete assembly of the Open Jr RoboCup Soccer Robot. Estimated assembly time: 4-6 hours.

## Tools Required

- Hex key set (metric)
- Screwdriver set (Phillips and flathead)
- Soldering iron and solder
- Wire cutters/strippers
- Heat gun or lighter (for heat shrink)
- Multimeter
- 3D printer (for custom parts)
- Allen keys (for motor mounting)

## Parts Checklist

Before starting, verify all components from `../hardware/bom.csv` are present.

## Step 1: Chassis Preparation

### 1.1 3D Printed Parts
Print the following parts using TPU filament:
- Main chassis plate
- Motor mounts (x3)
- Camera mount
- Electronics tray
- Kicker assembly housing

**Print Settings:**
- Material: TPU 85A/90A
- Infill: 40-50%
- Layer height: 0.2mm
- Wall thickness: 2-3 perimeters

### 1.2 Motor Assembly
For each of the 3 motors:
1. Attach L-bracket to motor using M3 screws
2. Mount shaft adapter to motor shaft (secure with set screw)
3. Press omni wheel onto shaft adapter
4. Verify wheel rotates freely

## Step 2: Drive System Installation

### 2.1 Motor Mounting
1. Position motors at 120° intervals around chassis center
2. Secure motor brackets to chassis using M4 bolts
3. Ensure all motors are oriented correctly for omnidirectional movement
4. Check that wheels contact the ground evenly

### 2.2 Wheel Alignment
- Verify all three wheels touch the ground simultaneously
- Adjust motor mount positions if needed
- Wheels should form an equilateral triangle pattern

## Step 3: Electronics Installation

### 3.1 Motor Drivers
1. Mount 3x Pololu G2 motor drivers on electronics tray
2. Leave space between drivers for heat dissipation
3. Secure with double-sided tape or small screws

### 3.2 Power Distribution
1. Install main power switch on chassis edge
2. Mount 20A fuse holder near battery connection point
3. Install buck converter in accessible location
4. Connect power distribution bus bars

### 3.3 Computing Platform
1. Mount Jetson Orin Nano securely on electronics tray
2. Ensure adequate ventilation
3. Route CSI cable for camera connection
4. Connect USB ports for future expansion

### 3.4 Sensor Mounting
1. **IMU (BNO055):**
   - Mount flat and level near robot center
   - Orient according to coordinate system in documentation
   - Secure with standoffs to minimize vibration

2. **Camera:**
   - Attach to camera mount at front of robot
   - Set tilt angle to approximately -15°
   - Route CSI cable carefully to avoid interference

## Step 4: Wiring

### 4.1 Power Wiring
```
Battery → Switch → Fuse → Distribution Point
                          ↓
              ┌───────────┼───────────┬────────────┐
              ↓           ↓           ↓            ↓
         Motor      Buck        Future       (reserve)
         Drivers   Converter
                   (5V)
                    ↓
              Jetson, Sensors
```

**Wire Gauges:**
- Main power (battery to distribution): 16 AWG
- Motor power: 18 AWG
- Logic power: 22 AWG
- Signal wires: 24 AWG

### 4.2 Motor Connections
For each motor driver:
1. Connect motor power (24V) with inline fuse if desired
2. Connect motor terminals to OUT1 and OUT2
3. Install flyback diode across motor terminals (optional, driver has protection)
4. Connect control signals to Jetson GPIO:
   - PWM (speed control)
   - DIR (direction)
   - EN (enable)
   - FAULT (monitoring)

### 4.3 Kicker Circuit
1. Connect solenoid positive to 12V from buck converter
2. Connect solenoid negative to TIP120 collector
3. Connect TIP120 emitter to ground
4. Add 1k resistor between Jetson GPIO and TIP120 base
5. **Critical:** Install flyback diode across solenoid terminals
   - Cathode (striped end) to +12V
   - Anode to transistor collector

### 4.4 I2C Bus (IMU)
Connect BNO055 to Jetson:
- VIN → 3.3V or 5V
- GND → GND
- SCL → I2C clock pin
- SDA → I2C data pin

### 4.5 Camera Connection
- Connect Arducam IMX477 via CSI cable to Jetson CSI port
- Ensure cable is fully seated and locked

## Step 5: Final Assembly

### 5.1 Battery Mounting
1. Secure LiPo battery with velcro strap
2. Ensure battery connector is accessible
3. Add protective covering over battery terminals

### 5.2 Cable Management
1. Bundle wires with zip ties
2. Keep high-current cables away from signal cables
3. Add strain relief where cables connect to boards
4. Label all connections for future maintenance

### 5.3 Final Checks
- [ ] All screws tightened
- [ ] No loose wires
- [ ] Wheels spin freely
- [ ] Camera view unobstructed
- [ ] Ventilation not blocked

## Step 6: Initial Testing

### 6.1 Power-On Sequence
1. **Disconnect motors initially**
2. Connect battery
3. Turn on power switch
4. Measure voltages:
   - Battery voltage at distribution point: ~22.2V
   - Buck converter output: 5.0V ±0.1V
5. Check Jetson boots properly
6. Power off

### 6.2 Motor Test
1. Reconnect motors
2. Power on
3. Test each motor individually at low speed
4. Verify rotation direction matches software configuration
5. Test emergency stop function

### 6.3 Sensor Test
1. Verify IMU is detected on I2C bus
2. Check IMU data readings (orientation, acceleration)
3. Test camera feed
4. Verify image quality and field of view

### 6.4 Kicker Test
⚠️ **Safety Warning:** Do not test kicker when people are in front of robot
1. Test solenoid activation at lowest power setting
2. Verify kicker retracts properly
3. Check cooldown period functionality

## Troubleshooting

### Motors Not Spinning
- Check enable pins are high
- Verify PWM signals present
- Confirm motor driver fault LEDs are off
- Check wiring continuity

### IMU Not Detected
- Verify I2C pull-up resistors
- Check I2C address (jumper setting on BNO055)
- Test I2C bus with `i2cdetect` command

### Camera Issues
- Reseat CSI cable
- Check camera is enabled in Jetson configuration
- Verify correct camera driver loaded

## Next Steps

After successful assembly:
1. Proceed to calibration (`calibration.md`)
2. Install and configure software
3. Test basic behaviors
4. Tune PID parameters
5. Practice soccer skills!

## Safety Reminders

- Always disconnect battery before working on electronics
- Never short battery terminals
- Use appropriate eye protection when testing kicker
- Handle LiPo batteries with care
- Keep flammable materials away from battery charging area
