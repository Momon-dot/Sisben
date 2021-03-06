                                                                                                                                                                                                                                                                                                                                                                                                                                                                          #include <Wire.h>
#include <BH1750.h>

//create two instances of BH1750 Ambient Light Intensity Sensors(one for each sensor)
BH1750 lightmeter;

//define pin and variables for LDR Sensor
//define pin number
const int A0_LDR =33;
//define variables
float lux,ADC_value=0.001221,LDR_value;

//define pin and variables for UltraSonic Sensor
// define pins numbers
const int trigPin = 26;
const int echoPin = 27;
// defines variables
long duration; int distance;

void LDR_read(){
  LDR_value=analogRead(A0_LDR);
  float vout = LDR_value * ADC_value+0.000001;
  lux = (2500/vout - 500)/10;
  Serial.print(",");
  Serial.print(lux);
  Serial.print(",");
}

void Ultrasonic_read(){
    // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance= duration*0.034/2;
  // Prints the distance on the Serial Monitor
  Serial.print(distance);
  Serial.print(",");
}

void BH1750_read(){
   float lux1 = lightmeter.readLightLevel();
   Serial.print(lux1);
   Serial.println(",");
}

void setup(){
   Serial.begin(9600);
   Wire.begin();
   lightmeter.begin();
   pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
   pinMode(echoPin, INPUT); // Sets the echoPin as an Input
   pinMode(A0_LDR,INPUT);    //make analog pin A0 as input
}

void loop(){
  LDR_read();
  Ultrasonic_read();
  BH1750_read();
  delay(1000);
}
