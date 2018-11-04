double randGPS_lat,randGPS_long;
double GPS_lat=36.799140, GPS_long=3.572391;
int RSSI,SNR;

void setup(){
  Serial.begin(9600);
  
  randomSeed(analogRead(0));
}

void loop() {
  randGPS_lat  = (random(36000000,37000000)/1000000.0);
  randGPS_long = (random(3000000,4000000)/1000000.0);
  RSSI = random(122);
  SNR  = random(80);
  Serial.print(randGPS_lat,6);
  Serial.print(",");
  Serial.print(randGPS_long,6);
  Serial.print(",");
  Serial.print(GPS_lat,6);
  Serial.print(",");
  Serial.print(GPS_long,6);
  Serial.print(",");
  Serial.print(RSSI);
  Serial.print(",");
  Serial.println(SNR);
  
  delay(10000);
}
