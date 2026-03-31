#!/usr/bin/env python3
"""
Motor Control Module for Open Jr RoboCup Soccer Robot
Controls three Pololu G2 High Power Motor Drivers via NVIDIA Jetson GPIO
"""

import RPi.GPIO as GPIO
import time
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class MotorConfig:
    """Configuration for a single motor"""
    pwm_pin: int
    dir_pin: int
    en_pin: int
    fault_pin: int
    inverted: bool = False

@dataclass
class MotorState:
    """Current state of a motor"""
    speed: float  # -1.0 to 1.0
    enabled: bool
    fault: bool

class MotorDriver:
    """
    Motor driver class for Pololu G2 24V21
    Controls one motor with PWM speed and direction control
    """
    
    def __init__(self, config: MotorConfig):
        self.config = config
        self.state = MotorState(speed=0.0, enabled=False, fault=False)
        self.pwm = None
        
    def setup(self, pwm_frequency: int = 20000):
        """Initialize GPIO pins for this motor"""
        GPIO.setup(self.config.pwm_pin, GPIO.OUT)
        GPIO.setup(self.config.dir_pin, GPIO.OUT)
        GPIO.setup(self.config.en_pin, GPIO.OUT)
        GPIO.setup(self.config.fault_pin, GPIO.IN)
        
        # Setup PWM
        self.pwm = GPIO.PWM(self.config.pwm_pin, pwm_frequency)
        self.pwm.start(0)
        
        # Disable motor initially
        self.disable()
        
    def enable(self):
        """Enable the motor driver"""
        GPIO.output(self.config.en_pin, GPIO.HIGH)
        self.state.enabled = True
        
    def disable(self):
        """Disable the motor driver"""
        GPIO.output(self.config.en_pin, GPIO.LOW)
        self.set_speed(0.0)
        self.state.enabled = False
        
    def set_speed(self, speed: float):
        """
        Set motor speed from -1.0 (full reverse) to 1.0 (full forward)
        """
        speed = max(-1.0, min(1.0, speed))  # Clamp to [-1, 1]
        
        if self.config.inverted:
            speed = -speed
            
        self.state.speed = speed
        
        if speed >= 0:
            GPIO.output(self.config.dir_pin, GPIO.HIGH)
            duty_cycle = speed * 100.0
        else:
            GPIO.output(self.config.dir_pin, GPIO.LOW)
            duty_cycle = abs(speed) * 100.0
            
        self.pwm.ChangeDutyCycle(duty_cycle)
        
    def check_fault(self) -> bool:
        """Check if motor driver has a fault condition"""
        fault = GPIO.input(self.config.fault_pin) == GPIO.LOW
        self.state.fault = fault
        return fault
        
    def emergency_stop(self):
        """Immediately stop the motor"""
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.config.en_pin, GPIO.LOW)
        self.state.speed = 0.0
        self.state.enabled = False


class OmniDriveController:
    """
    Omnidirectional drive controller for 3-wheel configuration
    Converts velocity commands to individual motor speeds
    """
    
    def __init__(self, motors: list[MotorDriver], wheel_base_m: float, wheel_radius_m: float):
        self.motors = motors
        self.wheel_base = wheel_base_m  # Distance from center to wheel
        self.wheel_radius = wheel_radius_m
        
        # Motor angles for omnidirectional drive (120 degrees apart)
        self.motor_angles = [
            0.0,                    # Front motor (0 degrees)
            2 * 3.14159 / 3,       # Rear left (120 degrees)
            4 * 3.14159 / 3        # Rear right (240 degrees)
        ]
        
    def set_velocity(self, vx: float, vy: float, omega: float):
        """
        Set robot velocity in body frame
        vx: forward velocity (m/s)
        vy: sideways velocity (m/s)
        omega: angular velocity (rad/s)
        """
        for i, motor in enumerate(self.motors):
            angle = self.motor_angles[i]
            
            # Calculate motor speed using inverse kinematics
            motor_speed = (
                vx * 3.14159 / 180.0 + 
                vy * 3.14159 / 180.0 + 
                omega * self.wheel_base
            ) / self.wheel_radius
            
            # Normalize to [-1, 1] range
            motor_speed = max(-1.0, min(1.0, motor_speed))
            
            motor.set_speed(motor_speed)
            
    def stop(self):
        """Stop all motors"""
        for motor in self.motors:
            motor.emergency_stop()
            
    def check_all_faults(self) -> list[int]:
        """Check all motors for faults, return list of faulty motor indices"""
        faults = []
        for i, motor in enumerate(self.motors):
            if motor.check_fault():
                faults.append(i)
        return faults


def load_motor_config(config_file: str) -> list[MotorConfig]:
    """Load motor configuration from YAML file"""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    motor_configs = []
    for motor_cfg in config['motors']:
        motor_configs.append(MotorConfig(
            pwm_pin=motor_cfg['pwm_pin'],
            dir_pin=motor_cfg['dir_pin'],
            en_pin=motor_cfg['en_pin'],
            fault_pin=motor_cfg['fault_pin'],
            inverted=motor_cfg.get('inverted', False)
        ))
    
    return motor_configs


def main():
    """Example usage of motor control system"""
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        # Load configuration
        configs = load_motor_config('/workspace/config/motor_pins.yaml')
        
        # Initialize motors
        motors = [MotorDriver(cfg) for cfg in configs]
        for motor in motors:
            motor.setup()
            
        # Create drive controller
        controller = OmniDriveController(
            motors=motors,
            wheel_base_m=0.15,
            wheel_radius_m=0.036
        )
        
        # Enable all motors
        for motor in motors:
            motor.enable()
            
        # Test movement
        print("Moving forward...")
        controller.set_velocity(0.5, 0.0, 0.0)
        time.sleep(2.0)
        
        print("Strafing left...")
        controller.set_velocity(0.0, -0.3, 0.0)
        time.sleep(2.0)
        
        print("Rotating...")
        controller.set_velocity(0.0, 0.0, 1.0)
        time.sleep(2.0)
        
        print("Stopping...")
        controller.stop()
        
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
