#!/usr/bin/env python3
"""
BNO055 9-DOF IMU Sensor Driver for Open Jr RoboCup Soccer Robot
Interfaces with Adafruit BNO055 via I2C on NVIDIA Jetson Orin Nano
"""

import smbus2
import time
import struct
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
import yaml

# BNO055 Register Addresses
BNO055_ADDRESS_A = 0x28
BNO055_ADDRESS_B = 0x29
BNO055_ID = 0xA0

# Page id register definition
BNO055_PAGE_ID_ADDR = 0x07

# PAGE0 REGISTER DEFINITION START
BNO055_CHIP_ID_ADDR = 0x00
BNO055_ACCEL_REV_ID_ADDR = 0x01
BNO055_MAG_REV_ID_ADDR = 0x02
BNO055_GYRO_REV_ID_ADDR = 0x03
BNO055_SW_REV_ID_LSB_ADDR = 0x04
BNO055_SW_REV_ID_MSB_ADDR = 0x05
BNO055_BL_REV_ID_ADDR = 0x06

# Accel data register
BNO055_ACCEL_DATA_X_LSB_ADDR = 0x08
BNO055_ACCEL_DATA_X_MSB_ADDR = 0x09
BNO055_ACCEL_DATA_Y_LSB_ADDR = 0x0A
BNO055_ACCEL_DATA_Y_MSB_ADDR = 0x0B
BNO055_ACCEL_DATA_Z_LSB_ADDR = 0x0C
BNO055_ACCEL_DATA_Z_MSB_ADDR = 0x0D

# Mag data register
BNO055_MAG_DATA_X_LSB_ADDR = 0x0E
BNO055_MAG_DATA_X_MSB_ADDR = 0x0F
BNO055_MAG_DATA_Y_LSB_ADDR = 0x10
BNO055_MAG_DATA_Y_MSB_ADDR = 0x11
BNO055_MAG_DATA_Z_LSB_ADDR = 0x12
BNO055_MAG_DATA_Z_MSB_ADDR = 0x13

# Gyro data registers
BNO055_GYRO_DATA_X_LSB_ADDR = 0x14
BNO055_GYRO_DATA_X_MSB_ADDR = 0x15
BNO055_GYRO_DATA_Y_LSB_ADDR = 0x16
BNO055_GYRO_DATA_Y_MSB_ADDR = 0x17
BNO055_GYRO_DATA_Z_LSB_ADDR = 0x18
BNO055_GYRO_DATA_Z_MSB_ADDR = 0x19

# Euler data registers
BNO055_EULER_H_LSB_ADDR = 0x1A
BNO055_EULER_H_MSB_ADDR = 0x1B
BNO055_EULER_R_LSB_ADDR = 0x1C
BNO055_EULER_R_MSB_ADDR = 0x1D
BNO055_EULER_P_LSB_ADDR = 0x1E
BNO055_EULER_P_MSB_ADDR = 0x1F

# Quaternion data registers
BNO055_QUATERNION_DATA_W_LSB_ADDR = 0x20
BNO055_QUATERNION_DATA_W_MSB_ADDR = 0x21
BNO055_QUATERNION_DATA_X_LSB_ADDR = 0x22
BNO055_QUATERNION_DATA_X_MSB_ADDR = 0x23
BNO055_QUATERNION_DATA_Y_LSB_ADDR = 0x24
BNO055_QUATERNION_DATA_Y_MSB_ADDR = 0x25
BNO055_QUATERNION_DATA_Z_LSB_ADDR = 0x26
BNO055_QUATERNION_DATA_Z_MSB_ADDR = 0x27

# Linear acceleration data registers
BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR = 0x28
BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR = 0x29
BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR = 0x2A
BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR = 0x2B
BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR = 0x2C
BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR = 0x2D

# Gravity data registers
BNO055_GRAVITY_DATA_X_LSB_ADDR = 0x2E
BNO055_GRAVITY_DATA_X_MSB_ADDR = 0x2F
BNO055_GRAVITY_DATA_Y_LSB_ADDR = 0x30
BNO055_GRAVITY_DATA_Y_MSB_ADDR = 0x31
BNO055_GRAVITY_DATA_Z_LSB_ADDR = 0x32
BNO055_GRAVITY_DATA_Z_MSB_ADDR = 0x33

# Temperature data register
BNO055_TEMP_ADDR = 0x34

# Status registers
BNO055_SYS_STATUS_ADDR = 0x39
BNO055_SELFTEST_RESULT_ADDR = 0x36
BNO055_INTR_STAT_ADDR = 0x37

