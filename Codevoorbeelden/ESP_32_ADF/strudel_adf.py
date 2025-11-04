# MicroPython code for Olimex ESP32-ADF Board
# Bass drum detection with LED strip control via MQTT color selection
#
# Hardware:
# - Olimex ESP32-ADF with built-in ES8388 codec and stereo microphones
# - WS2813 RGB LED strip (60 LEDs) connected to GPIO 19 (UEXT connector pin 3)
# - GND connected to UEXT connector pin 2
#
# Start To Study - Vives Elektronica-ICT

# Bibliotheken importeren
import network
import time
from umqtt.simple import MQTTClient
from machine import Pin, I2C, I2S, PWM
import neopixel
import ujson
import random
import array
import struct

# Import ES8388 driver (Olimex direct port)
from es8388_olimex import ES8388

# ============================================================================
# CONFIGURATIE
# ============================================================================

# LED-strip instellingen
NUMBER_OF_LEDS = 60
LED_PIN = 19  # GPIO 19 (UEXT connector pin 3 - UART TX)

# WiFi-instellingen
WIFI_SSID = 'Core-Z5'
WIFI_PASSWORD = 'kaya5050'

# MQTT-instellingen
MQTT_BROKER = 'mqtt.rubu.be'
MQTT_PORT = 1885
MQTT_USER = 'strudel'
MQTT_PASSWORD = 'qifj3258'
MQTT_COLOR_TOPIC = 'strudel/color'

# I2C instellingen voor ES8388 codec
I2C_SDA = 18
I2C_SCL = 23
I2C_FREQ = 100000

# I2S instellingen voor microphone
I2S_ID = 0
I2S_SCK = 5      # Bit clock
I2S_WS = 25      # Word select
I2S_SD = 35      # Data in (microphone)
I2S_SAMPLE_RATE = 16000  # 16kHz sample rate
I2S_BITS = 16

# Beat detection instellingen
BEAT_THRESHOLD = 5000      # Amplitude threshold for beat detection
BEAT_COOLDOWN_MS = 100     # Minimum time between beats (ms)
AUDIO_BUFFER_SIZE = 512    # Number of samples to read at once

# ============================================================================
# GLOBALE VARIABELEN
# ============================================================================

# LED strip color (R, G, B)
led_strip_color = (0, 0, 40)

# LED effect mode (flash or travel)
led_mode = "flash"

# Beat detection state
last_beat_time = 0

# Audio buffer
audio_buffer = bytearray(AUDIO_BUFFER_SIZE * 2)  # 16-bit samples = 2 bytes each

# ============================================================================
# LED STRIP SETUP
# ============================================================================

print("Initializing LED strip...")
led_pin = Pin(LED_PIN)
np = neopixel.NeoPixel(led_pin, NUMBER_OF_LEDS, bpp=3)

# Turn off all LEDs initially
np.fill((0, 0, 0))
np.write()
print(f"LED strip initialized on GPIO {LED_PIN}")

# ============================================================================
# WIFI SETUP
# ============================================================================

print("\nConnecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

# Wait for connection
while not wlan.isconnected():
    print('Trying to connect to WiFi...')
    time.sleep(1)

print('Connected to WiFi')
print('Network config:', wlan.ifconfig())
print()

# ============================================================================
# I2C SETUP
# ============================================================================

print("Initializing I2C bus...")
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)
print("I2C devices found:", [hex(addr) for addr in i2c.scan()])
print()

# ============================================================================
# I2S SETUP FOR MICROPHONE INPUT
# ============================================================================
# NOTE 1: I2S must be initialized BEFORE ES8388 codec
# NOTE 2: ES8388 REQUIRES MCLK (Master Clock) on GPIO0!
#         The codec cannot function without this external clock signal

