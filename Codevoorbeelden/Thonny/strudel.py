# MicroPython code voor op een Adafruit HUZZAH32 – ESP32 Feather Board.
# OPM: zorg dat de MicroPython interpreter geladen is in het microcontrollerbord. Doe
# dat best via 'Thonny - configure interpreter...' (onderaan rechts).
#
# Start To Study - Vives Elektronica-ICT


# Bibliotheken importeren.
import network
import time
from umqtt.simple import MQTTClient
import machine
import neopixel
import ujson
import random


# Eén meter LED-strip met telkens 60 LED's per meter (R, G, B).
number_of_leds = 60

# Aangeven op welke pin de LED-strip is gekoppeld met de microcontroller.
din = machine.Pin(5)

# Een NeoPixel object maken met de juiste instellingen.
# Aangezien we hier een RGB LED-strip gebruiken, zijn er 3 'bytes per pixel'.
# Zie: https://www.tinytronics.nl/nl/verlichting/led-strips/led-strips/ws2813-digitale-5050-rgb-led-strip-60-leds-1m
# Constructor info: https://docs.micropython.org/en/latest/library/neopixel.html
np = neopixel.NeoPixel(din, number_of_leds, bpp=3)

# Globale variabele (tuple) om het kleur van de LED-strip te bewaren (R, G, B).
led_strip_color = (0, 0, 40)

# Eerst alle LED's doven.
for i in range(number_of_leds):
    np[i] = (0, 0, 0)
np.write()


# WiFi-instellingen klaarzetten.
# TODO: aanpassen naar wens.
ssid = 'Core-Z5'
password = 'kaya5050'

# Verbinding maken met het WiFi-netwerk.
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wacht tot er verbinding is met het netwerk.
while not wlan.isconnected():
    print('Probeer te verbinden met WiFi...')
    time.sleep(1)
print()
print('Verbonden met het netwerk met volgende gegevens:')
print(wlan.ifconfig())
print()


# MQTT-instellingen klaarzetten.
# Een callback functie voorbereiden, om een ontvangen MQTT-bericht te verwerken.
def on_mqtt_message(topic, message):
    # De globale variabele voor het kleur ophalen.
    global led_strip_color

    # Topic omzetten naar string (eenmalig).
    topic_str = str(topic, 'utf-8')

    # Komt de info van het 'control' topic?
    if topic_str == "strudel/control":
        # De data in JSON-formaat, omzetten naar een Python dictionary.
        strudel_data = ujson.loads(str(message, 'utf-8'))

        # LED's inschakelen indien gevraagd.
        if strudel_data["s"] == "on":
            # Inschakelen met fill() (sneller dan loop).
            np.fill(led_strip_color)
            np.write()
            # Korte flash (20ms in plaats van 100ms).
            time.sleep(0.02)
            # Uitschakelen.
            np.fill((0, 0, 0))
            np.write()
            print("Flash!")  # Print NA de flash voor snelheid.

    # Komt de info van het 'color' topic?
    if topic_str == "strudel/color":
        # De data in JSON-formaat, omzetten naar een Python dictionary.
        color_data = ujson.loads(str(message, 'utf-8'))

        # Dictionary voor snellere color lookup.
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "yellow": (255, 255, 0)
        }

        # Strudel sends color value in "s" key (sound value)
        requested_color = color_data["s"]

        # Get the mode (flash or travel), default to flash if not specified
        mode = color_data.get("mode", "flash")

        if requested_color == "random":
            # Zie: https://docs.micropython.org/en/latest/library/random.html#random.randint
            led_strip_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            print(f"Nieuwe willekeurige kleur: {led_strip_color}.")
        elif requested_color in color_map:
            led_strip_color = color_map[requested_color]
            print(f"Kleur ingesteld: {requested_color}.")

        # Trigger the LED effect when color/mode changes
        print(f"Triggering LED effect: {mode}")
        if mode == "flash":
            # Flash effect: all LEDs on briefly then off
            np.fill(led_strip_color)
            np.write()
            time.sleep(0.1)
            np.fill((0, 0, 0))
            np.write()
            print(f"Flash! ({requested_color})")
        elif mode == "travel":
            # Travel effect: light travels from first to last LED in 300ms
            delay_per_led = 200 / number_of_leds / 1000  # Convert to seconds
            for i in range(number_of_leds):
                np[i] = led_strip_color
                np.write()
                time.sleep(delay_per_led)
            # Turn all LEDs off after the travel
            time.sleep(0.1)
            np.fill((0, 0, 0))
            np.write()
            print(f"Travel! ({requested_color})")

# Zie: https://mpython.readthedocs.io/en/v2.2.1/library/mPython/umqtt.simple.html#create-object
# Lokale MQTT broker op de PC (zelfde netwerk als ESP32)
client = MQTTClient("esp32", "10.75.1.63", port=1883, ssl=False)

# Koppeling maken naar callback functie indien een bericht ontvangen werd.
client.set_callback(on_mqtt_message)

# Verbinden met de MQTT-broker.
client.connect()
print("Verbonden met de MQTT-broker.")
print()

# Abonneren op twee interessante topics...
topic = "strudel/control"
client.subscribe(topic)
print(f"Geabonneerd op topic '{topic}'.")
topic = "strudel/color"
client.subscribe(topic)
print(f"Geabonneerd op topic '{topic}'.")


# Oneindige lus starten om continu te 'luisteren' naar binnenkomende berichten.
while True:
    # Check voor berichten (non-blocking). Verwerk als er één is.
    client.check_msg()
    # Kleine pauze om CPU te ontlasten
    time.sleep_ms(10)

# Unreachable, maar verbreek de verbinding...
client.disconnect()
