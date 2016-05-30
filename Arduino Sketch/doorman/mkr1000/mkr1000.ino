// Include libraries
#include <ArduinoJson.h>
#include <WiFi101.h>
#include <TelegramBot.h>
#include <Adafruit_NeoPixel.h>

// Defining Pins
#define FABLAB_DOOR (2)
#define EXT_DOOR (3)
// #define IRQ_DOORBELL1 (4)
// #define IRQ_DOORBELL2 (5)
// #define IRQ_DOORBELL3 (6)
// #define IRQ_DOORBELL4 (7)
#define LED_DOOR (8)
#define LED_WIFIOFF (9)
#define LED_ERROR (10)

// Defining Constant

#define SSID "FablabTorinoHome"
#define PASSWORD "Fablab.Torino!!"
#define PAGE "/labAdmin/labAdmin/opendoorbynfc/"
#define SERVER "192.168.1.103"
#define BOTTOKEN "201631714:AAHAYNyvBbmFtt0uhakPHeBA2C9WkUeyPiw" // Telegram Bot Token
#define BOTNAME "FablabTurinDoorBot" // Telegram Bot Name
#define BOTUSERNAME "fablabturindoorbot" // Telegram Bot Username
#define N_VALID_CHAT 1 // Number of valid chat for telegram bot
#define CHECKSYSTEM_DELAY 86400000 // Delay for checking the system in millis
#define REPEATREAD 5000 // Timeout for avoiding that arduino processes the same nfc code in millis (avoid multiple read)
#define PN532_TIMEOUT 10000 // Timeout for reading the nfc code in millis
#define N_NEO_PIXELS 4
#define NEO_GREEN 0
#define NEO_YELLOW 1
#define NEO_BLUE 2
#define NEO_RED 3

// Defining Errors Code
#define E_NFC_NOT_VALID 101
#define E_SAME_NFC_CODE 102
#define E_DOOR_NOT_OPENED 103
#define E_WIFI_NOT_CONNECTED 104
#define E_SERVER_NOT_CONNECTED 105
#define E_NFC_READER_NOT_PN532 106
#define E_BAD_NFC_CARD 107
#define E_NO_RESPONSE 108
#define E_JSON_OBJ_NOT_CREATED 109
#define E_BAD_DOOR_CODE 110
#define E_BAD_CHAT 111
#define E_GENERIC_ERROR 112
#define E_TELEGRAM_NO_REQUEST 113
#define E_TELEGRAM_COMMAND_NOT_FOUND 114

// Defining Internal Leds Code (LEDS Function)
#define LED_WIFI_ERROR 201
#define LED_WIFI_CONNECTING 202
#define LED_WIFI_CONNECTED 203
#define LED_SERVER_ERROR 204
#define LED_BAD_CHAT 205
#define LED_GENERIC_ERROR 206
#define LED_NFC_READER_ERROR 207
#define LED_READY 208

// Defining External Leds Code (NEOPIXELS Function)
#define NEO_OPEN 301
#define NEO_NOT_OPEN 302
#define NEO_SAME_NFC_CARD 303
#define NEO_NFC_ERROR 304
#define NEO_WAITING 305
#define NEO_SERVER_ERROR 306
#define NEO_GENERIC_ERROR 307
#define NEO_FINISH 308
#define NEO_TELEGRAM_REQUEST 309


#define DEBUG_CHAT 78310423


// Initializing objects, variables an other stuff
StaticJsonBuffer<400> jsonBuffer; // Define JSON Parser Buffer
WiFiSSLClient client; // Define WiFi Object
int status = WL_IDLE_STATUS; // Define WiFi Connection status
uint32_t lastNfc = 0; // Define the last NFC read
long lastRead = 0; // Define when the last NFC was read
long lastCheck = 0; // Define when the last check
bool checkSystemNow = true; // Define if the system needs checking
const int VALID_CHAT_ID[N_VALID_CHAT] = {/* Alessandro ID */ 78310423};//, /* CasaJasmina Chat ID */ 0, /* Officine Arduino Chat ID */ 0, /* Altra Chat ID */ 0, /* Altra Chat ID */ 0, /* Altra Chat ID (Apri Sempre) */ -127408294, /* Stefano Paradiso */ 60612128}; // Define chats that can send commands (0 mean no chat)
bool needOpen[N_VALID_CHAT] = {false}; // Define Requests From Doorbell
bool alwaysOpen[N_VALID_CHAT] = {false}; // Define who can always open the door
bool openFablab[N_VALID_CHAT] = {false}; // Define who can open FabLab Door
TelegramBot bot(BOTTOKEN, BOTNAME, BOTUSERNAME, client); // Define Telegram Bot
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(N_NEO_PIXELS, LED_DOOR, NEO_GRB + NEO_KHZ800); // Define Neopixels Strip

