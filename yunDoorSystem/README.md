# Door Opener

The system is composed by:
* Arduino Yun,
* NFC shield PN532,
* Crystal Liquid Display Hitachi HD44780,
* Relay.

The labchat server contains a database, where all the associates are registered and at least one nfc card is associated to them.
When the nfc card is detected by PN532, the ATmega32U4 decodes the id card and calls the python script with yun process library, passing the id card as command line argument.
The python script sends the POST request to the server. The server responds according to the assigned time slots to each associate. The response is fetched by the python script, which through process library, tells the atmega True or False and some other useful info.
The Arduino finally opens or keeps closed the door, and shows part of the server response through the lcd display.

## Getting Started

Note that this system needs a labchat server up and running, onto which it relies.
The python script must be put onto the microsd card, which must be loaded into the yun; while the sketch needs to be loaded through arduino IDE.
Check that the path and name of the python script match the one at line 115 in the arduino sketch.
The PN532 and Arduino YUN communicates through I2C, thus prepare your hw accordingly as described in https://learn.adafruit.com/adafruit-pn532-rfid-nfc/shield-wiring.
Please check to match the PN_532 IRQ pin in the sketch as the one wired on the shield.

### Prerequisites

Apart from the hw already listed you will need:

  Arduino IDE with following libraries:
  * 	Adafruit_PN532.h
  * 	Process.h
  * 	LiquidCrystal.h

Those libraries can be easily installed with the library manager in arduino IDE.

On the Yun you'll need to install, for proper working of the python script, the following python packages:
* urllib,
* httplib,
* json

 which can be done following http://playground.arduino.cc/Hardware/Yun#installing_python_module.

### Installing

Once the IDE is ready and Python modules installed and everything is wired, it's an easy deal to load the write the python script onto the microsd and insert it inside the yun. You can after flash the yun with the arduino sketch.

## Running the tests

If the labchat server is up and running, you can insert user profiles, associate to them some cards and time slots, and start testing the system.
