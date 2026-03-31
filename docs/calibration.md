# Calibration Guide - Open Jr RoboCup Soccer Robot

## Overview

This guide covers calibration procedures for all robot sensors and actuators. Proper calibration is essential for optimal performance.

## Prerequisites

- Fully assembled robot
- Charged battery connected
- Software environment set up
- Calibration tools (checkerboard, multimeter, etc.)

## 1. IMU Calibration (BNO055)

### 1.1 Initial Setup
```bash
# Install required libraries
pip3 install smbus2 numpy

# Test I2C connection
i2cdetect -r -y <i2c_bus_number>
# Should show device at 0x28 or 0x29
```

### 1.2 Static Calibration
1. Place robot on level surface
2. Run IMU calibration script:
```bash
python3 firmware/sensor_readings/calibrate_imu.py --mode static
```
3. Keep robot completely still for 30 seconds
4. Script will calculate bias values

### 1.3 Orientation Calibration
1. Mark the "forward" direction on your robot
2. Align robot with a known reference (field edge)
3. Record yaw offset:
```bash
python3 firmware/sensor_readings/calibrate_imu.py --mode orientation --reference-yaw 0.0
```

### 1.4 Verification
- Rotate robot 90°, verify yaw changes by ~90°
- Tilt robot, verify pitch and roll respond correctly
- Acceleration should read ~9.8 m/s² when stationary

### 1.5 Save Configuration
Update `config/robot_params.yaml` with offset values:
```yaml
sensors:
  imu:
    orientation:
      x_offset_deg: <calibrated_value>
      y_offset_deg: <calibrated_value>
      z_offset_deg: <calibrated_value>
```

## 2. Camera Calibration

### 2.1 Preparation
Print a checkerboard pattern:
- 9×6 internal corners
- 25mm square size
- High contrast print on stiff paper

### 2.2 Capture Images
```bash
# Create calibration directory
mkdir -p /tmp/camera_calibration

# Run image capture script
python3 firmware/vision/capture_calibration_images.py
```

Capture 15-20 images with checkerboard at:
- Various angles
- Different distances
- All areas of the image frame

### 2.3 Calculate Intrinsics
```bash
python3 firmware/vision/calibrate_camera.py \
  --image-dir /tmp/camera_calibration \
  --output config/camera_intrinsics.yaml
```

### 2.4 Verify Calibration
```bash
python3 firmware/vision/verify_calibration.py \
  --config config/camera_intrinsics.yaml
```

Check reprojection error (< 0.5 pixels is good)

### 2.5 Update Configuration
Copy calibrated parameters to `config/camera_params.yaml`:
```yaml
intrinsics:
  focal_length:
    fx: <calibrated_value>
    fy: <calibrated_value>
  principal_point:
    cx: <calibrated_value>
    cy: <calibrated_value>
  distortion:
    k1: <calibrated_value>
    k2: <calibrated_value>
    p1: <calibrated_value>
    p2: <calibrated_value>
    k3: <calibrated_value>
```

## 3. Motor Calibration

### 3.1 Direction Test
```bash
python3 firmware/motor_control/test_motor_direction.py
```

For each motor:
1. Command forward rotation
2. Verify wheel rotates in expected direction
3. If reversed, swap motor wires or update software configuration

### 3.2 Encoder Calibration (if equipped)
```bash
python3 firmware/motor_control/calibrate_encoders.py
```

Procedure:
1. Mark wheel and chassis alignment
2. Command 10 full rotations
3. Measure actual distance traveled
4. Calculate encoder counts per meter

### 3.3 Speed Calibration
```bash
python3 firmware/motor_control/calibrate_speed.py
```

For each motor:
1. Command various PWM values (20%, 40%, 60%, 80%, 100%)
2. Measure actual RPM with tachometer or timing method
3. Build PWM-to-RPM lookup table

### 3.4 PID Tuning
```bash
python3 firmware/motor_control/tune_pid.py --motor 0
```

**Tuning Procedure:**
1. Start with Ki=0, Kd=0
2. Increase Kp until oscillation begins, then reduce by 30%
3. Add Ki to eliminate steady-state error
4. Add Kd to dampen oscillations
5. Test with step changes in velocity command

Update `config/robot_params.yaml`:
```yaml
drive:
  pid:
    kp: <tuned_value>
    ki: <tuned_value>
    kd: <tuned_value>
    integral_limit: <value>
```

## 4. Kinematic Calibration

