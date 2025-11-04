# ESP32-ADF Troubleshooting Guide

Quick reference for common issues and solutions.

## Problem: No Beat Detection

### Symptoms
- LEDs don't flash when you play bass drum sounds
- Serial console shows no "Beat detected!" messages

### Solutions

**1. Check Audio Level**
```python
# In serial console (REPL), monitor amplitude values
# Look for lines showing amplitude when you make noise
```
- If amplitudes are below 1000: Increase microphone gain
- If amplitudes never change: Check I2S/ES8388 initialization

**2. Adjust Microphone Gain**
```python
# In strudel_adf.py, line ~140
codec.set_mic_gain(18)  # Try higher value (was 12)
```
- Range: 0-24 dB
- Start at 12, increase to 18 or 24 if too quiet

**3. Lower Beat Threshold**
```python
# In strudel_adf.py or config.py
BEAT_THRESHOLD = 2000  # Try lower value (was 5000)
```
- Too high = misses beats
- Too low = false triggers

**4. Test with Hand Clap**
- Clap your hands near the microphones
- Should trigger LED effect
- If this works, bass drum threshold needs adjustment

**5. Verify Microphone Position**
- Microphones are on the ESP32-ADF board
- Point board toward sound source
- Don't cover microphone holes

---

## Problem: Too Many False Triggers

### Symptoms
- LEDs flash constantly
- Triggers on background noise

### Solutions

**1. Increase Beat Threshold**
```python
BEAT_THRESHOLD = 8000  # Higher value (was 5000)
```

**2. Increase Cooldown Period**
```python
BEAT_COOLDOWN_MS = 200  # Longer cooldown (was 100)
```

**3. Reduce Microphone Gain**
```python
codec.set_mic_gain(6)  # Lower gain (was 12)
```

**4. Check Environment**
- Move away from loud ambient noise
- Reduce volume of other sounds
- Isolate bass drum sound source

---

## Problem: ES8388 Not Found

### Error Message
```
ES8388 not found at address 0x10. Found: []
```

### Solutions

**1. Check I2C Scan Results**
```python
# In serial console
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(23), sda=Pin(18), freq=100000)
print(i2c.scan())
```
- Should show `[16]` (0x10 in decimal)

**2. Verify I2C Pins**
- GPIO 18 = SDA (should be automatic on ESP32-ADF)
- GPIO 23 = SCL (should be automatic on ESP32-ADF)

**3. Try Different I2C Address**
```python
# In es8388.py, try address 0x11 instead
codec = ES8388(i2c, address=0x11)
```

**4. Check Board**
- Verify it's actually an ESP32-ADF board
- Check for loose connections or damaged components

---

## Problem: LED Strip Not Working

### Symptoms
- No lights on LED strip
- LEDs stay off even when triggered

### Solutions

**1. Verify Wiring**
```
Data:   UEXT Pin 3 (GPIO 19) -> LED Strip DIN
Ground: UEXT Pin 2 (GND)     -> LED Strip GND
Power:  External 5V          -> LED Strip 5V
```

**2. Check Power Supply**
- 60 LEDs need 5V 4A supply minimum
- Measure voltage at LED strip (should be ~5V)
- Check GND is shared between ESP32 and power supply

**3. Test LED Strip Manually**
```python
# In serial console
from machine import Pin
import neopixel
np = neopixel.NeoPixel(Pin(19), 60, bpp=3)
np[0] = (255, 0, 0)  # First LED red
np.write()
```

**4. Check LED Type**
```python
# If you have RGBW LEDs (4 color channels)
np = neopixel.NeoPixel(Pin(19), 60, bpp=4)  # Change bpp=3 to bpp=4
```

**5. Verify GPIO Pin**
- Should be GPIO 19 (UEXT pin 3)
- Try different pin if UEXT is damaged

---

## Problem: WiFi Won't Connect

### Symptoms
- "Trying to connect to WiFi..." repeats forever
- Never shows "Connected to WiFi"

### Solutions

**1. Check Credentials**
```python
WIFI_SSID = 'YourExactSSID'      # Case sensitive!
WIFI_PASSWORD = 'YourExactPassword'  # Case sensitive!
```

**2. Check WiFi Band**
- ESP32 only supports 2.4 GHz WiFi
- Disable 5 GHz if dual-band router

**3. Check WiFi Strength**
- Move closer to router
- Check router is broadcasting SSID

**4. Manual Connection Test**
```python
# In serial console
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()  # Should show available networks
wlan.connect('SSID', 'PASSWORD')
wlan.isconnected()  # Should return True after ~10 seconds
```

