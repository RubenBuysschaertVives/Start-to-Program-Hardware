# ESP32-ADF Bass Drum LED Controller

MicroPython project for the Olimex ESP32-ADF board that detects bass drum hits using the built-in microphones and controls an RGB LED strip with colors selected via MQTT.

## Features

- **Bass drum detection** using built-in stereo microphones
- **MQTT color control** from web app or Strudel
- **Two LED effects**: Flash (all LEDs at once) and Travel (wave effect)
- **ES8388 audio codec** for high-quality audio input
- **Real-time audio processing** at 16kHz sample rate
- **WiFi and MQTT** connectivity

## Hardware Requirements

### Main Board
- **Olimex ESP32-ADF** development board with:
  - ESP32-WROVER-B module
  - ES8388 audio codec
  - Built-in stereo microphones
  - UEXT connector for expansion

### LED Strip
- **WS2813 RGB LED strip** (60 LEDs per meter)
  - Compatible with WS2812B and similar addressable RGB LEDs
  - Data: GPIO 19 (UEXT connector)
  - GND: UEXT connector pin 2
  - Power: External 5V supply (recommended for 60 LEDs)

## Wiring Connections

### UEXT Connector Pinout

```
Pin 1:  3.3V       (not used for LEDs - use external 5V)
Pin 2:  GND        -> LED strip GND
Pin 3:  TXD/GPIO19 -> LED strip DATA
Pin 4:  RXD        (not used)
Pin 5:  SCL        (used internally for I2C)
Pin 6:  SDA        (used internally for I2C)
Pin 7:  MISO       (not used)
Pin 8:  MOSI       (not used)
Pin 9:  SCK        (not used)
Pin 10: SSEL       (not used)
```

### LED Strip Wiring

1. **Data**: Connect LED strip DATA to UEXT pin 3 (GPIO 19)
2. **Ground**: Connect LED strip GND to UEXT pin 2 (GND)
3. **Power**: Connect LED strip 5V to external power supply
   - **Important**: Share GND between ESP32-ADF and LED power supply
   - 60 LEDs can draw up to 3.6A at full brightness white
   - Use adequate power supply (5V 4A or higher recommended)

### Audio Connections

The microphones and ES8388 codec chip are physically built into the ESP32-ADF board:
- **Microphones**: Built-in stereo MEMS microphones (hardware)
- **ES8388 Codec**: Audio codec chip soldered on board (hardware)
- **I2S pins**: GPIO 5 (SCK), GPIO 25 (WS), GPIO 35 (SD) - for audio data
- **I2C pins**: GPIO 18 (SDA), GPIO 23 (SCL) - for codec configuration

**Note**: The codec hardware is on the board, but you must upload MicroPython firmware and our code to configure and use it.

## Software Setup

### 1. Install MicroPython on ESP32-ADF

**Step 1: Install esptool**

```bash
# Install esptool using pip
python -m pip install esptool
```

**Step 2: Download MicroPython firmware**

- Go to https://micropython.org/download/ESP32_GENERIC/
- Download the latest `.bin` file (e.g., `ESP32_GENERIC-20240222-v1.22.2.bin`)

**Step 3: Flash MicroPython to ESP32-ADF**

```bash
# Erase flash memory (use one of these commands)
esptool.py --port COM3 erase_flash
# OR
python -m esptool --port COM3 erase_flash

# Flash MicroPython firmware (use one of these commands)
esptool.py --port COM3 --baud 460800 write_flash -z 0x1000 esp32-micropython.bin
# OR
python -m esptool --port COM3 --baud 460800 write_flash -z 0x1000 esp32-micropython.bin
```

**Note**:
- Replace `COM3` with your actual serial port (check in Device Manager on Windows, or use `/dev/ttyUSB0` on Linux/Mac)
- Replace `esp32-micropython.bin` with the actual filename you downloaded
- Use `esptool.py` if it works, otherwise use `python -m esptool`

### 2. Upload Files to ESP32

