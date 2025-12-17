# MicroPython code voor op een Adafruit HUZZAH32 – ESP32 Feather Board.
# OPM: zorg dat de MicroPython interpreter geladen is in het microcontrollerbord. Doe
# dat best via 'Thonny - configure interpreter...' (onderaan rechts).
#
# Start to Program Hardware - Vives Elektronica-ICT - Kortrijk


# Bibliotheken importeren.
import network
import time
from umqtt.simple import MQTTClient
import machine
import neopixel
import ujson
import random

# TODO: aantal LED's bepalen.
# Een stukje LED-strip (met telkens 60 LED's per meter), van 5 LED's (R, G, B) in totaal.
number_of_leds = ...

# TODO: koppeling met pin maken.
# Aangeven op welke pin de LED-strip is gekoppeld met de microcontroller.
din = machine.Pin(...)

# Een NeoPixel object maken met de juiste instellingen.
# Aangezien we hier een RGB LED-strip gebruiken, zijn er 3 'bytes per pixel'.
# Zie: https://www.tinytronics.nl/nl/verlichting/led-strips/led-strips/ws2813-digitale-5050-rgb-led-strip-60-leds-1m
# Constructor info: https://docs.micropython.org/en/latest/library/neopixel.html
np = neopixel.NeoPixel(din, number_of_leds, bpp=3)

# Globale variabele die bijhoudt welke kleur laatst aangevraagd werd (via MQTT). Zet dat kleur standaard op blauw.
requested_color = "blue"

# TODO: topics aanpassen met een verwijzing naar je eigen naam.
# Globale variabelen die de MQTT-topics bevatten die gebruikt moeten worden.
controlTopic = "strudel/voornaamachternaam/control"
colorTopic = "strudel/voornaamachternaam/color"


# TODO: tupple met drie nullen opvullen.
# Eerst alle LED's doven.
for i in range(number_of_leds):
    np[i] = ...
np.write()


# WiFi-instellingen klaarzetten.
# TODO: aanpassen naar wens, volgens het beschikbare WiFi-netwerk.
ssid = 'A118_IWT_TEMPORARY'
password = '...'

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


# Functie maken die een bepaalde kleur (string), omzet naar RGB-waarden (tuple).
def color_to_rgb(color):
    # Lokale variabele (tuple) om het kleur van de LED-strip te bewaren (R, G, B).
    led_strip_color = (0, 0, 0)

    # Juiste kleur klaarzetten in de lokale variabele.
    if(color == "red"):
        led_strip_color = (255, 0, 0)
        
    if(color == "green"):
        led_strip_color = (0, 255, 0)
        
    if(color == "blue"):
        led_strip_color = (0, 0, 255)
        
    if(color == "white"):
        led_strip_color = (255, 255, 255)
        
    if(color == "cyan"):
        led_strip_color = (0, 255, 255)
        
    if(color == "magenta"):
        led_strip_color = (255, 0, 255)
        
    if(color == "yellow"):
        led_strip_color = (255, 255, 0)
    
    if(color == "random"):
        # Zie: https://docs.micropython.org/en/latest/library/random.html#random.randint
        led_strip_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
    print(f"Huidige kleur: {led_strip_color}.")
    
    # Het resultaat teruggeven.
    return led_strip_color


# MQTT-instellingen klaarzetten.
# Een callback functie voorbereiden, om een ontvangen MQTT-bericht te verwerken.
def on_mqtt_message(topic, message):
    # De globale variabele voor het kleur ophalen.
    global requested_color
    
    # Info geven aan de gebruiker.
    print(f"Bericht ontvangen op '{str(topic, 'utf-8')}': {str(message, 'utf-8')}.")
    
    # Komt de info van het 'control' topic?
    if(str(topic, 'utf-8') == controlTopic):
        # De data in JSON-formaat, omzetten naar een Python dictionary.
        strudel_data = ujson.loads(str(message, 'utf-8'))
        
        # LED's inschakelen indien gevraagd. Bekijk daarvoor de 's' key uit de dictionary.
        if(strudel_data["s"] == "on"):
            # TODO: de omzettingsfunctie oproepen.
            # Kleur omzetten van tekst naar tuple.
            led_strip_color = ...
            
            # LED's inschakelen.
            for i in range(number_of_leds):
                np[i] = led_strip_color
            np.write()
            # Even wachten.
            time.sleep(0.1)
            # LED'S terug uitschakelen.
            for i in range(number_of_leds):
                np[i] = (0, 0, 0)
            np.write()

    # Komt de info van het 'color' topic?
    if(str(topic, 'utf-8') == colorTopic):
        # De data in JSON-formaat, omzetten naar een Python dictionary en daaruit het kleur bewaren.
        requested_color = ujson.loads(str(message, 'utf-8'))["color"]

# MQTT-client maken.
# Zie: https://mpython.readthedocs.io/en/v2.2.1/library/mPython/umqtt.simple.html#create-object
client = MQTTClient("esp32", "mqtt.rubu.be", port=1885, ssl=True, user="strudel", password="qifj3258")

# Koppeling maken naar callback functie indien een bericht ontvangen werd.
client.set_callback(on_mqtt_message)

# Verbinden met de MQTT-broker.
client.connect()
print("Verbonden met de MQTT-broker.")
print()

# Abonneren op twee interessante topics...
client.subscribe(controlTopic)
print(f"Geabonneerd op topic '{controlTopic}'.")
client.subscribe(colorTopic)
print(f"Geabonneerd op topic '{colorTopic}'.")


# Oneindige lus starten om continu te 'luisteren' naar binnenkomende berichten.
while True:
    # Wacht op een bericht. Als er één is, roep de callback functie aan.
    client.wait_msg()

# Unreachable, maar verbreek de verbinding...
client.disconnect()