BNO055_SYS_CLK_STAT_ADDR = 0x38
BNO055_SYS_ERR_ADDR = 0x3A

# Unit selection register
BNO055_UNIT_SEL_ADDR = 0x3B
BNO055_DATA_SELECT_ADDR = 0x3C

# Operation mode register
BNO055_OPR_MODE_ADDR = 0x3D
BNO055_PWR_MODE_ADDR = 0x3E

BNO055_SYS_TRIGGER_ADDR = 0x3F
BNO055_TEMP_SOURCE_ADDR = 0x40

# Axis remap registers
BNO055_AXIS_MAP_CONFIG_ADDR = 0x41
BNO055_AXIS_MAP_SIGN_ADDR = 0x42

# SIC registers
BNO055_SIC_MATRIX_0_LSB_ADDR = 0x43
BNO055_SIC_MATRIX_0_MSB_ADDR = 0x44
BNO055_SIC_MATRIX_1_LSB_ADDR = 0x45
BNO055_SIC_MATRIX_1_MSB_ADDR = 0x46
BNO055_SIC_MATRIX_2_LSB_ADDR = 0x47
BNO055_SIC_MATRIX_2_MSB_ADDR = 0x48
BNO055_SIC_MATRIX_3_LSB_ADDR = 0x49
BNO055_SIC_MATRIX_3_MSB_ADDR = 0x4A
BNO055_SIC_MATRIX_4_LSB_ADDR = 0x4B
BNO055_SIC_MATRIX_4_MSB_ADDR = 0x4C
BNO055_SIC_MATRIX_5_LSB_ADDR = 0x4D
BNO055_SIC_MATRIX_5_MSB_ADDR = 0x4E
BNO055_SIC_MATRIX_6_LSB_ADDR = 0x4F
BNO055_SIC_MATRIX_6_MSB_ADDR = 0x50
BNO055_SIC_MATRIX_7_LSB_ADDR = 0x51
BNO055_SIC_MATRIX_7_MSB_ADDR = 0x52
BNO055_SIC_MATRIX_8_LSB_ADDR = 0x53
BNO055_SIC_MATRIX_8_MSB_ADDR = 0x54

# Accelerometer Offset registers
BNO055_ACCEL_OFFSET_X_LSB_ADDR = 0x55
BNO055_ACCEL_OFFSET_X_MSB_ADDR = 0x56
BNO055_ACCEL_OFFSET_Y_LSB_ADDR = 0x57
BNO055_ACCEL_OFFSET_Y_MSB_ADDR = 0x58
BNO055_ACCEL_OFFSET_Z_LSB_ADDR = 0x59
BNO055_ACCEL_OFFSET_Z_MSB_ADDR = 0x5A

# Magnetometer Offset registers
BNO055_MAG_OFFSET_X_LSB_ADDR = 0x5B
BNO055_MAG_OFFSET_X_MSB_ADDR = 0x5C
BNO055_MAG_OFFSET_Y_LSB_ADDR = 0x5D
BNO055_MAG_OFFSET_Y_MSB_ADDR = 0x5E
BNO055_MAG_OFFSET_Z_LSB_ADDR = 0x5F
BNO055_MAG_OFFSET_Z_MSB_ADDR = 0x60

# Gyroscope Offset registers
BNO055_GYRO_OFFSET_X_LSB_ADDR = 0x61
BNO055_GYRO_OFFSET_X_MSB_ADDR = 0x62
BNO055_GYRO_OFFSET_Y_LSB_ADDR = 0x63
BNO055_GYRO_OFFSET_Y_MSB_ADDR = 0x64
BNO055_GYRO_OFFSET_Z_LSB_ADDR = 0x65
BNO055_GYRO_OFFSET_Z_MSB_ADDR = 0x66

# Radius registers
BNO055_ACCEL_RADIUS_LSB_ADDR = 0x67
BNO055_ACCEL_RADIUS_MSB_ADDR = 0x68
BNO055_MAG_RADIUS_LSB_ADDR = 0x69
BNO055_MAG_RADIUS_MSB_ADDR = 0x6A

# Power modes
POWER_MODE_NORMAL = 0x00
POWER_MODE_LOWPOWER = 0x01
POWER_MODE_SUSPEND = 0x02

