# ES8388 Audio Codec Driver for MicroPython
# Direct port of Olimex ESP32-ADF es8388.c driver
# Based on: https://github.com/OLIMEX/ESP32-ADF/blob/master/SOFTWARE/esp-va-sdk/board_support_pkgs/olimex_esp32_adf/esp_codec/es8388/components/codec_es8388/es8388.c

from machine import I2C, Pin
import time

class ES8388:
    """ES8388 Audio Codec Driver - Direct port of Olimex implementation"""
    
    # ES8388 I2C Address
    ES8388_ADDR = 0x20  # Write address (0x10 << 1)
    
    # Register addresses from es8388.h
    ES8388_CONTROL1 = 0x00
    ES8388_CONTROL2 = 0x01
    ES8388_CHIPPOWER = 0x02
    ES8388_ADCPOWER = 0x03
    ES8388_DACPOWER = 0x04
    ES8388_CHIPLOPOW1 = 0x05
    ES8388_CHIPLOPOW2 = 0x06
    ES8388_ANAVOLMANAG = 0x07
    ES8388_MASTERMODE = 0x08
    
    # ADC registers
    ES8388_ADCCONTROL1 = 0x09
    ES8388_ADCCONTROL2 = 0x0A
    ES8388_ADCCONTROL3 = 0x0B
    ES8388_ADCCONTROL4 = 0x0C
    ES8388_ADCCONTROL5 = 0x0D
    ES8388_ADCCONTROL6 = 0x0E
    ES8388_ADCCONTROL7 = 0x0F
    ES8388_ADCCONTROL8 = 0x10
    ES8388_ADCCONTROL9 = 0x11
    ES8388_ADCCONTROL10 = 0x12
    ES8388_ADCCONTROL11 = 0x13
    ES8388_ADCCONTROL12 = 0x14
    ES8388_ADCCONTROL13 = 0x15
    ES8388_ADCCONTROL14 = 0x16
    
    # DAC registers
    ES8388_DACCONTROL1 = 0x17
    ES8388_DACCONTROL2 = 0x18
    ES8388_DACCONTROL3 = 0x19
    ES8388_DACCONTROL16 = 0x26
    ES8388_DACCONTROL17 = 0x27
    ES8388_DACCONTROL20 = 0x2A
    ES8388_DACCONTROL21 = 0x2B
    ES8388_DACCONTROL23 = 0x2D
    
    def __init__(self, i2c, address=0x10):
        """Initialize ES8388
        
        Args:
            i2c: I2C bus object
            address: I2C address (7-bit address, default 0x10)
        """
        self.i2c = i2c
        self.addr = address  # 7-bit address
        
        # Check if codec is present
        devices = i2c.scan()
        if self.addr not in devices:
            raise RuntimeError(f"ES8388 not found at address 0x{self.addr:02X}")
        print(f"ES8388 found at address 0x{self.addr:02X}")
    
    def write_reg(self, reg_addr, data):
        """Write to ES8388 register
        
        Direct port of es8388_write_reg() from Olimex code
        """
        self.i2c.writeto_mem(self.addr, reg_addr, bytes([data]))
    
    def read_reg(self, reg_addr):
        """Read from ES8388 register
        
        Direct port of es8388_read_reg() from Olimex code
        """
        return self.i2c.readfrom_mem(self.addr, reg_addr, 1)[0]
    
    def init(self):
        """Initialize ES8388 for ADC mode
        
        Direct port of es8388_init() from Olimex ESP32-ADF code
        Lines 246-313 from es8388.c
        """
        print("Initializing ES8388 codec (Olimex implementation)...")
        
        # Line 263: DAC mute
        self.write_reg(self.ES8388_DACCONTROL3, 0x04)
        
        # Line 265: Chip Control and Power Management
        self.write_reg(self.ES8388_CONTROL2, 0x50)
        self.write_reg(self.ES8388_CHIPPOWER, 0x00)  # Normal all and power up all
        self.write_reg(self.ES8388_MASTERMODE, 0x00)  # CODEC IN I2S SLAVE MODE
        
        # Line 270: CONTROL1 - Enable play & record mode
        self.write_reg(self.ES8388_CONTROL1, 0x12)
        
        # Line 271-276: DAC configuration
        self.write_reg(self.ES8388_DACCONTROL1, 0x18)  # 16bit I2S
        self.write_reg(self.ES8388_DACCONTROL2, 0x02)  # DACFsMode, SINGLE SPEED; DACFsRatio, 256
        self.write_reg(self.ES8388_DACCONTROL16, 0x00)  # Audio on LIN1&RIN1
        self.write_reg(self.ES8388_DACCONTROL17, 0x90)  # Only left DAC to left mixer enable 0db
        self.write_reg(self.ES8388_DACCONTROL20, 0x90)  # Only right DAC to right mixer enable 0db
        self.write_reg(self.ES8388_DACCONTROL21, 0x80)  # Set internal ADC and DAC use the same LRCK clock
        self.write_reg(self.ES8388_DACCONTROL23, 0x00)  # vroi=0
        
        # Line 278: Set DAC volume to 0dB (we'll implement this inline)
        # es8388_set_adc_dac_volume(MEDIA_HAL_CODEC_MODE_DECODE, 0)
        # For DECODE mode, this writes to DACCONTROL4 and DACCONTROL5
        # Volume: 0dB means write 0x00 to both registers
        # But we won't use DAC, so skip
        
        # Line 281: ADC configuration
        self.write_reg(self.ES8388_ADCPOWER, 0xFF)  # Power down ADC first
        self.write_reg(self.ES8388_ADCCONTROL1, 0x88)  # MIC PGA = 24dB
        self.write_reg(self.ES8388_ADCCONTROL3, 0x02)
        self.write_reg(self.ES8388_ADCCONTROL4, 0x0C)  # I2S-16BIT, LEFT ADC DATA = LIN1, RIGHT ADC DATA = RIN1
        self.write_reg(self.ES8388_ADCCONTROL5, 0x02)  # ADCFsMode, single SPEED, RATIO=256
        
        # Line 287: Set ADC volume to 0dB
        # es8388_set_adc_dac_volume(MEDIA_HAL_CODEC_MODE_ENCODE, 0)
        # For ENCODE mode, this writes to ADCCONTROL8 and ADCCONTROL9
        self.write_reg(self.ES8388_ADCCONTROL8, 0x00)  # 0dB
        self.write_reg(self.ES8388_ADCCONTROL9, 0x00)  # 0dB
        
        # Line 290: Power up ADC, Enable LIN&RIN, Power down MICBIAS
        self.write_reg(self.ES8388_ADCPOWER, 0x09)
        
        # Line 292-296: DAC power configuration
        # We'll keep DAC powered down since we only use ADC
        self.write_reg(self.ES8388_DACPOWER, 0xFC)  # Power down DAC
        
        # Line 299-312: ADC input routing
        # This writes ADCCONTROL2 based on input type
        # For LINE1 (default): write 0x00
        self.write_reg(self.ES8388_ADCCONTROL2, 0x00)  # Enable LIN1/RIN1 as ADC input
        
        print("ES8388 initialization complete")
    
    def start(self):
        """Start ADC capture
        
        Direct port of es8388_set_state() from Olimex code with START_STATE
        Lines 169-184 from es8388.c
        """
        print("Starting ES8388 ADC...")
        
        # Line 177-178: Restart state machine if needed
        # Read previous DACCONTROL21 value
        prev_data = self.read_reg(self.ES8388_DACCONTROL21)
        # For ADC mode, write 0x80 to DACCONTROL21
        self.write_reg(self.ES8388_DACCONTROL21, 0x80)
        data = self.read_reg(self.ES8388_DACCONTROL21)
        
        if prev_data != data:
            # Restart state machine
            self.write_reg(self.ES8388_CHIPPOWER, 0xF0)
            self.write_reg(self.ES8388_CHIPPOWER, 0x00)
        
        # Line 184: Power up ADC and line in
        # CRITICAL: This is where we write 0x00 to ADCPOWER for START state
        self.write_reg(self.ES8388_ADCPOWER, 0x00)
        
        print("ES8388 ADC started")
    
    def set_mic_gain(self, gain_db):
        """Set microphone gain
        
        Direct port of es8388_set_mic_gain() from Olimex code
        Lines 488-493 from es8388.c
        
        Args:
            gain_db: Gain in dB (0, 3, 6, 9, 12, 15, 18, 21, 24)
        """
        gain_n = gain_db // 3
        self.write_reg(self.ES8388_ADCCONTROL1, gain_n)
        print(f"Microphone gain set to {gain_db}dB (register value: 0x{gain_n:02X})")
    
    def read_all_registers(self):
        """Read and display all registers
        
        Direct port of es8388_read_all_registers() from Olimex code
        """
        print("\n=== ES8388 Register Dump (Olimex format) ===")
        for i in range(50):
            try:
                reg = self.read_reg(i)
                print(f"0x{i:02x}: 0x{reg:02x}")
            except:
                pass
        print("=" * 40)