// Functions:

// String contains another string (case insensitive)
bool stringContainIgnoreCase(String str1, String str2) {
  str1.toLowerCase();
  str2.toLowerCase();
  return str1.indexOf(str2) >= 0;
}

// Print Error On Serial Monitor (Only Debug Mode)
void error(int code) {

  switch (code) {
    case E_NFC_NOT_VALID:
      Serial.println("NFC Code Not Valid!\n");
      break;
    case E_DOOR_NOT_OPENED:
      Serial.println("Access Denied!\n");
      break;
    case E_WIFI_NOT_CONNECTED:
      Serial.println("Device Not Connected To Wifi\n");
      break;
    case E_SERVER_NOT_CONNECTED:
      Serial.println("Server Not Connected\n");
      break;
    case E_NFC_READER_NOT_PN532:
      Serial.println("The NFC Card Reader isn't a PN532 Module\n");
      break;
    case E_BAD_NFC_CARD:
      Serial.println("The NFC Card isn't a MIFARE ISO14443A\n");
      break;
    case E_NO_RESPONSE:
      Serial.println("Response Not Received\n");
      break;
    case E_JSON_OBJ_NOT_CREATED:
      Serial.println("Json Object Not Created\n");
      break;
    case E_BAD_DOOR_CODE:
      Serial.println("Door Code Not Valid\n");
      break;
    case E_BAD_CHAT:
      Serial.println("Chat ID Not Valid\n");
      break;
    case E_GENERIC_ERROR:
      Serial.println("Generic Error\n");
      break;
    case E_TELEGRAM_NO_REQUEST:
      Serial.println("Unable to open the door: No request pending\n");
      break;
    case E_TELEGRAM_COMMAND_NOT_FOUND:
      Serial.println("Command Not Found\n");
      break;
  }
}

// Power On Internal Leds
void leds(int code) {
  switch (code) {
    case LED_WIFI_ERROR:
      for (int i = 0 ; i < 3; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(1000);
        digitalWrite(LED_ERROR, LOW);
        delay(1000);
      }
      break;
    case LED_WIFI_CONNECTING:
      digitalWrite(LED_WIFIOFF, HIGH);
      break;
    case LED_WIFI_CONNECTED:
      digitalWrite(LED_WIFIOFF, LOW);
      break;
    case LED_SERVER_ERROR:
      for (int i = 0 ; i < 3; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(1000);
        digitalWrite(LED_ERROR, LOW);
        delay(1000);
      }
      break;
    case LED_BAD_CHAT:
      for (int i = 0 ; i < 3; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(1000);
        digitalWrite(LED_ERROR, LOW);
        delay(1000);
      }
      break;
    case LED_NFC_READER_ERROR:
      for (int i = 0 ; i < 10; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(100);
        digitalWrite(LED_ERROR, LOW);
        delay(100);
      }
      break;
    case LED_GENERIC_ERROR:
      for (int i = 0 ; i < 3; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(1000);
        digitalWrite(LED_ERROR, LOW);
        delay(1000);
      }
      break;
    case LED_READY:
      for (int i = 0 ; i < 3; i++) {
        digitalWrite(LED_ERROR, HIGH);
        delay(250);
        digitalWrite(LED_WIFIOFF, HIGH);
        delay(250);
        digitalWrite(LED_ERROR, LOW);
        delay(500);
        digitalWrite(LED_WIFIOFF, LOW);
        delay(500);
      }
      break;
  }
}

