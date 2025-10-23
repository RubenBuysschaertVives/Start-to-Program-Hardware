// jQuery gebruiken voor de animatie van het menu.
$(document).ready(function(){
    // Pagina is geladen.
    console.log("Page ready.");

    // Menu openschuiven en icoon aanpassen.
    $("#menuIcon").click(function(){
        $("nav").slideToggle("fast", function(){
            if($("#menuIcon").html() === "menu")
                $("#menuIcon").html("close");
            else
                $("#menuIcon").html("menu");
        });
    });

    console.log("Page still ready.");
});



// Gewone JavaScript voor de MQTT-functionaliteiten.
var requestedColor = "none";

// MQTT-gedeelte implementeren via een JavaScript MQTT-client (Paho).
var mqttClient;
const mqttTopic = "strudel/color";

window.addEventListener('load', function(){
    // Service worker laden, zodat het een echte PWA wordt.
    if ('serviceWorker' in navigator) 
    {
        navigator.serviceWorker.register('./service-worker.js')
        .then((registration) => {
          console.log('Registered: ');
          console.log(registration);
          })
        .catch((err) => console.log(err));
    } 
    else
    {
      alert('No service worker support in this browser.');
    }

    // Alle kleuren DIV's overlopen en hun click events opvangen.
    var colorOptions = document.querySelectorAll(".colorOption");
    colorOptions.forEach(colorOption => {
        colorOption.addEventListener('click', (e) => {
            requestedColor = colorOption.style.backgroundColor;
            if(requestedColor == "gray")
                requestedColor = "random";
            console.log("Requeste color:", requestedColor);

            // Client object maken met unieke ID.
            var clientId = Math.floor(Math.random() * 100000);

            try {
                // LET OP: de Paho bibliotheek gebruikt WebSockets. Dus kies de juiste poort!
                mqttClient = new Paho.MQTT.Client("mqtt.rubu.be", 9003,
                "", "strudel" + String(clientId));

                // Eén of enkele events registreren.
                mqttClient.onConnectionLost = onMqttDisconnected;

                // Verbinden met dictionary met opties: zie: http://www.eclipse.org/paho/files/jsdoc/index.html.
                // Verbinden met username en password.
                mqttClient.connect(
                {
                    onSuccess: onMqttConnected,
                    onFailure: onMqttFailure,
                    useSSL: true,
                    userName: document.getElementById("tbxMqttUser").value,
                    password: document.getElementById("tbxMqttPwd").value
                });
            }
            catch (error) {
                console.log("Error:", error);
            }
        });
    });
});

function onMqttConnected() {
    console.log("Connected to MQTT-broker.");

    try {
        // MQTT-data publishen via een Message object.
        let message = new Paho.MQTT.Message("{\"color\":\"" + requestedColor + "\"}");
        message.destinationName = mqttTopic;			  // Topic bepalen.
        message.qos = 0;                                  // Fire and forget.
        message.retained = false;                         // Bericht niet afleveren aan nieuw verbonden clients.
        mqttClient.send(message);

        console.log("Message published to MQTT-broker.");

        // Verbinding met MQTT-broker verbreken.
        mqttClient.disconnect();
    }
    catch (error) {
        console.log("Error publishing to MQTT-broker:", error);
    }
};

// Indien MQTT-verbinding verbroker werd.
function onMqttDisconnected() {
    console.log("Disconnected from MQTT-broker.")
}

// Indien verbinden niet lukt, toon een foutmelding.
function onMqttFailure(response) {
    console.log("Unable to connect to MQTT-broker.", response.errorMessage);
}
