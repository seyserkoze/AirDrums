/* Teensy test code
 *  Sandbox to test connections and serial output
 */

// constants won't change. Used here to set pin numbers:
  // Pin 13: Arduino has an LED connected on pin 13
  // Pin 11: Teensy 2.0 has the LED on pin 11
  // Pin  6: Teensy++ 2.0 has the LED on pin 6
  // Pin 13: Teensy 3.0 has the LED on pin 13

const int ledPin =  11;      // LED of Teensy 2.0

const int  serialBaudRate = 9600 ; 
// Variables will change:
int ledState = LOW;             // ledState used to set the LED

void setup() {
  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH) ; // turn on LED
  Serial.begin(serialBaudRate) ; // turn on usb serial output
  Serial.println("Hello From Teensy") ;
}

void loop()
{
  // here is where you'd put code that needs to be running all the time.
} 

