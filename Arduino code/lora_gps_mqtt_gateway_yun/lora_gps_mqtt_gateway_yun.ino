//Include required lib so Arduino can talk with the Lora Shield
#include <SPI.h>
#include <RH_RF95.h>
#include <YunClient.h>
#include <PubSubClient.h>
#include <Bridge.h>

// Singleton instance of the radio driver
RH_RF95 rf95;

int reset_lora = 9;

String dataString = "";
String latE="";
String lonE="";
String RSSI="";
String SNR="";

char databuf[50];

const char* topic_t="lora_test/coord";

// L'adresse de du Broker
// the Broker adress

const char* server = "192.168.1.3";

// instance de la classe EthernetClient
// instance of the EthernetClient class

YunClient YClient;

// l'instance de la classe MQTT
// instance of the MQTT class

PubSubClient mqtt(YClient);

void reconnect(void);
void pubValeur(String dataString);

void setup() 
{
  Bridge.begin();
  Serial.begin(9600);
  
  pinMode(reset_lora, OUTPUT);     
  
  // reset lora module first. to make sure it will works properly
  digitalWrite(reset_lora, LOW);   
  delay(1000);
  digitalWrite(reset_lora, HIGH); 
  
  if (!rf95.init())
    Serial.println("init failed");  
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
  // Need to change to 868.0Mhz in RH_RF95.cpp 

  // Initialisation de la connexion TCP
  // Initializing the TCP connection

  // Initialisation de la connexion au Broker
  // Initializing the Broker connection
  
  mqtt.setServer(server, 1883);
 
  delay(1500);  
}

void loop()
{ 
  if(mqtt.connected())
  {
  bool newData = false;
  dataString="";
  if (rf95.available())
  {
    // Should be a message for us now   
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    // For one second we parse GPS data and report some key values
  
  if (rf95.recv(buf, &len))
    {
      //RH_RF95::printBuffer("request: ", buf, len);
      
      //make a string that start with a timestamp for assembling the data to log:
      dataString += String((char*)buf);
      //Serial.println(dataString);
      lonE = dataString.substring(0,dataString.indexOf(','));
      latE = dataString.substring(dataString.indexOf(',')+1);

      
      Serial.print(latE);
      Serial.print(",");
      Serial.print(lonE);
      Serial.print(",");
      Serial.print(rf95.lastRssi(), DEC);
      Serial.print(",");
      Serial.println(rf95.lastSNR(), DEC);

      //dataString ="";
      
      //dataString += latE;
      //dataString += String(",");
      //dataString += lonE;
      dataString += String(",");
      dataString += String(rf95.lastRssi(), DEC);
      dataString += String(",");
      dataString += String(rf95.lastSNR(), DEC);

      pubValeur(dataString);
      
      // Send a reply to client as ACK
      uint8_t data[] = "200 OK";
      rf95.send(data, sizeof(data));
      rf95.waitPacketSent();
    }
  }
}
else {
    // Sinon se reconnecté au Broker
    // Otherwise connect to the Broker
    reconnect();
  }
}

void pubValeur(String dataString)
{
  
  // publication des donnée sur la Broker
  // publication of data on the Broker

  dataString.toCharArray(databuf, 50);
  
  mqtt.publish(topic_t,databuf);

  delay(10000); 
}

void reconnect(void) {
  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (mqtt.connect("oha")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}   
