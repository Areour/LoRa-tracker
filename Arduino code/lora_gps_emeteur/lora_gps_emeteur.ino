#include <TinyGPS.h>
#include <SPI.h>
#include <RH_RF95.h>
#include <avr/dtostrf.h>

// Instance of the radio driver
RH_RF95 rf95;
TinyGPS gps;

char databuf[100];
uint8_t dataoutgoing[100];
char gps_lon[20]={"\0"};  
char gps_lat[20]={"\0"};

static void smartdelay(unsigned long ms);

void setup()
{
  Serial.begin(115200);
  Serial1.begin(9600);
  if (!rf95.init()) Serial.println("init failed");
    // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
  
  Serial.print("Simple teste de portée de trensmission avec LoRa");
  Serial.println();
}

void loop()
{ 
  // Print Sending to rf95_server
  Serial.println("Sending to reciver");
  bool newData =true;// false;
  unsigned long chars;
  unsigned short sentences, failed;
  String latstring="";
  String lonstring="";


  // For one second we parse GPS data and report some key values
  for (unsigned long start = millis(); millis() - start < 1000;)
  {
    while (Serial1.available())
    {
      char c = Serial1.read();
      //Serial.write(c); // uncomment this line if you want to see the GPS data flowing
      if (gps.encode(c)) // Did a new valid sentence come in?
      newData = true;
    }
  }
  //Get the GPS data*/
  if (newData)
  {
    float flat, flon;
    unsigned long age;
    gps.f_get_position(&flat, &flon);

    dtostrf(flat, 10, 6, gps_lat); 
    dtostrf(flon, 10, 6, gps_lon);

    strcat(strcat(gps_lon,","),gps_lat);
    strcpy(gps_lat,gps_lon);
    strcpy((char *)dataoutgoing,gps_lat);
    
    Serial.println((char *)dataoutgoing);
    // Send the data to server
    rf95.send(dataoutgoing, sizeof(dataoutgoing));

    // Now wait for a reply
    uint8_t indatabuf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(indatabuf);

    if (rf95.waitAvailableTimeout(3000))
     { 
       // Should be a reply message for us now   
       if (rf95.recv(indatabuf, &len))
      {
         // Serial print "got reply:" and the reply message from the server
         Serial.print("got reply: ");
         Serial.println((char*)indatabuf);
      }
      else
      {
      Serial.println("recv failed");
      }
    }
    else
    {
      // Serial print "No reply, is rf95_server running?" if don't get the reply .
      Serial.println("No reply, is rf95_server running?");
    }
    delay(400);
    
    }
    gps.stats(&chars, &sentences, &failed);                                                                                                                                                                                                                                                                                                                                                                          
  Serial.print(" CHARS=");
  Serial.print(chars);
  Serial.print(" SENTENCES=");
  Serial.print(sentences);
  Serial.print(" CSUM ERR=");
  Serial.println(failed);
  if (chars == 0)
  Serial.println("** No characters received from GPS: check wiring **");
}