// Power On External Leds (Neopixels)
// Not connected
void neopixels(int code) {
  switch (code) {
    case NEO_OPEN: // Green led
      pixels.setPixelColor(NEO_GREEN, pixels.Color(0, 255, 0)); // Moderately bright green color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_NOT_OPEN: // Red Led
      pixels.setPixelColor(NEO_RED, pixels.Color(255, 0, 0)); // Moderately bright red color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_WAITING: // Yellow Led
      pixels.setPixelColor(NEO_YELLOW, pixels.Color(255, 255, 0)); // Moderately bright yellow color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_SERVER_ERROR: // Red Led
      pixels.setPixelColor(NEO_RED, pixels.Color(255, 0, 0)); // Moderately bright red color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_NFC_ERROR: // Red Led
      pixels.setPixelColor(NEO_RED, pixels.Color(0, 0, 200)); // Moderately bright red color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_GENERIC_ERROR: // Red Led
      pixels.setPixelColor(NEO_RED, pixels.Color(255, 0, 0)); // Moderately bright red color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_TELEGRAM_REQUEST: // Red Led
      pixels.setPixelColor(NEO_BLUE, pixels.Color(0, 0, 255)); // Moderately bright blue color.
      pixels.setPixelColor(NEO_YELLOW, pixels.Color(255, 255, 0)); // Moderately bright yellow color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
    case NEO_FINISH: // Power Off All
      pixels.setPixelColor(NEO_GREEN, pixels.Color(0, 0, 0));
      pixels.setPixelColor(NEO_YELLOW, pixels.Color(0, 0, 0));
      pixels.setPixelColor(NEO_BLUE, pixels.Color(0, 0, 0));
      pixels.setPixelColor(NEO_RED, pixels.Color(0, 0, 0));
      pixels.show(); // This sends the updated pixel color to the hardware.
      break;
  }
}

// Open the selected Door
void openDoor(int code) {
  switch (code) {
    case EXT_DOOR:
      digitalWrite(EXT_DOOR, HIGH);
      delay(150);
      digitalWrite(EXT_DOOR, LOW);
      delay(25);
      break;
    case FABLAB_DOOR:
      digitalWrite(FABLAB_DOOR, HIGH);
      delay(3000);
      digitalWrite(FABLAB_DOOR, LOW);
      delay(250);
      break;
    default:
      error(E_BAD_DOOR_CODE);
      break;
  }
}

// Send POST to server
bool postData(char *data) {
  char postBuffer[1024] = {'\0'};
  if (client.connected()) {
    sprintf(postBuffer, "POST %s HTTP/1.1\nHost: %s\r\nUser-Agent: Arduino/1.0\r\nConnection: close\r\nContent-Type: application/json;\nContent-Length: %d\r\n\r\n%s\r\n", PAGE, SERVER, strlen(data), data);
    client.print(postBuffer);
    Serial.println("Sent Packet:");
    Serial.println(postBuffer);
    Serial.println();
  } else {
    error(E_SERVER_NOT_CONNECTED);
    leds(LED_SERVER_ERROR);
    neopixels(NEO_SERVER_ERROR);
    return false;
  }

  return true;
}

// Get Response from server
String responseData() {
  String response = "";
  char c;
  if (client.connected()) {
    while (client.connected())
      while (client.available()) {
        c = client.read();
        response.concat(c);
      }
    Serial.println("Response Packet:");
    Serial.println(response);
    Serial.println();
  } else {
    error(E_SERVER_NOT_CONNECTED);
    leds(LED_SERVER_ERROR);
    neopixels(NEO_SERVER_ERROR);
  }

  return response;
}

// Routine for doorbell button 1
// Not Used
void doorbell1() {
  bot.sendMessage(VALID_CHAT_ID[0], "Open The Door Please");
  needOpen[0] = true;
}

// Routine for doorbell button 2
// Not Used
void doorbell2() {
  bot.sendMessage(VALID_CHAT_ID[1], "Open The Door Please");
  needOpen[1] = true;
}

// Interrupt Routine for doorbell buttons
// Not Used
void doorbells() {
  detachIRQ();
  bool button1Pressed = true, button2Pressed = true;
  bool button1LastStatus = false, button2LastStatus = false;

  while (button1Pressed or button2Pressed) {
    button1Pressed = (digitalRead(IRQ_DOORBELL1) == HIGH);
    button2Pressed = (digitalRead(IRQ_DOORBELL2) == HIGH);

    if (button1Pressed && ! button1LastStatus)
      doorbell1();

    if (button2Pressed && ! button2LastStatus)
      doorbell2();
    button1LastStatus = button1Pressed;
    button2LastStatus = button2Pressed;
  }
  attachIRQ();
}

