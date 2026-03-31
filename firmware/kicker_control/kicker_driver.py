#!/usr/bin/env python3
"""
Kicker Solenoid Control for Open Jr RoboCup Soccer Robot
Controls solenoid via TIP120 transistor with safety features
"""

import RPi.GPIO as GPIO
import time
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class KickerConfig:
    """Configuration for kicker solenoid"""
    control_pin: int
    kick_duration_ms: int = 50
    cooldown_ms: int = 1000
    max_power_level: int = 3
    
@dataclass
class PowerLevel:
    """Power level configuration"""
    level: int
    charge_time_ms: int
    description: str

class KickerController:
    """
    Solenoid kicker controller using TIP120 transistor
    Implements power levels, cooldown, and safety features
    """
    
    def __init__(self, config: KickerConfig, power_levels: list[PowerLevel]):
        self.config = config
        self.power_levels = {pl.level: pl for pl in power_levels}
        self.last_kick_time: Optional[float] = None
        self.is_charging = False
        
    def setup(self):
        """Initialize GPIO pins"""
        GPIO.setup(self.config.control_pin, GPIO.OUT)
        GPIO.output(self.config.control_pin, GPIO.LOW)
        
    def _check_cooldown(self) -> bool:
        """Check if kicker has cooled down sufficiently"""
        if self.last_kick_time is None:
            return True
            
        elapsed = (time.time() - self.last_kick_time) * 1000  # Convert to ms
        return elapsed >= self.config.cooldown_ms
        
    def get_remaining_cooldown_ms(self) -> float:
        """Get remaining cooldown time in milliseconds"""
        if self.last_kick_time is None:
            return 0.0
            
        elapsed = (time.time() - self.last_kick_time) * 1000
        remaining = self.config.cooldown_ms - elapsed
        return max(0.0, remaining)
        
    def kick(self, power_level: int = 1) -> bool:
        """
        Execute a kick at specified power level
        
        Args:
            power_level: Power level (1-3), higher = stronger kick
            
        Returns:
            True if kick was successful, False if on cooldown
        """
        if power_level not in self.power_levels:
            print(f"Invalid power level: {power_level}")
            return False
            
        if not self._check_cooldown():
            remaining = self.get_remaining_cooldown_ms()
            print(f"Kicker on cooldown, wait {remaining:.0f}ms")
            return False
            
        # Get charge time for power level
        charge_time = self.power_levels[power_level].charge_time_ms
        
        try:
            # Activate solenoid
            GPIO.output(self.config.control_pin, GPIO.HIGH)
            self.is_charging = True
            
            # Wait for charge time
            time.sleep(charge_time / 1000.0)
            
            # Deactivate solenoid (kick!)
            GPIO.output(self.config.control_pin, GPIO.LOW)
            self.is_charging = False
            
            # Record kick time for cooldown
            self.last_kick_time = time.time()
            
            print(f"Kick executed at power level {power_level} "
                  f"({self.power_levels[power_level].description})")
            return True
            
        except Exception as e:
            print(f"Kick failed: {e}")
            self.is_charging = False
            GPIO.output(self.config.control_pin, GPIO.LOW)
            return False
            
    def emergency_disable(self):
        """Immediately disable kicker (safety function)"""
        GPIO.output(self.config.control_pin, GPIO.LOW)
        self.is_charging = False
        print("Kicker emergency disabled")
        
    def get_status(self) -> dict:
        """Get current kicker status"""
        return {
            'ready': self._check_cooldown(),
            'cooldown_remaining_ms': self.get_remaining_cooldown_ms(),
            'is_charging': self.is_charging,
            'available_power_levels': list(self.power_levels.keys())
        }


def load_kicker_config(config_file: str) -> tuple[KickerConfig, list[PowerLevel]]:
    """Load kicker configuration from YAML file"""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    kicker_cfg = config['kicker']
    
    kicker_config = KickerConfig(
        control_pin=kicker_cfg['control_pin'],
        kick_duration_ms=kicker_cfg.get('kick_duration_ms', 50),
        cooldown_ms=kicker_cfg.get('cooldown_ms', 1000),
        max_power_level=kicker_cfg.get('max_power_level', 3)
    )
    
    power_levels = []
    for pl in kicker_cfg.get('power_levels', []):
        power_levels.append(PowerLevel(
            level=pl['level'],
            charge_time_ms=pl['charge_time_ms'],
            description=pl.get('description', f'Level {pl["level"]}')
        ))
    
    return kicker_config, power_levels


def main():
    """Example usage of kicker control system"""
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        # Load configuration
        config, power_levels = load_kicker_config('/workspace/config/kicker_pins.yaml')
        
        # Initialize kicker
        kicker = KickerController(config, power_levels)
        kicker.setup()
        
        print("Kicker Controller Initialized")
        print("=" * 60)
        print(f"Available power levels: {list(kicker.power_levels.keys())}")
        print(f"Cooldown: {config.cooldown_ms}ms")
        print("=" * 60)
        
        # Test kicks at different power levels
        for level in [1, 2, 3]:
            print(f"\nTesting power level {level}...")
            
            status = kicker.get_status()
            if status['ready']:
                success = kicker.kick(power_level=level)
                if success:
                    print(f"✓ Kick successful!")
                else:
                    print(f"✗ Kick failed")
            else:
                print(f"Waiting for cooldown... ({status['cooldown_remaining_ms']:.0f}ms)")
                time.sleep(status['cooldown_remaining_ms'] / 1000.0 + 0.1)
                success = kicker.kick(power_level=level)
                
            time.sleep(1.5)  # Wait for cooldown between tests
            
        print("\n" + "=" * 60)
        print("Test complete!")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


if __name__ == '__main__':
    main()