### 4.1 Wheel Diameter Measurement
Measure actual wheel diameter under load:
```
wheel_diameter_mm: <measured_value>
```

### 4.2 Wheelbase Calibration
```bash
python3 firmware/motor_control/calibrate_kinematics.py
```

Procedure:
1. Draw straight line on floor
2. Command robot to travel 1 meter forward
3. Measure actual distance
4. Adjust wheel diameter parameter accordingly

5. Draw perpendicular line
6. Command 90° rotation
7. Measure actual angle
8. Adjust wheelbase parameter

Update parameters:
```yaml
drive:
  wheel_diameter_mm: <calibrated_value>
  wheel_base_mm: <calibrated_value>
```

## 5. Kicker Calibration

### 5.1 Safety First
⚠️ **WARNING:** 
- Clear area in front of robot
- Wear safety glasses
- Start with minimum power settings

### 5.2 Solenoid Timing Test
```bash
python3 firmware/kicker_control/test_solenoid.py --power-level 1
```

Verify:
- Solenoid activates crisply
- Returns fully when deactivated
- No unusual sounds or heating

### 5.3 Power Level Calibration
```bash
python3 firmware/kicker_control/calibrate_power.py
```

For each power level:
1. Set charge time
2. Fire kicker (into safe backstop)
3. Measure ball distance
4. Adjust charge time for desired power

Update configuration:
```yaml
kicker:
  kick_power_levels:
    - level: 1
      charge_time_ms: <calibrated_value>
      description: "Light touch"
    - level: 2
      charge_time_ms: <calibrated_value>
      description: "Medium kick"
    - level: 3
      charge_time_ms: <calibrated_value>
      description: "Full power"
```

### 5.4 Cooldown Verification
1. Fire kicker repeatedly
2. Monitor solenoid temperature
3. Ensure cooldown period prevents overheating
4. Adjust `cooldown_ms` if necessary

## 6. Vision System Calibration

### 6.1 Color Calibration
```bash
python3 firmware/vision/calibrate_colors.py
```

**Ball Detection:**
1. Place orange ball in view
2. Adjust HSV ranges until ball is detected reliably
3. Test under various lighting conditions

**Field Detection:**
1. Point camera at green field
2. Adjust green color range
3. Verify field boundaries detected

**Goal Detection:**
1. Show blue and yellow goal colors
2. Calibrate each color range separately
3. Test detection at various distances

### 6.2 Distance Estimation
```bash
python3 firmware/vision/calibrate_distance.py
```

Procedure:
1. Place ball at known distances (0.5m, 1m, 1.5m, 2m, etc.)
2. Record apparent size in pixels
3. Fit distance estimation model
4. Validate with test measurements

## 7. System Integration Testing

### 7.1 Complete System Check
```bash
python3 tests/integration_test.py
```

Verifies:
- All motors respond correctly
- IMU data is reasonable
- Camera feed is available
- Kicker fires safely
- Emergency stop works

### 7.2 Field Testing
1. Place robot on competition field
2. Test basic behaviors:
   - Drive forward/backward
   - Rotate in place
   - Move sideways (strafe)
   - Ball detection and tracking
   - Kicking at target

### 7.3 Performance Validation
- Maximum speed meets requirements
- Rotation rate sufficient for competition
- Ball detection reliable at 2+ meters
- Kicking accuracy acceptable

## Calibration Schedule

| Component | Frequency | Trigger |
|-----------|-----------|---------|
| IMU | Every session | Temperature change >10°C |
| Camera | Monthly | Lens changed or impact |
| Motors | As needed | Performance degradation |
| Kicker | Every session | Battery changed |
| Vision Colors | Per venue | Lighting changes |

## Troubleshooting

### IMU Drift
- Recalibrate static bias
- Check mounting is secure
- Verify temperature compensation

### Poor Ball Detection
- Recalibrate color ranges
- Clean camera lens
- Check for glare/reflections

### Inconsistent Kicking
- Check battery voltage
- Verify solenoid mechanical operation
- Recalibrate power levels

### Odometry Errors
- Re-measure wheel diameter
- Recalibrate kinematics
- Check for wheel slippage

## Recording Calibration Data

Maintain a calibration log:
```
Date: YYYY-MM-DD
Venue: Location name
Lighting: Indoor/Outdoor, brightness
IMU Offsets: [x, y, z]
Camera RMS Error: X.XX pixels
Motor PID: [kp, ki, kd]
Notes: Any observations
```

Save calibration files with timestamps for rollback capability.