Using Thonny, ampy, or mpremote:

1. Upload `es8388.py` to the board
2. Upload `strudel_adf.py` to the board
3. Rename `strudel_adf.py` to `main.py` (or import it from boot.py)

Using Thonny:
- Open both files
- Select "File -> Save As..."
- Choose "MicroPython device"
- Save to root directory

### 3. Configure WiFi and MQTT

Edit `strudel_adf.py` and update these settings:

```python
# WiFi settings
WIFI_SSID = 'YourWiFiName'
WIFI_PASSWORD = 'YourPassword'

# MQTT settings (if using different broker)
MQTT_BROKER = 'mqtt.rubu.be'
MQTT_PORT = 1885
MQTT_USER = 'strudel'
MQTT_PASSWORD = 'qifj3258'
```

### 4. Adjust Beat Detection Sensitivity

Fine-tune the beat detection threshold based on your environment:

```python
# In strudel_adf.py
BEAT_THRESHOLD = 5000      # Lower = more sensitive
BEAT_COOLDOWN_MS = 100     # Time between beats (ms)
```

Test and adjust:
- **Too sensitive**: Increase `BEAT_THRESHOLD` (try 8000-15000)
- **Not sensitive enough**: Decrease `BEAT_THRESHOLD` (try 2000-4000)
- **Multiple triggers**: Increase `BEAT_COOLDOWN_MS` (try 150-300)

## Usage

### Starting the System

1. Connect LED strip to UEXT connector (pins 2 and 3)
2. Power up the ESP32-ADF board
3. Open Thonny and connect to the ESP32-ADF (or use any serial console at 115200 baud)
4. Run the script or view the console output
5. Wait for WiFi and MQTT connection
6. System will display "System ready!" when initialized

### Changing LED Colors

Use the web app from the main project:

1. Open `Codevoorbeelden/Web App/index.html`
2. Select a color (red, green, blue, cyan, magenta, yellow, white, random)
3. Choose mode: Flash or Travel
4. Color is sent via MQTT to `strudel/color` topic

### Manual MQTT Control

Send JSON message to `strudel/color` topic:

```json
{
  "s": "red",
  "mode": "flash"
}
```

Colors: `"red"`, `"green"`, `"blue"`, `"white"`, `"cyan"`, `"magenta"`, `"yellow"`, `"random"`

Modes: `"flash"`, `"travel"`

### Using with Strudel

Play bass drum sounds in Strudel and the ESP32-ADF will detect them via the microphones and trigger the LED effects.

## Configuration Reference

### LED Strip Settings

```python
NUMBER_OF_LEDS = 60        # Number of LEDs in strip
LED_PIN = 19               # GPIO pin (UEXT pin 3)
```

### Audio Settings

```python
I2S_SAMPLE_RATE = 16000    # Sample rate (Hz)
I2S_BITS = 16              # Bit depth
AUDIO_BUFFER_SIZE = 512    # Samples per read
```

### Beat Detection

```python
BEAT_THRESHOLD = 5000      # Amplitude threshold
BEAT_COOLDOWN_MS = 100     # Min time between beats
```

### ES8388 Codec

```python
codec.set_mic_gain(12)     # Microphone gain (0-24 dB)
codec.set_adc_volume(0)    # ADC volume (-96 to 0 dB)
```

## LED Effects

### Flash Effect
- All LEDs turn on simultaneously
- Duration: 100ms
- Best for sharp, punchy beats

### Travel Effect
- Light travels from first to last LED
- Duration: 300ms (5ms per LED for 60 LEDs)
- Creates a wave/chase effect

## Troubleshooting

### No Beat Detection

1. **Check microphone gain**: Increase `codec.set_mic_gain(12)` to higher value (up to 24)
2. **Adjust threshold**: Lower `BEAT_THRESHOLD` value
3. **Check audio input**: Monitor `avg_amplitude` values in serial console
4. **Verify I2S**: Ensure I2S pins are correctly connected (should be automatic on ESP32-ADF)