// Detach any doorbell button interrupt
// Not used
void detachIRQ() {
  detachInterrupt(IRQ_DOORBELL1);
  detachInterrupt(IRQ_DOORBELL2);
}

// Attach any doorbell button interrupt
// Not Used
void attachIRQ() {
  attachInterrupt(IRQ_DOORBELL1, doorbells, LOW);
  attachInterrupt(IRQ_DOORBELL2, doorbells, LOW);
}

// Not Used
void setupIRQ() {
  pinMode(IRQ_DOORBELL1, INPUT_PULLUP);
  pinMode(IRQ_DOORBELL2, INPUT_PULLUP);
  // attachIRQ();
}

// Function that check the system status
void checkSystemFunction() {
  int i = 0;
  uint32_t versiondata = 0;
  if (! checkSystemNow and millis() - lastCheck < CHECKSYSTEM_DELAY) {
    Serial.println("Check up not needed!!\n\n");
    return;
  }
  // detachIRQ();
  Serial.println("Check Wireless Connection...\n");
  leds(LED_WIFI_CONNECTING);
  status = WiFi.begin(SSID, PASSWORD);
  i = 0;
  while (status != WL_CONNECTED) {
    delay(2500);
    i++;
    if (i >= 3) {
      error(E_WIFI_NOT_CONNECTED);
      while (i > 0) {
        i--;
        leds(LED_WIFI_ERROR);
        neopixels(NEO_GENERIC_ERROR);
        delay(100);
      }
    } else {
      i++;
    }
    status = WiFi.begin(SSID, PASSWORD);
  }
  Serial.println("Arduino Connected to network...");
  leds(LED_WIFI_CONNECTED);
  delay(100);
  i = 0;
  Serial.println("Check Connection to server...");
  client.connect(SERVER, 443);
  while (!client.connected()) {
    Serial.println("Check Connection to server again...");
    delay(2500);
    client.connect(SERVER, 443);
    if (i >= 3) {
      error(E_SERVER_NOT_CONNECTED);
      while (i > 0) {
        i--;
        leds(LED_SERVER_ERROR);
        neopixels(NEO_SERVER_ERROR);
        delay(1000);
      }
    } else {
      i++;
    }
  }
  client.stop();
  Serial.println("Server Connected...");
  // attachIRQ();
  checkSystemNow = false;
  lastCheck = millis();
  neopixels(NEO_FINISH);
}

void nfcFunction() {
  long now = millis();
  uint32_t cardId = 0;
  bool dataRead = false;

  // TIMEOUT
  while (millis() - now < PN532_TIMEOUT) {
    if (Serial1.available()) {
      dataRead = true;
      delay(100);
      while (Serial1.available()) {
        char c = Serial1.read();
        if (c == '\n' or c == '\0' or c == '\r') {
          break;
        } else if (c < '0' or c > '9') {
          Serial.print("\nError: ascii code "); Serial.println((int)c);
          dataRead = false;
          break;
        } else {
          cardId *= 10;
          cardId += c - '0';
        }
      }
      if (dataRead && cardId > 0) {
        // Don't repeat the function if the same nfc tag is just used
        if (lastNfc == cardId && millis() - lastRead < REPEATREAD) {
          break;
        }

        if (! client.connect(SERVER, 443)) {
          error(E_SERVER_NOT_CONNECTED);
          neopixels(NEO_SERVER_ERROR);
          checkSystemNow = true;
          return;
        }
        lastRead = millis();
        lastNfc = cardId;

        char data[255];
        String response = "", body = "";
        sprintf(data, "{\"nfcId\": %u}", cardId);
        Serial.println(data);
        postData(data);
        delay(100);
        response = responseData();
        client.stop();
        if (response.length() == 0) {
          error(E_NO_RESPONSE);
          neopixels(NEO_SERVER_ERROR);
          checkSystemNow = true;
          return;
        }
        Serial.println("Response:");
        Serial.println(response);
        Serial.println();

        if (!response.startsWith("HTTP/1.1 201 Created")) {
          error(E_NFC_NOT_VALID);
          neopixels(NEO_NFC_ERROR);
          // attachIRQ();
          return;
        }

        body = response.substring(response.indexOf('{'), response.indexOf('}') + 1);
        Serial.println("Body Of response:");
        Serial.println(body);
        Serial.println();
        jsonBuffer = StaticJsonBuffer<400>();
        JsonObject& root = jsonBuffer.parseObject(body);
        if (! root.success()) {
          error(E_JSON_OBJ_NOT_CREATED);
          neopixels(NEO_GENERIC_ERROR);
          leds(LED_GENERIC_ERROR);
        }
        if (root["open"]) {
          Serial.println("You can enter!");
          openDoor(EXT_DOOR);
          String type = root["type"];
          if (stringContainIgnoreCase(type, "fablab")) {
            delay(5000);
            openDoor(FABLAB_DOOR);
            Serial.println("Open Fablab Door!!\n\n");
          }
          neopixels(NEO_OPEN);
        } else {
          Serial.println("You can\'t enter now!");
          neopixels(NEO_NOT_OPEN);
        }
        neopixels(NEO_FINISH);
        // attachIRQ();
      }
      break;
    }
  }
}