# Operation modes
OPERATION_MODE_CONFIG = 0x00
OPERATION_MODE_ACCONLY = 0x01
OPERATION_MODE_MAGONLY = 0x02
OPERATION_MODE_GYRONLY = 0x03
OPERATION_MODE_ACCMAG = 0x04
OPERATION_MODE_ACCGYRO = 0x05
OPERATION_MODE_MAGGYRO = 0x06
OPERATION_MODE_AMG = 0x07
OPERATION_MODE_IMUPLUS = 0x08
OPERATION_MODE_COMPASS = 0x09
OPERATION_MODE_M4G = 0x0A
OPERATION_MODE_NDOF_FMC_OFF = 0x0B
OPERATION_MODE_NDOF = 0x0C

@dataclass
class IMUData:
    """Container for IMU sensor data"""
    # Euler angles (degrees)
    heading: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    
    # Quaternion (w, x, y, z)
    quaternion: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    
    # Linear acceleration (m/s²)
    linear_accel: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Gravity vector (m/s²)
    gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Angular velocity (rad/s)
    gyro: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Acceleration (m/s²)
    accel: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Magnetic field (µT)
    mag: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Temperature (°C)
    temperature: float = 0.0
    
    # System status
    system_status: int = 0
    calibration: Tuple[int, int, int, int] = (0, 0, 0, 0)  # sys, gyro, accel, mag


