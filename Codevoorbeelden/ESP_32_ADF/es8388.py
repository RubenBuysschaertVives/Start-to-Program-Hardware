# ES8388 Audio Codec Driver for MicroPython
# Simplified driver for microphone input on ESP32-ADF
# Based on ES8388 datasheet and ESP-ADF examples

from machine import I2C, Pin
import time

class ES8388:
    """ES8388 Audio Codec Driver - Basic ADC (Microphone) Support"""

    # ES8388 I2C address (when CE pin is low)
    ADDR = 0x10

    # Register addresses (subset for basic microphone input)
    REG_CHIP_CONTROL1 = 0x00
    REG_CHIP_CONTROL2 = 0x01
    REG_CHIP_POWER_MAN = 0x02
    REG_ADC_POWER_MAN = 0x03
    REG_DAC_POWER_MAN = 0x04
    REG_CHIP_LOW_POWER1 = 0x05
    REG_CHIP_LOW_POWER2 = 0x06
    REG_ANALOG_VOLTAGE_MAN = 0x07
    REG_MASTER_MODE_CONTROL = 0x08
    REG_ADC_CONTROL1 = 0x09
    REG_ADC_CONTROL2 = 0x0A
    REG_ADC_CONTROL3 = 0x0B
    REG_ADC_CONTROL4 = 0x0C
    REG_ADC_CONTROL5 = 0x0D
    REG_ADC_CONTROL6 = 0x0E
    REG_ADC_CONTROL7 = 0x0F
    REG_ADC_CONTROL8 = 0x10
    REG_ADC_CONTROL9 = 0x11
    REG_ADC_CONTROL10 = 0x12
    REG_ADC_CONTROL11 = 0x13
    REG_ADC_CONTROL12 = 0x14
    REG_ADC_CONTROL13 = 0x15
    REG_ADC_CONTROL14 = 0x16

    def __init__(self, i2c, address=ADDR):
        """Initialize ES8388 codec

        Args:
            i2c: I2C bus object
            address: I2C address (default 0x10)
        """
        self.i2c = i2c
        self.addr = address

        # Check if codec is present
        devices = i2c.scan()
        if self.addr not in devices:
            raise Exception(f"ES8388 not found at address {hex(self.addr)}. Found: {[hex(d) for d in devices]}")

        print(f"ES8388 found at address {hex(self.addr)}")

    def write_reg(self, reg, value):
        """Write to ES8388 register"""
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def read_reg(self, reg):
        """Read from ES8388 register"""
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def init_adc(self, sample_rate=16000):
        """Initialize ES8388 for ADC (microphone input)

        Args:
            sample_rate: Audio sample rate (8000, 16000, 44100, 48000)
        """
        print("Initializing ES8388 for ADC mode...")

        # Reset codec
        self.write_reg(self.REG_CHIP_CONTROL1, 0x80)
        time.sleep_ms(100)
        self.write_reg(self.REG_CHIP_CONTROL1, 0x00)
        time.sleep_ms(50)

        # Power down everything first
        self.write_reg(self.REG_CHIP_POWER_MAN, 0xFF)
        self.write_reg(self.REG_ADC_POWER_MAN, 0xFF)
        self.write_reg(self.REG_DAC_POWER_MAN, 0xFF)
        time.sleep_ms(100)

        # Configure before powering up
        # Chip control - MCLK divider and basic setup
        self.write_reg(self.REG_CHIP_CONTROL2, 0x50)  # MCLK/2, normal polarity
        
        # Power up chip and Vref
        self.write_reg(self.REG_CHIP_POWER_MAN, 0x00)  # Power up all analog circuits
        
        # Master mode control - Slave mode (ESP32 is master)
        self.write_reg(self.REG_MASTER_MODE_CONTROL, 0x00)
        
        # CRITICAL: Enable play & record mode (CONTROL1 = 0x12)
        # This enables the audio paths for ADC and DAC
        self.write_reg(self.REG_CHIP_CONTROL1, 0x12)
        
        # Analog voltage management
        self.write_reg(self.REG_ANALOG_VOLTAGE_MAN, 0x7C)

        # ADC controls - configure EXACTLY like Olimex official code
        # Power down ADC first
        self.write_reg(self.REG_ADC_POWER_MAN, 0xFF)
        
        # ADC Control 1: 0x88 = MIC PGA 24dB
        self.write_reg(self.REG_ADC_CONTROL1, 0x88)

        # ADC Control 3: 0x02 (from Olimex code)
        self.write_reg(self.REG_ADC_CONTROL3, 0x02)

        # ADC Control 4: 0x0c = I2S-16BIT, LEFT ADC DATA = LIN1, RIGHT ADC DATA = RIN1
        self.write_reg(self.REG_ADC_CONTROL4, 0x0C)

        # ADC Control 5: 0x02 = ADCFsMode, single SPEED, RATIO=256
        self.write_reg(self.REG_ADC_CONTROL5, 0x02)

        # ADC volume will be set by set_adc_volume later
        # ADC Control 8,9: Volume control (0x00 = 0dB)
        self.write_reg(self.REG_ADC_CONTROL8, 0x00)
        self.write_reg(self.REG_ADC_CONTROL9, 0x00)

        # Power up ADC (bits: 7=ADCR, 6=ADCL, 5=AINR, 4=AINL, 3=MicBias, 2=ADCR-Mod, 1=ADCL-Mod)
        # Olimex board: Use 0x09 - power down MicBias, power up left/right ADC and line inputs
        # 0x09 = 0b00001001 = ADCR/ADCL powered up, AINR/AINL powered up, MicBias OFF
        self.write_reg(self.REG_ADC_POWER_MAN, 0x09)
        time.sleep_ms(50)

        # **CRITICAL**: ADC Control 2 MUST be written AFTER ADC power-up
        # This routes the physical microphone inputs (LIN1/RIN1) to the ADC
        # 0x00 = Enable LIN1/RIN1 as ADC input (default for Olimex board)
        # From Olimex: This MUST come after ADCPOWER to route inputs correctly
        self.write_reg(self.REG_ADC_CONTROL2, 0x00)
        time.sleep_ms(10)

        # **CRITICAL STATE MACHINE RESTART** (from Olimex code lines 177-178)
        # After configuration changes, must restart the ES8388 state machine
        # This ensures all register changes take effect
        self.write_reg(self.REG_CHIP_POWER_MAN, 0xF0)  # Stop state machine
        time.sleep_ms(10)
        self.write_reg(self.REG_CHIP_POWER_MAN, 0x00)  # Restart state machine
        time.sleep_ms(50)

        # Keep DAC powered down (we don't use it)
        self.write_reg(self.REG_DAC_POWER_MAN, 0xFF)

        print("ES8388 ADC initialization complete")

    def start_adc(self):
        """Start ADC capture - MUST be called after init_adc()
        
        From Olimex es8388.c line 184 (es8388_set_state with START_STATE):
        When starting ADC mode, write ADCPOWER = 0x00 to fully power up ADC
        """
        # CRITICAL: Write 0x00 to ADCPOWER when STARTING capture (not init)
        # 0x00 = Full power-up: ADCR, ADCL, AINR, AINL all powered up
        # This is different from init where we use 0x09
        print("Starting ADC capture (full power-up)...")
        self.write_reg(self.REG_ADC_POWER_MAN, 0x00)  # Full ADC power-up for capture
        time.sleep_ms(50)
        print("ADC capture started")

    def set_mic_gain(self, gain=0):
        """Set microphone input PGA gain

        Args:
            gain: Gain in dB (0-24 in 3dB steps)
        """
        # ADC_CONTROL1: MIC PGA gain
        # 0x00 = 0dB, 0x11 = 3dB, 0x22 = 6dB, ..., 0x88 = 24dB
        gain_val = min(max(gain // 3, 0), 8)
        reg_value = gain_val * 0x11
        self.write_reg(self.REG_ADC_CONTROL1, reg_value)
        print(f"Microphone gain set to {gain_val * 3}dB (ADC_CONTROL1 = 0x{reg_value:02X})")

    def set_adc_volume(self, volume=0):
        """Set ADC digital volume

        Args:
            volume: Volume in dB (-96 to 0, 0.5dB steps)
        """
        # 0 = 0dB, 192 = -96dB
        vol_val = max(0, min(192, -volume * 2))
        self.write_reg(self.REG_ADC_CONTROL8, vol_val)
        self.write_reg(self.REG_ADC_CONTROL9, vol_val)
        print(f"ADC volume set to {-vol_val/2}dB")

    def dump_registers(self):
        """Dump all important registers for debugging"""
        print("\n=== ES8388 Register Dump ===")
        regs = [
            ("CHIP_CONTROL1", 0x00),
            ("CHIP_CONTROL2", 0x01),
            ("CHIP_POWER_MAN", 0x02),
            ("ADC_POWER_MAN", 0x03),
            ("DAC_POWER_MAN", 0x04),
            ("CHIP_LOW_POWER1", 0x05),
            ("CHIP_LOW_POWER2", 0x06),
            ("ANALOG_VOLTAGE_MAN", 0x07),
            ("MASTER_MODE_CONTROL", 0x08),
            ("ADC_CONTROL1", 0x09),
            ("ADC_CONTROL2", 0x0A),
            ("ADC_CONTROL3", 0x0B),
            ("ADC_CONTROL4", 0x0C),
            ("ADC_CONTROL5", 0x0D),
            ("ADC_CONTROL6", 0x0E),
            ("ADC_CONTROL7", 0x0F),
            ("ADC_CONTROL8", 0x10),
            ("ADC_CONTROL9", 0x11),
            ("ADC_CONTROL10", 0x12),
            ("ADC_CONTROL14", 0x16),
        ]

        for name, addr in regs:
            try:
                value = self.read_reg(addr)
                print(f"  {name:25} (0x{addr:02X}): 0x{value:02X} ({value:08b}b)")
            except Exception as e:
                print(f"  {name:25} (0x{addr:02X}): ERROR - {e}")

        print("===========================")

    def test_codec_communication(self):
        """Test if codec is responding correctly by reading/writing a register"""
        print("\n=== Testing ES8388 Communication ===")
        
        # Test register: CHIP_CONTROL2 (can be safely read/written)
        test_reg = 0x01
        
        # Read original value
        original = self.read_reg(test_reg)
        print(f"Original CHIP_CONTROL2 value: 0x{original:02X}")
        
        # Write a test value (0x51 instead of 0x50)
        test_value = 0x51
        self.write_reg(test_reg, test_value)
        time.sleep_ms(10)
        
        # Read back
        readback = self.read_reg(test_reg)
        print(f"After writing 0x{test_value:02X}, read back: 0x{readback:02X}")
        
        # Restore original
        self.write_reg(test_reg, original)
        time.sleep_ms(10)
        restored = self.read_reg(test_reg)
        print(f"After restoring 0x{original:02X}, read back: 0x{restored:02X}")
        
        if readback == test_value and restored == original:
            print("✓ Codec communication is WORKING correctly")
        else:
            print("✗ Codec communication FAILED - register writes not taking effect!")
        
        print("=====================================\n")
