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


# Drie meter LED-strip met telkens 60 LED's per meter (R, G, B, W).
number_of_leds = 180

# Aangeven op welke pin de LED-strip is gekoppeld met de microcontroller.
din = machine.Pin(5)

# Een NeoPixel object maken met de juiste instellingen.
# Aangezien we hier een RGBW LED-strip gebruiken, zijn er 4 'bytes per pixel'.
# Zie: https://www.tinytronics.nl/nl/verlichting/led-strips/led-strips/sk6812-digitale-5050-rgbw-led-strip-60-leds-1m
# Constructor info: https://docs.micropython.org/en/latest/library/neopixel.html
np = neopixel.NeoPixel(din, number_of_leds, bpp=4)

# Globale variabele (tuple) om het kleur van de LED-strip te bewaren (R, G, B, W).
led_strip_color = (0, 0, 40, 0)

# Eerst alle LED's doven.
for i in range(number_of_leds):
    np[i] = (0, 0, 0, 0)
np.write()


# WiFi-instellingen klaarzetten.
# TODO: aanpassen naar wens.
ssid = 'A118_IWT_TEMPORARY'
password = 'VIVES_ELOICT'

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
    
    # Info geven aan de gebruiker.
    print(f"Bericht ontvangen op '{str(topic, 'utf-8')}': {str(message, 'utf-8')}.")
    
    # Komt de info van het 'control' topic?
    if(str(topic, 'utf-8') == "strudel/control"):
        # De data in JSON-formaat, omzetten naar een Python dictionary.
        strudel_data = ujson.loads(str(message, 'utf-8'))
        
        # LED's inschakelen indien gevraagd.
        if(strudel_data["s"] == "on"):
            # Inschakelen.
            for i in range(number_of_leds):
                np[i] = led_strip_color
            np.write()
            # Even wachten.
            time.sleep(0.1)
            # Uitschakelen.
            for i in range(number_of_leds):
                np[i] = (0, 0, 0, 0)
            np.write()

    # Komt de info van het 'color' topic?
    if(str(topic, 'utf-8') == "strudel/color"):
        # De data in JSON-formaat, omzetten naar een Python dictionary.
        color_data = ujson.loads(str(message, 'utf-8'))
        
        # Juiste kleur klaarzetten in de globale variabele.
        if(color_data["color"] == "red"):
            led_strip_color = (255, 0, 0, 0)
            
        if(color_data["color"] == "green"):
            led_strip_color = (0, 255, 0, 0)
            
        if(color_data["color"] == "blue"):
            led_strip_color = (0, 0, 255, 0)
            
        if(color_data["color"] == "white"):
            led_strip_color = (0, 0, 0, 255)
            
        if(color_data["color"] == "cyan"):
            led_strip_color = (0, 255, 255, 0)
            
        if(color_data["color"] == "magenta"):
            led_strip_color = (255, 0, 255, 0)
            
        if(color_data["color"] == "yellow"):
            led_strip_color = (255, 255, 0, 0)
        
        if(color_data["color"] == "random"):
            # Zie: https://docs.micropython.org/en/latest/library/random.html#random.randint
            led_strip_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 0)
            print(f"Nieuwe willekeurige kleur: {led_strip_color}.")

# Zie: https://mpython.readthedocs.io/en/v2.2.1/library/mPython/umqtt.simple.html#create-object
client = MQTTClient("esp32", "mqtt.rubu.be", port=1885, ssl=True, user="strudel", password="qifj3258")

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
    # Wacht op een bericht. Als er één is, roep de callback functie aan.
    client.wait_msg()

# Unreachable, maar verbreek de verbinding...
client.disconnect()
