#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <Wire.h>
#include <WireKinetis.h>

/* Teensy test code
 *  Sandbox to test connections and serial output
 */

// constants won't change. Used here to set pin numbers:
  // Pin 13: Arduino has an LED connected on pin 13
  // Pin 11: Teensy 2.0 has the LED on pin 11
  // Pin  6: Teensy++ 2.0 has the LED on pin 6
  // Pin 13: Teensy 3.0 has the LED on pin 13

const int ledPin =  11;      // LED of Teensy 2.0
const int sdaPin = 6 ;
const int sclPin = 5 ; 

//IMU fusion variables
const unsigned char imuAddr = 0x28 ; // i2c address
const int imu_id = 55 ; 
Adafruit_BNO055 bno = Adafruit_BNO055(imu_id, imuAddr) ; // id 55
const unsigned int imu_loop_delay = 1000 ; //100 ms

const int  serialBaudRate = 9600 ; 
// Variables will change:
int ledState = LOW;             // ledState used to set the LED



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
 

void setup() {
  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH) ; // turn on LED
  Serial.begin(serialBaudRate) ; // turn on usb serial output
  Serial.println("Hi From Teensy") ;
  //Wire.setSDA(sdaPin) ;
  //Wire.setSCL(sclPin) ; 
  if(!bno.begin()) {
    Serial.println("Could not find BN055") ;
    while(1) ; //hang here
  }
  Serial.print("Starting BnO055 ...\n") ;
  delay(1000);
  displaySensorDetails(); 
  displaySensorStatus() ;
  bno.setExtCrystalUse(true) ;
  
}

void loop()
{
  /* Get a new sensor event */
  sensors_event_t event;
  bno.getEvent(&event);

  /* Display the floating point data 
  Serial.print("X: ");
  Serial.print(event.acceleration.x, 4);
  Serial.print("\tY: ");
  Serial.print(event.acceleration.y, 4);
  Serial.print("\tZ: ");
  Serial.print(event.acceleration.z, 4);
  Serial.println("\n------------------") ;
  */

  imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  Serial.print("lX: ");
  Serial.print(accel.x(), 4);
  Serial.print("\tlY: ");
  Serial.print(accel.y(), 4);
  Serial.print("\tlZ: ");
  Serial.print(accel.z(), 4);
  Serial.println("\n------------------") ;


  /* Optional: Display calibration status */
  //displayCalStatus();

  /* Optional: Display sensor status (debug only) */
  //displaySensorStatus();

  /* New line for the next sample */
  Serial.println("");

  /* Wait the specified delay before requesting nex data */
  delay(imu_loop_delay);
} 

