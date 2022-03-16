#include <Wire.h>;

// some variables for later use
String positions = "";
int carddir = 0;
int destination;
int rnat = 0;
int storyHeight = 69;
int throwoff = 42;

void setup() {
  Wire.begin(0x02); //start receiving data from Pi
  Wire.onReceive(received);
  pinMode(2, OUTPUT); //set all motor control pins 
  pinMode(3, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
}

// with destination figured out
void go(){
  if (rnat != destination){ //if dropper isn't already there
    digitalWrite(5, rnat > destination); //set the direction depending on which way the destination is from where we are now
    delay(42);
    for (byte i; i < storyHeight*abs(rnat-destination); i++){ //each loop is a step
      digitalWrite(2, HIGH);
      delayMicroseconds(420);
      digitalWrite(2, LOW);
      delayMicroseconds(420);
    }
    rnat = destination; //save location for later
  }
  digitalWrite(6, carddir); // set direction of carddrop
  for (byte i; i < throwoff; i++){ //throw the card off
    digitalWrite(3, HIGH);
    delayMicroseconds(420);
    digitalWrite(3, LOW);
    delayMicroseconds(420);
  }
}

// triggered when Pi sends position
void received(int bytes){
  while (Wire.available()){ //read all the data
    positions += char(Wire.read());
  }
  carddir = int(positions[0]); //split data to parts
  destination = int(positions[1]);
  if (positions.length() > 2){
    destination = int(positions[1] + positions[2]);
  }
  go();
}

void loop() {
}
