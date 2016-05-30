#include <Wire.h>
#include <Adafruit_PN532.h>

#define PN532_IRQ   (2)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield
#define REPEATREAD 10000

Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);
uint32_t lastNfc = 0;

void setup(void) {
  Serial.begin(9600);
  delay(500);
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // configure board to read RFID tags
  nfc.SAMConfig();
}

void loop(void) {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
  if (success && uidLength == 4) {
    uint32_t cardId = 0;
    long now = millis();
    cardId = uid[0];
    cardId <<= 8;
    cardId |= uid[1];
    cardId <<= 8;
    cardId |= uid[2];
    cardId <<= 8;
    cardId |= uid[3];
    // Send cardId to MKR1000
    Serial.print(cardId);
    delay(REPEATREAD);
  }
}
