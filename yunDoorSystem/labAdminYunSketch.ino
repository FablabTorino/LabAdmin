#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <string.h>
//#include <Bridge.h>
#include <LiquidCrystal.h>
#include <Process.h>
// If using the breakout or shield with I2C, define just the pins connected
// to the IRQ and reset lines.  Use the values below (2, 3) for the shield!
#define PN532_IRQ   (4)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield

//#define DEBUG
//#define DEBUG2
#define PULSE_WITDH 1000
// Or use this line for a breakout or shield with an I2C connection:
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

#if defined(ARDUINO_ARCH_SAMD)
// for Zero, output on USB Serial console, remove line below if using programming port to program the Zero!
// also change #define in Adafruit_PN532.cpp library file
#define Serial SerialUSB
#endif
LiquidCrystal lcd(10, 12, 8, 7, 5, 6);
int relay = 9;
void setup(void) {
  lcd.begin(16, 2);
#ifndef ESP8266
#ifdef DEBUG
  while (!Serial); // for Leonardo/Micro/Zero
#endif
#endif
#ifdef DEBUG
  Serial.begin(115200);
  Serial.println("Hello!");
#endif
  nfc.begin();
  pinMode(relay, OUTPUT);

#ifdef DEBUG
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata >> 24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata >> 16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata >> 8) & 0xFF, DEC);

  Serial.println("configure board to read RFID tags");
#endif
  nfc.SAMConfig();

#ifdef DEBUG
  Serial.println("Initializing Bridge ...");
  lcd.print("Initializing");

#endif
  Bridge.begin();
#ifdef DEBUG
  Serial.println("READY");
#endif

}


void loop(void) {

  Process query;

  uint8_t success, uidLength;
  uint8_t uid[] = { 0, 0, 0, 0};  // Buffer to store the returned UID
  String suid, r1, r2;
  int r = 0, x = 0;
  uint32_t cardId = 0;
  int current_time = 0, last_time = 0, len;
  //home screen
  lcd.clear();
  lcd.print("Officine");
  lcd.setCursor(0, 1);
  lcd.print("Arduino");

  //the reader will be listening
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  last_time = current_time;
  //if something was found by nfc reader
  if (success && uidLength == 4) {
    //display something was found
    //#ifdef DEBUG
    lcd.clear();
    lcd.print("Rilevata Tessera");
    //#endif
    //translate byte of uid in integer number
    //eg: 0xAA is one byte 2^8=256 since they are concatenated the value of the first byte
    //from right will be 256 the second will have value 256^2 and so on


    cardId = uid[0];
    cardId <<= 8;
    cardId |= uid[1];
    cardId <<= 8;
    cardId |= uid[2];
    cardId <<= 8;
    cardId |= uid[3];
#ifdef DEBUG

    Serial.println(cardId);

    lcd.print(String("uid=") + String(cardId));
    delay(2000);
#endif
    //build command to run in order to send POST request
    suid = String("python -O ~/openDoorByNFCLinino.py " + String(cardId));
#ifdef DEBUG
    suid = String("python -O ~/openDoorByNFCLinino.py " + String(cardId));
    Serial.println(suid);
#endif
    //send command
    query.runShellCommand(suid);
    //initialize some var
    r1 = "";
    r2 = "";
    r = 0;
    x = 0;
#ifdef DEBUG
    Serial.println(query.available());
#endif
    //read response of linino
    while (query.available() > 0) {
      char c = query.read();
      //Double line response, check example.py for more infos
      //1st line can_open = True or False
      //if False 2nd line = Error Information retrieved from HTTPError and URLError python lib
      //if True 2nd line = Name and Surname of the User
      if (isAlpha(c) == 0) {
        r++;
      }
      if (r < 1) {
        r1 += String(c);
      }
      else {
        r2 += String(c);
      }
    }
    r2.remove(0, 1);
#ifdef DEBUG
    Serial.println(r1);
    Serial.println(r2);
    Serial.println(r1.equals("False") != 0);
#endif

    if (r1.equals("True") != 0) {
#ifdef DEBUG
      Serial.print("Accesso Consentito");
      Serial.println(r2);
#endif
      lcd.clear();
      lcd.print("Benvenuto");
      lcd.setCursor(0, 1);
      r2.remove(0, 5);
      lcd.print(r2);
      apriPorta(relay, PULSE_WITDH);
      delay(1000);
    }
    else {
#ifdef DEBUG
      Serial.print("Accesso Negato");
      Serial.println(r2);
#endif
      lcd.clear();
      lcd.print("Accesso Negato");
      lcd.setCursor(0, 1);
      lcd.print("Fuori Orario");
      delay(1000);
      len = r2.length();
      r2.remove(len - 1, 1);
      len--;
      if (len > 16) {
        x = 0;
        while (x < len - 16) {
          current_time = millis();
          if (current_time - last_time > 150) {
            lcd.scrollDisplayLeft();
            x++;
            last_time = millis();
          }
        }
        x = 0;
        while (x < len - 16) {
          current_time = millis();
          if (current_time - last_time > 150) {
            lcd.scrollDisplayRight();
            x++;
            last_time = millis();
          }
        }
        delay(1000);
      }//end of resplen>16
    }//end of accesso negato
  }//end of if success
  Serial.println("End of Loop");
}//end of loop

void apriPorta(int porta, int del) {
  digitalWrite(porta, HIGH);
  delay(del);
  digitalWrite(porta, LOW);

}
