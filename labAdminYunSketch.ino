#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <string.h>
#include <Bridge.h>
#include <LiquidCrystal.h>
#include <Process.h>


// If using the breakout or shield with I2C, define just the pins connected
// to the IRQ and reset lines.  Use the values below (2, 3) for the shield!
//when using with yun it is suggested you cut the line between IRQ and pin 2 
//wire IRQ to a pin 4 or Higher i wired to pin 6
//for more details https://learn.adafruit.com/adafruit-pn532-rfid-nfc/shield-wiring
#define PN532_IRQ   (6)
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

//Liquid Crystal pins
LiquidCrystal lcd(10, 9, 8, 7, 5, 4);
int relay=12;


void setup(void) {
  //LCD with 16 columns times 2 rows 
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
  //initialize nfc reader
  nfc.begin();
  //init relay pin, just to be sure, let's put it open
  pinMode(relay,OUTPUT);
  digitalWrite(relay,HIGH);
  // debug stuff from nfc reader
  #ifdef DEBUG
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    lcd.clear();
    lcd.print("Check NFC Reader");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
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

  uint8_t success,uidLength;
  uint8_t uid[] = { 0, 0, 0, 0};  // Buffer to store the returned UID
  String suid,r1,r2;  
  int r=0,x=0;
  long int sum=0;
  int current_time=0,last_time=0,len;
  //home screen
  lcd.clear();
  lcd.print("Officine");
  lcd.setCursor(0,1);
  lcd.print("Arduino"); 

  //the reader will be listening
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
  
  last_time=current_time;
  //if something was found by nfc reader
  if (success) {
    //display something was found
    //#ifdef DEBUG
    lcd.clear();
    lcd.print("Rilevata Tessera");
    //#endif
    //translate byte of uid in integer number 
    //eg: 0xAA is one byte 2^8=256 since they are concatenated the value of the first byte
    //from right will be 256 the second will have value 256^2 and so on
    for(x=0;x<4;x++){
      sum=sum+uid[x]*pow(256,3-x);
      }
      #ifdef DEBUG
        Serial.println(sum);
        lcd.print(String("uid=")+String(sum));
        delay(2000);
      #endif
      //build command to run in order to send POST request
      suid=String("python -O ~/labAdminYunPythonScript.py "+String(sum));  
      #ifdef DEBUG
        suid=String("python -O ~/labAdminYunPythonScript.py "+String(sum));
        Serial.println(suid);
      #endif
      //send command
      query.runShellCommand(suid);
      //initialize some var
      r1="";
      r2="";
      r=0;
      x=0;
      #ifdef DEBUG
        Serial.println(query.available());
      #endif
      //read response of linino
      while(query.available()>0){
        char c = query.read();
        //Double line response, check example.py for more infos
        //1st line can_open = True or False
        //if False 2nd line = Error Information retrieved from HTTPError and URLError python lib
        //if True 2nd line = Name and Surname of the User
        if (isAlpha(c)==0){r++;}
        if (r<1){r1+=String(c);}
        else{r2+=String(c);} 
      }
      r2.remove(0,1);
      #ifdef DEBUG
        Serial.println(r1);
        Serial.println(r2);
        Serial.println(r1.equals("False")!=0);
      #endif
      
      if (r1.equals("True")!=0){
          #ifdef DEBUG
            Serial.print("Accesso Consentito");
            Serial.println(r2);
          #endif
          lcd.clear();
          lcd.print("Benvenuto");
          lcd.setCursor(0,1);
          r2.remove(0,5);
          lcd.print(r2);
          apriPorta(relay,PULSE_WITDH);
          delay(1000);         
        }
        else{
          lcd.clear();
          lcd.print("Accesso Negato");
          lcd.setCursor(0,1);
          lcd.print(r2);
          len=r2.length();
          if (len<=16){delay(1000);}
          else{
            r2.remove(len-1,1);
            len--;
            x=0;
            while (x<len-16){
              current_time=millis();
              if (current_time-last_time>150){
                lcd.scrollDisplayLeft();
                x++;
                last_time=millis();
                }
              }
              x=0;
              while (x<len-16){
              current_time=millis();
              if (current_time-last_time>150){
                lcd.scrollDisplayRight();
                x++;
                last_time=millis();
                }
            }
        delay(1000);
          }//end of resplen>16
    }//end of accesso negato
  }//end of if success
}//end of loop

void apriPorta(int porta,int del){
          digitalWrite(porta,LOW);
          delay(del);
          digitalWrite(porta,HIGH);
          
}