# CRITICAL: Generate MCLK on GPIO0 using PWM
# ES8388 typically needs MCLK = 256 * sample_rate or 512 * sample_rate
# For 16kHz: MCLK should be 256 * 16000 = 4.096 MHz or 512 * 16000 = 8.192 MHz
# We'll use 512x ratio = 8.192 MHz
print("Configuring MCLK (Master Clock) on GPIO0...")
mclk_pin = PWM(Pin(0), freq=8192000, duty=512)  # 8.192 MHz, 50% duty cycle
print("MCLK: 8.192 MHz on GPIO0")
print()

print("Initializing I2S for microphone input...")
audio_in = I2S(
    I2S_ID,
    sck=Pin(I2S_SCK),
    ws=Pin(I2S_WS),
    sd=Pin(I2S_SD),
    mode=I2S.RX,
    bits=I2S_BITS,
    format=I2S.STEREO,
    rate=I2S_SAMPLE_RATE,
    ibuf=4096  # Internal buffer size
)

print("I2S initialized")
print(f"Sample rate: {I2S_SAMPLE_RATE} Hz")
print(f"Format: {I2S_BITS}-bit stereo")
print()

# Give I2S time to stabilize
time.sleep_ms(100)

# ============================================================================
# ES8388 CODEC SETUP
# ============================================================================

print("Initializing ES8388 codec...")
codec = ES8388(i2c)
codec.init()  # Use Olimex init method
codec.set_mic_gain(24)  # 24dB microphone gain
# Volume is already set to 0dB in init()

# CRITICAL: Start ADC capture (from Olimex es8388_set_state)
codec.start()  # Use Olimex start method

print("ES8388 codec ready")

# Dump registers for debugging
codec.read_all_registers()

# Test: Try to read a few samples immediately after codec init
print("\nTesting immediate audio read after codec init...")
test_buffer = bytearray(100)
test_read = audio_in.readinto(test_buffer)
print(f"Test read: {test_read} bytes")
print(f"Test data: {[test_buffer[i] for i in range(min(20, test_read))]}")

# Additional debug: Check if data is actually changing over time
print("\nWaiting 500ms and reading again...")
time.sleep_ms(500)
test_buffer2 = bytearray(100)
test_read2 = audio_in.readinto(test_buffer2)
print(f"Second read: {test_read2} bytes")
print(f"Second data: {[test_buffer2[i] for i in range(min(20, test_read2))]}")

# Check if the two reads are identical (which would be suspicious)
if test_buffer[:test_read] == test_buffer2[:test_read2]:
    print("WARNING: Both reads returned IDENTICAL data - codec may not be capturing!")
else:
    print("Data is changing - codec appears to be capturing")

# Additional diagnostic: Try reading a large chunk
print("\nTrying large read (4096 bytes)...")
large_buffer = bytearray(4096)
large_read = audio_in.readinto(large_buffer)
print(f"Large read: {large_read} bytes")
# Count how many bytes are non-zero
non_zero_count = sum(1 for b in large_buffer[:large_read] if b != 0)
print(f"Non-zero bytes: {non_zero_count} out of {large_read} ({non_zero_count*100//large_read if large_read > 0 else 0}%)")

print()

# ============================================================================
# LED EFFECTS
# ============================================================================

def led_flash(color):
    """Flash all LEDs briefly"""
    np.fill(color)
    np.write()
    time.sleep_ms(100)
    np.fill((0, 0, 0))
    np.write()

def led_travel(color):
    """Travel effect: light moves from first to last LED in 300ms"""
    delay_per_led = 150 / NUMBER_OF_LEDS  # milliseconds per LED
    for i in range(NUMBER_OF_LEDS):
        np[i] = color
        np.write()
        time.sleep_ms(int(delay_per_led))
    # Turn off after travel
    time.sleep_ms(100)
    np.fill((0, 0, 0))
    np.write()

def trigger_led_effect():
    """Trigger LED effect based on current mode and color"""
    if led_mode == "flash":
        led_flash(led_strip_color)
        print(f"Flash! ({led_strip_color})")
    elif led_mode == "travel":
        led_travel(led_strip_color)
        print(f"Travel! ({led_strip_color})")

