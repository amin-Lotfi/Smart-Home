const int pinD1 = 13; 
const int pinD2 = 12; 
const int pinD3 = 11; 
const int pinD4 = 10; 
const int pinD5 = 9; 
const int pinD6 = 8; 


char command;

void setup() {
  Serial.begin(9600);
  pinMode(pinD1, OUTPUT); 
  pinMode(pinD2, OUTPUT); 
  pinMode(pinD3, OUTPUT); 
  pinMode(pinD4, OUTPUT); 
  pinMode(pinD5, OUTPUT); 
  pinMode(pinD6, OUTPUT); 

}

void loop() {
  
  if (Serial.available() > 0) {
    command = Serial.read(); 
    
    if (command == 'H') {
      digitalWrite(pinD1, HIGH);
    }
    else if (command == 'L') {
      digitalWrite(pinD1, LOW);
    }


    if (command == '1') {
      digitalWrite(pinD2, HIGH);
    }
    else if (command == '2') {
      digitalWrite(pinD2, LOW);
    }


    if (command == '3') {
      digitalWrite(pinD3, HIGH);
    }
    else if (command == '4') {
      digitalWrite(pinD3, LOW);
    }

    
    if (command == '5') {
      digitalWrite(pinD4, HIGH);
    }
    else if (command == '6') {
      digitalWrite(pinD4, LOW);
    }

    
    if (command == '7') {
      digitalWrite(pinD5, HIGH);
    }
    else if (command == '8') {
      digitalWrite(pinD5, LOW);
    }


    if (command == '9') {
      digitalWrite(pinD6, HIGH);
    }
    else if (command == '0') {
      digitalWrite(pinD6, LOW);
    }
  }
}