// Function that manage telegram Bot
// Not Used
void telegramFunction() {
  message m;
  int i;

  m = bot.getUpdates();
  Serial.print("CHAT ID: "); Serial.println(m.chat_id);
  Serial.print("LAST UPDATE ID: "); Serial.println(bot.getLastID());
  if (m.chat_id == 0) {
    Serial.println("No Message For Telegram Bot");
    return;
  }
  // detachIRQ();
  i = 0;
  while (i < N_VALID_CHAT && m.chat_id != VALID_CHAT_ID[i])
    i++;
  if (i >= N_VALID_CHAT) {
    error(E_BAD_CHAT);
    bot.sendMessage(m.chat_id, "You haven\'t permission to use this bot");
    // attachIRQ();
    return;
  }

  if (! m.text.equalsIgnoreCase("/open")) {
    error(E_TELEGRAM_COMMAND_NOT_FOUND);
    bot.sendMessage(m.chat_id, "Command Not Found");
    // attachIRQ();
    return;
  }

  if (!alwaysOpen[i] and !needOpen[i]) {
    error(E_TELEGRAM_NO_REQUEST);
    bot.sendMessage(m.chat_id, "Unable to open the door now... no request pending");
    // attachIRQ();
    return;
  }
  needOpen[i] = false;
  Serial.println("Open Door");
  openDoor(EXT_DOOR);
  if (openFablab[i]) {
    delay(5000);
    openDoor(FABLAB_DOOR);
    bot.sendMessage(m.chat_id, "Both Doors are open");
  } else {
    bot.sendMessage(m.chat_id, "External Door is open");
  }
  neopixels(NEO_OPEN);
  // attachIRQ();
}

void setup() {

  // put your setup code here, to run once:
  digitalWrite(FABLAB_DOOR, LOW);
  digitalWrite(EXT_DOOR, LOW);
  pinMode(FABLAB_DOOR, OUTPUT);
  pinMode(EXT_DOOR, OUTPUT);

  pinMode(LED_WIFIOFF, OUTPUT); digitalWrite(LED_WIFIOFF, LOW);
  pinMode(LED_ERROR, OUTPUT); digitalWrite(LED_ERROR, LOW);


  Serial.begin(115200);
  Serial1.begin(9600);
  delay(1000);
  Serial.println("Start");

  // Not used
  // openFablab[0] = true;
  // alwaysOpen[0] = true;
  // pixels.begin();
  // setupIRQ();

  // First Check = Start the system
  checkSystemNow = true;
  checkSystemFunction();
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("\n # # # # # # # # # # # # # #\nRun Check System Routine...\n");
  checkSystemFunction();
  if (checkSystemNow) return;

  Serial.println("\n # # # # # # # # # # # # # #\nRun NFC Routine...\n");
  nfcFunction();
  if (checkSystemNow) return;

  // Serial.println("\n # # # # # # # # # # # # # #\nRun Telegram Bot Routine...\n");
  // telegramFunction();
  // if (checkSystemNow) return;
}