---

## Problem: MQTT Won't Connect

### Symptoms
- WiFi connects but MQTT fails
- Error: "Unable to connect to MQTT broker"

### Solutions

**1. Verify MQTT Settings**
```python
MQTT_BROKER = 'mqtt.rubu.be'  # Correct broker address?
MQTT_PORT = 1885               # Correct port?
MQTT_USER = 'strudel'         # Correct username?
MQTT_PASSWORD = 'qifj3258'    # Correct password?
```

**2. Test MQTT Broker**
- Use MQTT Explorer or mosquitto_sub on PC
- Verify broker is reachable
- Check if SSL/TLS is required

**3. Check SSL Setting**
```python
# In strudel_adf.py
mqtt_client = MQTTClient("esp32_adf", MQTT_BROKER,
                         port=MQTT_PORT, ssl=True, ...)
```
- Try `ssl=False` if broker doesn't use SSL

**4. Network Firewall**
- Check if port 1885 is blocked
- Try from different network

---

## Problem: Colors Don't Change from Web App

### Symptoms
- Web app works but colors don't update on ESP32
- No messages in serial console when color selected

### Solutions

**1. Verify Topic Subscription**
```python
# Should see this in console at startup
"Subscribed to topic: strudel/color"
```

**2. Check MQTT Topic**
```python
# In strudel_adf.py
MQTT_COLOR_TOPIC = 'strudel/color'  # Must match web app
```

**3. Monitor MQTT Messages**
- Watch serial console for incoming messages
- Should show: "Color set to: red (255, 0, 0)"

**4. Test with MQTT Client**
```bash
# Send test message using mosquitto_pub
mosquitto_pub -h mqtt.rubu.be -p 1885 -u strudel -P qifj3258 \
  -t "strudel/color" -m '{"s":"red","mode":"flash"}'
```

---

## Problem: Memory Error

### Error Message
```
MemoryError: memory allocation failed
```

### Solutions

**1. Reduce Buffer Size**
```python
AUDIO_BUFFER_SIZE = 256  # Reduce from 512
I2S_BUFFER_SIZE = 2048   # Reduce from 4096
```

**2. Reduce Sample Rate**
```python
I2S_SAMPLE_RATE = 8000  # Lower from 16000
```

**3. Free Memory**
```python
import gc
gc.collect()  # Force garbage collection
```

---

## Problem: I2S Error

### Error Message
```
OSError: I2S init failed
```

### Solutions

**1. Verify I2S Pins**
```python
I2S_SCK = 5   # Bit clock
I2S_WS = 25   # Word select
I2S_SD = 35   # Data in
```

**2. Check Pin Conflicts**
- Ensure pins aren't used elsewhere
- GPIO 35 is input-only (correct for microphone)

**3. Deinit Previous I2S**
```python
# In serial console
from machine import I2S
i2s = I2S(0)
i2s.deinit()
```

---

## Diagnostic Commands

### Check System Status
```python
# Run in serial console (REPL)
import sys
print("Free memory:", gc.mem_free())
print("MicroPython version:", sys.version)

import network
wlan = network.WLAN(network.STA_IF)
print("WiFi connected:", wlan.isconnected())
print("IP address:", wlan.ifconfig()[0])

from machine import I2C, Pin
i2c = I2C(0, scl=Pin(23), sda=Pin(18))
print("I2C devices:", [hex(d) for d in i2c.scan()])
```

### Monitor Audio Levels
```python
# Add to detect_beat() function temporarily
print(f"Amplitude: {avg_amplitude}")
```

### Test Individual Components
```python
# Test LED
np.fill((255, 0, 0))
np.write()

# Test MQTT
mqtt_client.publish("test/topic", "Hello")

# Test ES8388
print("ES8388 register 0x00:", hex(codec.read_reg(0x00)))
```

---

## Getting More Help

1. **Check Serial Console**
   - Always run with serial console open
   - Look for error messages and warnings
   - Monitor beat detection amplitude values

2. **Enable Debug Output**
   - Uncomment print statements in code
   - Add `print()` statements at key points

3. **Test Components Individually**
   - Test WiFi alone
   - Test MQTT alone
   - Test LEDs alone
   - Test audio alone
   - Combine once each works

4. **Check Documentation**
   - README.md for full setup instructions
   - WIRING.txt for connection diagram
   - MicroPython docs for library reference

5. **Verify Hardware**
   - Visual inspection of connections
   - Multimeter to check voltages
   - Try known-good components