# ============================================================================
# BEAT DETECTION
# ============================================================================

def detect_beat():
    """
    Read audio samples and detect if a beat occurred
    Returns True if a beat was detected, False otherwise
    """
    global last_beat_time

    try:
        # Read audio samples
        num_read = audio_in.readinto(audio_buffer)

        if num_read > 0:
            # Calculate RMS (Root Mean Square) amplitude
            # Convert bytes to 16-bit signed integers
            samples = array.array('h', audio_buffer[:num_read])

            # Calculate average absolute amplitude (simpler than RMS, works well)
            total = 0
            for sample in samples:
                total += abs(sample)

            avg_amplitude = total // len(samples) if len(samples) > 0 else 0

            # Check if amplitude exceeds threshold
            if avg_amplitude > BEAT_THRESHOLD:
                # Check cooldown to avoid multiple triggers
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_beat_time) > BEAT_COOLDOWN_MS:
                    last_beat_time = current_time
                    print(f"BEAT DETECTED! Amplitude: {avg_amplitude}")
                    return True
        
    except Exception as e:
        print(f"Error in beat detection: {e}")
        import sys
        sys.print_exception(e)

    return False

# ============================================================================
# MQTT CALLBACK
# ============================================================================

def on_mqtt_message(topic, message):
    """Handle incoming MQTT messages for color changes"""
    global led_strip_color, led_mode

    topic_str = str(topic, 'utf-8')

    # Handle color topic
    if topic_str == MQTT_COLOR_TOPIC:
        try:
            # Parse JSON data
            color_data = ujson.loads(str(message, 'utf-8'))

            # Color map
            color_map = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "white": (255, 255, 255),
                "cyan": (0, 255, 255),
                "magenta": (255, 0, 255),
                "yellow": (255, 255, 0)
            }

            # Get color from message
            requested_color = color_data.get("s", "")

            # Update color
            if requested_color == "random":
                led_strip_color = (random.randint(0, 255),
                                 random.randint(0, 255),
                                 random.randint(0, 255))
                print(f"New random color: {led_strip_color}")
            elif requested_color in color_map:
                led_strip_color = color_map[requested_color]
                print(f"Color set to: {requested_color} {led_strip_color}")

            # Update mode if specified
            if "mode" in color_data:
                led_mode = color_data["mode"]
                print(f"Mode set to: {led_mode}")

            # Trigger LED effect when color changes (for testing)
            print("Triggering LED effect from color change...")
            trigger_led_effect()

        except Exception as e:
            print(f"Error processing color message: {e}")

# ============================================================================
# MQTT SETUP
# ============================================================================

print("Connecting to MQTT broker...")
mqtt_client = MQTTClient("esp32_adf", MQTT_BROKER, port=MQTT_PORT,
                         ssl=True, user=MQTT_USER, password=MQTT_PASSWORD)
mqtt_client.set_callback(on_mqtt_message)
mqtt_client.connect()
print("Connected to MQTT broker")

# Subscribe to color topic only (not control topic)
mqtt_client.subscribe(MQTT_COLOR_TOPIC)
print(f"Subscribed to topic: {MQTT_COLOR_TOPIC}")
print()

# ============================================================================
# MAIN LOOP
# ============================================================================

print("=" * 50)
print("System ready!")
print("Listening for bass drum hits...")
print("Use web app or MQTT to change LED colors")
print("=" * 50)
print()

# Main loop
try:
    while True:
        # Check for MQTT messages (non-blocking with timeout)
        mqtt_client.check_msg()

        # Check for beat detection
        if detect_beat():
            trigger_led_effect()

        # Small delay to prevent CPU overload
        time.sleep_ms(1)

except KeyboardInterrupt:
    print("\nShutting down...")

finally:
    # Cleanup
    print("Turning off LEDs...")
    np.fill((0, 0, 0))
    np.write()

    print("Stopping I2S...")
    audio_in.deinit()

    print("Disconnecting from MQTT...")
    mqtt_client.disconnect()

    print("Done.")
