#include <Arduino.h>
#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_UART.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <Wire.h>
#include <WireKinetis.h>

#include "BluefruitConfig.h"

#if SOFTWARE_SERIAL_AVAILABLE
  #include <SoftwareSerial.h>
#endif

#define FACTORYRESET_ENABLE 1
#define MINIMUM_FIRMWARE_VERSION "0.6.6"
#define MODE_LED_BEHAVIOUR "MODE"
#define X 0
#define Y 1
#define Z 2

/*--------------------Globals-------------------------------*/
const char teensyLEDPin = 11 ;
const int packet_len = 27 ; //4 time chars and 1 ,
char packet_buf[packet_len + 1] ;

const unsigned baud_rate = 115200 ;

unsigned long last_time ; 

//BLE variables
const int cts_pin = 14 ;
const int mod_pin = 13 ;
const unsigned ble_baud_rate = 115200 ;
/*hardware serial, which does not need the RTS/CTS pins. Uncomment this line */
Adafruit_BluefruitLE_UART ble(BLUEFRUIT_HWSERIAL_NAME, BLUEFRUIT_UART_MODE_PIN);


//IMU fusion variables
const unsigned char imuAddr = 0x28 ; // i2c address
const int imu_id = 55 ; 
const unsigned int imu_loop_delay = 1000 ; //100 ms
Adafruit_BNO055 bno = Adafruit_BNO055(imu_id, imuAddr) ; // id 55


/*-------------------------Helper Functions--------------------*/
// A small helper
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}

/*
 * Get sensor's basic indentification values
 */
void displaySensorDetails(void)
{
  sensor_t sensor;
  bno.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" xxx");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" xxx");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" xxx");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
} 

/*
 * Get sensor's status
 */
void displaySensorStatus(void)
{
  /* Get the system status values (mostly for debugging purposes) */
  uint8_t system_status, self_test_results, system_error;
  system_status = self_test_results = system_error = 0;
  bno.getSystemStatus(&system_status, &self_test_results, &system_error);

  /* Display the results in the Serial Monitor */
  Serial.println("");
  Serial.print("System Status: 0x");
  Serial.println(system_status, HEX);
  Serial.print("Self Test:     0x");
  Serial.println(self_test_results, HEX);
  Serial.print("System Error:  0x");
  Serial.println(system_error, HEX);
  Serial.println("");
  delay(500);
}


/*
 * Get sensor's calibration values
 */
void displayCalStatus(void)
{
  /* Get the four calibration values (0..3) */
  /* Any sensor data reporting 0 should be ignored, */
  /* 3 means 'fully calibrated" */
  uint8_t system, gyro, accel, mag;
  system = gyro = accel = mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);

  /* The data should be ignored until the system calibration is > 0 */
  Serial.print("\t");
  if (!system)
  {
    Serial.print("! ");
  }

  /* Display the individual values */
  Serial.print("Sys:");
  Serial.print(system, DEC);
  Serial.print(" G:");
  Serial.print(gyro, DEC);
  Serial.print(" A:");
  Serial.print(accel, DEC);
  Serial.print(" M:");
  Serial.print(mag, DEC);
}

void ble_setup() {
  while (!Serial);  // required for Flora & Micro
  delay(500);
  //F stores string in ram
  Serial.println(F("Adafruit Bluefruit Command <-> Data Mode Example"));
  Serial.println(F("------------------------------------------------"));

  /* Initialise the module */
  Serial.print(F("Initialising the Bluefruit LE module: "));

  if ( !ble.begin(VERBOSE_MODE) )
  {
    error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
  }
  Serial.println( F("OK!") );

  if ( FACTORYRESET_ENABLE )
  {
    /* Perform a factory reset to make sure everything is in a known state */
    Serial.println(F("Performing a factory reset: "));
    if ( ! ble.factoryReset() ){
      error(F("Couldn't factory reset"));
    }
  }

  /* Disable command echo from Bluefruit */
  ble.echo(false);

  Serial.println("Requesting Bluefruit info:");
  /* Print Bluefruit information */
  ble.info();

  Serial.println(F("Please use Adafruit Bluefruit LE app to connect in UART mode"));
  Serial.println(F("Then Enter characters to send to Bluefruit"));
  Serial.println();

  ble.verbose(false);  // debug info is a little annoying after this point!

  /* Wait for connection */
  while (! ble.isConnected()) {
      delay(500);
  }

  Serial.println(F("******************************"));

  // LED Activity command is only supported from 0.6.6
  if ( ble.isVersionAtLeast(MINIMUM_FIRMWARE_VERSION) )
  {
    // Change Mode LED Activity
    Serial.println(F("Change LED activity to " MODE_LED_BEHAVIOUR));
    ble.sendCommandCheckOK("AT+HWModeLED=" MODE_LED_BEHAVIOUR);
  }

 
  Serial.println(F("******************************"));
}

char imu_setup() {
  if(!bno.begin()) {
    Serial.println(F("Could not find BNO055")) ; 
    return 0 ; // no sensor found
  }
  Serial.println("Starting BNO055...") ;
  delay(1000) ;
  displaySensorDetails(); 
  displaySensorStatus() ;
  bno.setExtCrystalUse(true) ;
  return 1 ; 
}

imu::Vector<3> get_acceleration() {
  return bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL) ;
}


String serialize_data(unsigned long elapsed_t, imu::Vector<3> &accel) {
  unsigned char width = 6 ;
  char prec = 4 ; 
  char *buf = packet_buf ;
  buf[0] = '[' ; 
  buf = buf + 1  ;
  sprintf(buf, "%4lu", elapsed_t); // put time value at start of buf
  buf[4] = ',' ;
  buf = buf + 5 ; 
  
  for(int i = 0 ; i < 3 ; i++) {
    // enter readings into buf
    if(i == X) {
      dtostrf(accel.x(), width, prec, buf) ;
      buf[width] = ',' ;
      buf = buf + width + 1 ; 
    }
    else if(i == Y) {
      dtostrf(accel.y(), width, prec, buf) ;
      buf[width] = ',' ;
      buf = buf + width + 1 ;
    }
    else {
      dtostrf(accel.z(), width, prec, buf) ;
      buf = buf + width ;
      buf[0] = ']' ;
      buf[1] = 0 ; 
    }
  }
  //Serial.println(packet_buf) ;
  return String(packet_buf) ;
}


char send_data(String data) {
  int len = data.length() ;
  if(len > packet_len) {
    Serial.println("Serialized data too long");
    return 0 ;
  }
  for(int i =0; i < len; i++) {
    packet_buf[i] = data[i] ; 
  }
  packet_buf[len] = 0 ; //null terminator
  ble.print("AT+BLEUARTTX=");
  ble.println(packet_buf) ;
  return 1 ; 
}




/*------------------Main Functions--------------------*/

void setup() {
  Serial.begin(baud_rate) ;
  pinMode(teensyLEDPin, OUTPUT) ;
  digitalWrite(teensyLEDPin, HIGH) ; //turn on status led on teensy
  ble_setup() ;
  while(!imu_setup()) ; //spin until imu is setup
  last_time = millis() ;
}

void loop() {
  imu::Vector<3> sensor_data = get_acceleration() ;
  unsigned long elapsed_time = millis() - last_time ;
  last_time = millis() ; 
  send_data(serialize_data(elapsed_time, sensor_data)) ; 
}