### ES8388 Not Found

```
ES8388 not found at address 0x10
```

- Check I2C connections (should be built-in on ESP32-ADF)
- Verify I2C address (should be 0x10 with CE pin low)
- Run `i2c.scan()` to see detected devices

### LED Strip Not Working

1. **Check wiring**:
   - Data to GPIO 19 (UEXT pin 3)
   - GND to UEXT pin 2
   - 5V to external supply
2. **Verify LED type**: Code is configured for RGB (bpp=3), change to RGBW (bpp=4) if needed
3. **Test with simple pattern**: Add test code in serial console

```python
np.fill((255, 0, 0))  # All red
np.write()
```

### WiFi Connection Issues

- Verify SSID and password
- Check 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Ensure WiFi is in range

### MQTT Connection Issues

- Verify broker address and port
- Check username and password
- Ensure SSL/TLS is supported by broker (port 1885)
- Test with MQTT client tool (MQTT Explorer, mosquitto_sub)

## Serial Console Output

Normal operation shows:

```
Initializing LED strip...
LED strip initialized on GPIO 19

Connecting to WiFi...
Connected to WiFi
Network config: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')

Initializing I2C bus...
I2C devices found: ['0x10']

Initializing ES8388 codec...
ES8388 found at address 0x10
Initializing ES8388 for ADC mode...
ES8388 ADC initialization complete
Microphone gain set to 12dB
ADC volume set to 0.0dB
ES8388 codec ready

Initializing I2S for microphone input...
I2S initialized
Sample rate: 16000 Hz
Format: 16-bit stereo

Connecting to MQTT broker...
Connected to MQTT broker
Subscribed to topic: strudel/color

==================================================
System ready!
Listening for bass drum hits...
Use web app or MQTT to change LED colors
==================================================

Color set to: red (255, 0, 0)
Mode set to: flash
Beat detected! Amplitude: 8543
Flash! (255, 0, 0)
Beat detected! Amplitude: 12234
Flash! (255, 0, 0)
```

## Technical Details

### Audio Processing

- **Sample Rate**: 16kHz (good balance of quality and CPU usage)
- **Bit Depth**: 16-bit signed integers
- **Channels**: Stereo (both microphones)
- **Buffer Size**: 512 samples (32ms at 16kHz)

### Beat Detection Algorithm

1. Read audio samples from I2S buffer
2. Convert bytes to 16-bit signed integers
3. Calculate average absolute amplitude
4. Compare to threshold
5. Apply cooldown period to prevent multiple triggers

This simple amplitude-based approach works well for bass drum detection as bass drums produce high-amplitude, low-frequency sounds.

### Performance

- **CPU Usage**: ~10-15% (main loop with audio processing)
- **Memory**: ~30KB for buffers and objects
- **Latency**: <50ms from sound to LED trigger
- **Beat Detection Rate**: Up to 10 beats/second (with 100ms cooldown)

## Project Structure

```
ESP_32_ADF/
├── README.md           # This file
├── es8388.py          # ES8388 codec driver
└── strudel_adf.py     # Main application code
```

## Credits

**Project**: Start 2 Study - Strudel LED Controller
**Institution**: Vives Hogeschool - Elektronica-ICT Kortrijk
**Hardware**: Olimex ESP32-ADF development board
**Software**: MicroPython 1.20+

## License

This project is for educational purposes as part of the Start 2 Study program at Vives Hogeschool.

## References

- [MicroPython Documentation](https://docs.micropython.org/)
- [Olimex ESP32-ADF](https://www.olimex.com/Products/IoT/ESP32/ESP32-ADF/)
- [ES8388 Datasheet](https://dl.radxa.com/rock2/docs/hw/ds/ES8388%20user%20Guide.pdf)
- [WS2813 LED Strip Info](https://www.tinytronics.nl/nl/verlichting/led-strips/led-strips/ws2813-digitale-5050-rgb-led-strip-60-leds-1m)