class BNO055:
    """
    BNO055 9-DOF IMU driver
    Supports fusion modes for absolute orientation
    """
    
    def __init__(self, i2c_bus: int = 1, address: int = BNO055_ADDRESS_A):
        self.i2c_bus = i2c_bus
        self.address = address
        self.bus: Optional[smbus2.SMBus] = None
        self.data = IMUData()
        
    def connect(self) -> bool:
        """Initialize I2C connection and configure sensor"""
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)
            
            # Check chip ID
            chip_id = self._read_byte(BNO055_CHIP_ID_ADDR)
            if chip_id != BNO055_ID:
                print(f"Invalid chip ID: {hex(chip_id)}, expected {hex(BNO055_ID)}")
                return False
                
            # Reset the sensor
            self._write_byte(BNO055_SYS_TRIGGER_ADDR, 0x3F)
            time.sleep(0.65)  # Wait for reset
            
            # Set to config mode
            self._set_mode(OPERATION_MODE_CONFIG)
            
            # Set power mode to normal
            self._write_byte(BNO055_PWR_MODE_ADDR, POWER_MODE_NORMAL)
            
            # Set sensor units
            self._write_byte(BNO055_UNIT_SEL_ADDR, 0x80)  # Use m/s², rad/s, degrees
            
            # Set axis remap (default orientation)
            self._write_byte(BNO055_AXIS_MAP_CONFIG_ADDR, 0x21)
            self._write_byte(BNO055_AXIS_MAP_SIGN_ADDR, 0x00)
            
            # Set to NDOF fusion mode
            self._set_mode(OPERATION_MODE_NDOF)
            
            time.sleep(0.02)  # Wait for mode switch
            
            print("BNO055 initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize BNO055: {e}")
            return False
            
    def _set_mode(self, mode: int):
        """Set operation mode"""
        self._write_byte(BNO055_OPR_MODE_ADDR, mode & 0xFF)
        time.sleep(0.02)  # Delay for mode switch
        
    def _read_byte(self, register: int) -> int:
        """Read a single byte from register"""
        return self.bus.read_byte_data(self.address, register)
        
    def _write_byte(self, register: int, value: int):
        """Write a single byte to register"""
        self.bus.write_byte_data(self.address, register, value)
        
    def _read_bytes(self, register: int, length: int) -> bytes:
        """Read multiple bytes from register"""
        return self.bus.read_i2c_block_data(self.address, register, length)
        
    def _read_word(self, register: int) -> int:
        """Read a 16-bit word from register"""
        data = self._read_bytes(register, 2)
        return data[0] | (data[1] << 8)
        
    def _read_signed_word(self, register: int) -> int:
        """Read a signed 16-bit word from register"""
        data = self._read_bytes(register, 2)
        value = data[0] | (data[1] << 8)
        if value >= 32768:
            value -= 65536
        return value
        
    def read_data(self) -> IMUData:
        """Read all sensor data"""
        if not self.bus:
            return self.data
            
        try:
            # Read Euler angles (degrees)
            euler_raw = self._read_bytes(BNO055_EULER_H_LSB_ADDR, 6)
            self.data.heading = struct.unpack('<h', bytes(euler_raw[0:2]))[0] / 16.0
            self.data.roll = struct.unpack('<h', bytes(euler_raw[2:4]))[0] / 16.0
            self.data.pitch = struct.unpack('<h', bytes(euler_raw[4:6]))[0] / 16.0
            
            # Read quaternion (scaled by 2^14)
            quat_raw = self._read_bytes(BNO055_QUATERNION_DATA_W_LSB_ADDR, 8)
            scale = 1.0 / (1 << 14)
            w = struct.unpack('<h', bytes(quat_raw[0:2]))[0] * scale
            x = struct.unpack('<h', bytes(quat_raw[2:4]))[0] * scale
            y = struct.unpack('<h', bytes(quat_raw[4:6]))[0] * scale
            z = struct.unpack('<h', bytes(quat_raw[6:8]))[0] * scale
            self.data.quaternion = (w, x, y, z)
            
            # Read linear acceleration (m/s²)
            lin_accel_raw = self._read_bytes(BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR, 6)
            self.data.linear_accel = tuple(
                struct.unpack('<h', bytes(lin_accel_raw[i:i+2]))[0] / 100.0
                for i in range(0, 6, 2)
            )
            
            # Read gravity vector (m/s²)
            gravity_raw = self._read_bytes(BNO055_GRAVITY_DATA_X_LSB_ADDR, 6)
            self.data.gravity = tuple(
                struct.unpack('<h', bytes(gravity_raw[i:i+2]))[0] / 100.0
                for i in range(0, 6, 2)
            )
            
            # Read gyroscope (rad/s)
            gyro_raw = self._read_bytes(BNO055_GYRO_DATA_X_LSB_ADDR, 6)
            self.data.gyro = tuple(
                struct.unpack('<h', bytes(gyro_raw[i:i+2]))[0] / 16.0 * 0.0174532925
                for i in range(0, 6, 2)
            )
            
            # Read accelerometer (m/s²)
            accel_raw = self._read_bytes(BNO055_ACCEL_DATA_X_LSB_ADDR, 6)
            self.data.accel = tuple(
                struct.unpack('<h', bytes(accel_raw[i:i+2]))[0] / 100.0
                for i in range(0, 6, 2)
            )
            
            # Read magnetometer (µT)
            mag_raw = self._read_bytes(BNO055_MAG_DATA_X_LSB_ADDR, 6)
            self.data.mag = tuple(
                struct.unpack('<h', bytes(mag_raw[i:i+2]))[0] / 16.0
                for i in range(0, 6, 2)
            )
            
            # Read temperature (°C)
            temp = self._read_byte(BNO055_TEMP_ADDR)
            self.data.temperature = temp if temp < 128 else temp - 256
            
            # Read system status
            self.data.system_status = self._read_byte(BNO055_SYS_STATUS_ADDR)
            
            # Read calibration status
            cal_stat = self._read_byte(BNO055_CALIB_STAT_ADDR)
            self.data.calibration = (
                (cal_stat >> 6) & 0x03,  # System
                (cal_stat >> 4) & 0x03,  # Gyro
                (cal_stat >> 2) & 0x03,  # Accelerometer
                cal_stat & 0x03          # Magnetometer
            )
            
        except Exception as e:
            print(f"Error reading BNO055 data: {e}")
            
        return self.data
        
    def get_orientation(self) -> Tuple[float, float, float]:
        """Get current orientation as (heading, roll, pitch) in degrees"""
        self.read_data()
        return (self.data.heading, self.data.roll, self.data.pitch)
        
    def get_linear_accel(self) -> Tuple[float, float, float]:
        """Get linear acceleration in m/s²"""
        self.read_data()
        return self.data.linear_accel
        
    def get_gyro(self) -> Tuple[float, float, float]:
        """Get angular velocity in rad/s"""
        self.read_data()
        return self.data.gyro
        
    def is_fully_calibrated(self) -> bool:
        """Check if all sensors are fully calibrated (level 3)"""
        self.read_data()
        return all(cal == 3 for cal in self.data.calibration)
        
    def get_calibration_offsets(self) -> dict:
        """Read calibration offsets from sensor"""
        self._set_mode(OPERATION_MODE_CONFIG)
        time.sleep(0.02)
        
        offsets = {}
        
        # Read accelerometer offsets
        offsets['accel'] = {
            'x': self._read_signed_word(BNO055_ACCEL_OFFSET_X_LSB_ADDR),
            'y': self._read_signed_word(BNO055_ACCEL_OFFSET_Y_LSB_ADDR),
            'z': self._read_signed_word(BNO055_ACCEL_OFFSET_Z_LSB_ADDR)
        }
        
        # Read magnetometer offsets
        offsets['mag'] = {
            'x': self._read_signed_word(BNO055_MAG_OFFSET_X_LSB_ADDR),
            'y': self._read_signed_word(BNO055_MAG_OFFSET_Y_LSB_ADDR),
            'z': self._read_signed_word(BNO055_MAG_OFFSET_Z_LSB_ADDR)
        }
        
        # Read gyroscope offsets
        offsets['gyro'] = {
            'x': self._read_signed_word(BNO055_GYRO_OFFSET_X_LSB_ADDR),
            'y': self._read_signed_word(BNO055_GYRO_OFFSET_Y_LSB_ADDR),
            'z': self._read_signed_word(BNO055_GYRO_OFFSET_Z_LSB_ADDR)
        }
        
        # Read radii
        offsets['accel_radius'] = self._read_word(BNO055_ACCEL_RADIUS_LSB_ADDR)
        offsets['mag_radius'] = self._read_word(BNO055_MAG_RADIUS_LSB_ADDR)
        
        # Return to NDOF mode
        self._set_mode(OPERATION_MODE_NDOF)
        
        return offsets
        
    def set_calibration_offsets(self, offsets: dict):
        """Write calibration offsets to sensor"""
        self._set_mode(OPERATION_MODE_CONFIG)
        time.sleep(0.02)
        
        # Write accelerometer offsets
        self._write_word(BNO055_ACCEL_OFFSET_X_LSB_ADDR, offsets['accel']['x'])
        self._write_word(BNO055_ACCEL_OFFSET_Y_LSB_ADDR, offsets['accel']['y'])
        self._write_word(BNO055_ACCEL_OFFSET_Z_LSB_ADDR, offsets['accel']['z'])
        
        # Write magnetometer offsets
        self._write_word(BNO055_MAG_OFFSET_X_LSB_ADDR, offsets['mag']['x'])
        self._write_word(BNO055_MAG_OFFSET_Y_LSB_ADDR, offsets['mag']['y'])
        self._write_word(BNO055_MAG_OFFSET_Z_LSB_ADDR, offsets['mag']['z'])
        
        # Write gyroscope offsets
        self._write_word(BNO055_GYRO_OFFSET_X_LSB_ADDR, offsets['gyro']['x'])
        self._write_word(BNO055_GYRO_OFFSET_Y_LSB_ADDR, offsets['gyro']['y'])
        self._write_word(BNO055_GYRO_OFFSET_Z_LSB_ADDR, offsets['gyro']['z'])
        
        # Write radii
        self._write_word(BNO055_ACCEL_RADIUS_LSB_ADDR, offsets['accel_radius'])
        self._write_word(BNO055_MAG_RADIUS_LSB_ADDR, offsets['mag_radius'])
        
        # Return to NDOF mode
        self._set_mode(OPERATION_MODE_NDOF)
        
    def _write_word(self, register: int, value: int):
        """Write a 16-bit word to register"""
        self._write_byte(register, value & 0xFF)
        self._write_byte(register + 1, (value >> 8) & 0xFF)
        
    def disconnect(self):
        """Close I2C connection"""
        if self.bus:
            self.bus.close()
            self.bus = None


def main():
    """Example usage of BNO055 IMU"""
    imu = BNO055(i2c_bus=1, address=BNO055_ADDRESS_A)
    
    if not imu.connect():
        print("Failed to connect to BNO055")
        return
        
    print("Reading IMU data (press Ctrl+C to stop)...")
    print("-" * 80)
    
    try:
        while True:
            data = imu.read_data()
            
            print(f"Heading: {data.heading:7.2f}° | "
                  f"Roll: {data.roll:7.2f}° | "
                  f"Pitch: {data.pitch:7.2f}°")
            print(f"Linear Accel: [{data.linear_accel[0]:6.2f}, {data.linear_accel[1]:6.2f}, {data.linear_accel[2]:6.2f}] m/s²")
            print(f"Gyro: [{data.gyro[0]:6.3f}, {data.gyro[1]:6.3f}, {data.gyro[2]:6.3f}] rad/s")
            print(f"Calibration: Sys={data.calibration[0]}, Gyro={data.calibration[1]}, "
                  f"Accel={data.calibration[2]}, Mag={data.calibration[3]}")
            print("-" * 80)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        imu.disconnect()


if __name__ == '__main__':
    main()
